"""OpenAPI spec renderer."""

import collections
import functools
import http.client
import json

import docutils.parsers.rst.directives as directives
import m2r
import requests
import sphinx.util.logging as logging

from sphinxcontrib.openapi.renderers import abc
from sphinxcontrib.openapi.schema_utils import example_from_schema


CaseInsensitiveDict = requests.structures.CaseInsensitiveDict


logger = logging.getLogger(__name__)


def indented(generator, indent=3):
    for item in generator:
        if item:
            item = " " * indent + item
        yield item


def _iterinorder(iterable, order_by, key=lambda x: x, case_sensitive=False):
    """Iterate over iterable in a given order."""

    order_by = collections.defaultdict(
        # Assume default priority is `Infinity` which means the lowest one.
        # This value is effectively used if there's no corresponding value in a
        # given 'order_by' array.
        lambda: float("Inf"),
        # Passed 'order_by' may be 'None' which means *do not reorder, use
        # natural order*. In order to avoid special cases in the code, we're
        # simply falling back to an empty 'order_by' array since it effectively
        # means *assume every item in 'iterable' has equal priority*.
        ((value, i) for i, value in enumerate(order_by or [])),
    )
    yield from sorted(
        iterable,
        key=lambda value: order_by[
            key(value) if case_sensitive else key(value).lower()
        ],
    )


def _iterexamples(media_types, example_preference, examples_from_schemas):
    """Iterate over examples and return them according to the caller preference."""

    for content_type in _iterinorder(media_types, example_preference):
        media_type = media_types[content_type]

        # Look for a example in a bunch of possible places. According to
        # OpenAPI v3 spec, `examples` and `example` keys are mutually
        # exclusive, so there's no much difference between their
        # inspection order, while both must take precedence over a
        # schema example.
        if media_type.get("examples", {}):
            for example in media_type["examples"].values():
                if "externalValue" in example:
                    if not example["externalValue"].startswith(("http://", "https://")):
                        logger.warning(
                            "Not supported protocol in 'externalValue': %s",
                            example["externalValue"],
                        )
                        continue

                    try:
                        response = requests.get(example["externalValue"])
                        response.raise_for_status()

                        example["value"] = response.text
                        example.pop("externalValue")
                    except Exception:
                        logger.error(
                            "Cannot retrieve example from: '%s'",
                            example["externalValue"],
                        )
                        continue
                break
            else:
                # If the loop over examples has not been interrupted, we
                # probably didn't find an example to render. In that case,
                # let's try and go next media type.
                continue
        elif media_type.get("example"):
            # Save example from "example" in "examples" compatible format. This
            # allows to treat all returned examples the same way.
            example = {"value": media_type["example"]}
        elif media_type.get("schema", {}).get("example"):
            # Save example from "schema" in "examples" compatible format. This
            # allows to treat all returned examples the same way.
            example = {"value": media_type["schema"]["example"]}
        elif "schema" in media_type and examples_from_schemas:
            # Convert schema to example
            example = {"value": example_from_schema(media_type["schema"])}
            pass
        else:
            continue

        yield content_type, example


class HttpdomainRenderer(abc.RestructuredTextRenderer):
    """Render OpenAPI v3 using `sphinxcontrib-httpdomain` extension."""

    _markup_converters = {"commonmark": m2r.convert, "restructuredtext": lambda x: x}
    _response_examples_for = {"200", "201", "202", "2XX"}
    _request_parameters_order = ["header", "path", "query", "cookie"]

    option_spec = {
        "markup": functools.partial(directives.choice, values=_markup_converters),
        "http-methods-order": lambda s: s.split(),
        "response-examples-for": None,
        "request-parameters-order": None,
        "example-preference": None,
        "request-example-preference": None,
        "response-example-preference": None,
        "generate-examples-from-schemas": directives.flag,
    }

    def __init__(self, state, options):
        super().__init__(state, options)

        self._convert_markup = self._markup_converters[
            options.get("markup", "commonmark")
        ]
        self._http_methods_order = [
            http_method.lower() for http_method in options.get("http-methods-order", [])
        ]
        self._response_examples_for = options.get(
            "response-examples-for", self._response_examples_for
        )
        self._request_parameters_order = [
            parameter_type.lower()
            for parameter_type in options.get(
                "request-parameters-order", self._request_parameters_order
            )
        ]
        self._example_preference = options.get("example-preference")
        self._request_example_preference = options.get(
            "request-example-preference", self._example_preference
        )
        self._response_example_preference = options.get(
            "response-example-preference", self._example_preference
        )
        self._generate_example_from_schema = "generate-examples-from-schemas" in options

    def render_restructuredtext_markup(self, spec):
        """Spec render entry point."""
        yield from self.render_paths(spec.get("paths", {}))

    def render_paths(self, paths):
        """Render OAS paths item."""

        for endpoint, path in paths.items():
            common_parameters = path.pop("parameters", [])

            # OpenAPI's path description may contain objects of different
            # types. Since we're interested in rendering only objects of
            # operation type, let's remove irrelevant one from the definition
            # in order to simplify further code.
            for key in {"summary", "description", "servers"}:
                path.pop(key, None)

            for method in _iterinorder(path, self._http_methods_order):
                operation = path[method]
                operation.setdefault("parameters", [])
                operation_parameters_ids = set(
                    (parameter["name"], parameter["in"])
                    for parameter in operation["parameters"]
                )
                operation["parameters"] = [
                    parameter
                    for parameter in common_parameters
                    if (parameter["name"], parameter["in"])
                    not in operation_parameters_ids
                ] + operation["parameters"]

                yield from self.render_operation(endpoint, method, operation)
                yield ""

    def render_operation(self, endpoint, method, operation):
        """Render OAS operation item."""

        yield f".. http:{method}:: {endpoint}"

        if operation.get("deprecated"):
            yield f"   :deprecated:"
        yield f""

        if operation.get("summary"):
            yield f"   **{operation['summary']}**"
            yield f""

        if operation.get("description"):
            yield from indented(
                self._convert_markup(operation["description"]).strip().splitlines()
            )
            yield f""

        yield from indented(self.render_parameters(operation.get("parameters", [])))
        if "requestBody" in operation:
            yield from indented(
                self.render_request_body(operation["requestBody"], endpoint, method)
            )
        yield from indented(self.render_responses(operation["responses"]))

    def render_parameters(self, parameters):
        """Render OAS operation's parameters."""

        for parameter in _iterinorder(
            parameters, self._request_parameters_order, key=lambda value: value["in"]
        ):
            yield from self.render_parameter(parameter)

    def render_parameter(self, parameter):
        """Render OAS operation's parameter."""

        kinds = CaseInsensitiveDict(
            {"path": "param", "query": "queryparam", "header": "reqheader"}
        )
        markers = []
        schema = parameter.get("schema", {})

        if "content" in parameter:
            # According to OpenAPI v3 spec, 'content' in this case may
            # have one and only one entry. Hence casting its values to
            # list is not expensive and should be acceptable.
            schema = list(parameter["content"].values())[0].get("schema", {})

        if parameter["in"] not in kinds:
            logger.warning(
                "OpenAPI spec contains parameter '%s' (in: '%s') that cannot "
                "be rendererd.",
                parameter["name"],
                parameter["in"],
            )
            return

        if schema.get("type"):
            type_ = schema["type"]
            if schema.get("format"):
                type_ = f"{type_}:{schema['format']}"
            markers.append(type_)

        if parameter.get("required"):
            markers.append("required")

        if parameter.get("deprecated"):
            markers.append("deprecated")

        yield f":{kinds[parameter['in']]} {parameter['name']}:"

        if parameter.get("description"):
            yield from indented(
                self._convert_markup(parameter["description"]).strip().splitlines()
            )

        if markers:
            markers = ", ".join(markers)
            yield f":{kinds[parameter['in']]}type {parameter['name']}: {markers}"

    def render_request_body(self, request_body, endpoint, method):
        """Render OAS operation's requestBody."""

        yield from self.render_request_body_example(request_body, endpoint, method)
        yield ""

    def render_request_body_example(self, request_body, endpoint, method):
        """Render OAS operation's requestBody's example."""

        content_type, example = next(
            _iterexamples(
                request_body["content"],
                self._request_example_preference,
                self._generate_example_from_schema,
            ),
            (None, None),
        )

        if content_type and example:
            example = example["value"]

            if not isinstance(example, str):
                example = json.dumps(example, indent=2)

            yield f".. sourcecode:: http"
            yield f""
            yield f"   {method.upper()} {endpoint} HTTP/1.1"
            yield f"   Content-Type: {content_type}"
            yield f""
            yield from indented(example.splitlines())

    def render_responses(self, responses):
        """Render OAS operation's responses."""

        for status_code, response in responses.items():
            # Due to the way how YAML spec is parsed, status code may be
            # infered as integer. In order to spare some cycles on type
            # guessing going on, let's ensure it's always string at this point.
            yield from self.render_response(str(status_code), response)

    def render_response(self, status_code, response):
        """Render OAS operation's response."""

        yield f":statuscode {status_code}:"
        yield from indented(
            self._convert_markup(response["description"]).strip().splitlines()
        )

        if "content" in response and status_code in self._response_examples_for:
            yield ""
            yield from indented(
                self.render_response_content(response["content"], status_code)
            )

        if "headers" in response:
            yield ""

            for header_name, header_value in response["headers"].items():
                # According to OpenAPI v3 specification, if a response header
                # is defined with the name 'Content-Type', it shall be ignored.
                if header_name.lower() == "content-type":
                    continue

                yield f":resheader {header_name}:"

                if header_value.get("description"):
                    yield from indented(
                        self._convert_markup(header_value["description"])
                        .strip()
                        .splitlines()
                    )

                markers = []
                schema = header_value.get("schema", {})
                if "content" in header_value:
                    # According to OpenAPI v3 spec, 'content' in this case may
                    # have one and only one entry. Hence casting its values to
                    # list is not expensive and should be acceptable.
                    schema = list(header_value["content"].values())[0].get("schema", {})

                if schema.get("type"):
                    type_ = schema["type"]
                    if schema.get("format"):
                        type_ = f"{type_}:{schema['format']}"
                    markers.append(type_)

                if header_value.get("required"):
                    markers.append("required")

                if header_value.get("deprecated"):
                    markers.append("deprecated")

                if markers:
                    markers = ", ".join(markers)
                    yield f":resheadertype {header_name}: {markers}"

    def render_response_content(self, media_type, status_code):
        # OpenAPI 3.0 spec may contain more than one response media type, and
        # each media type may contain more than one example. Rendering all
        # invariants normally is not an option because the result will be hard
        # to read and follow. The best option we can go with at this moment is
        # to render first found example of either response media type. Users
        # should control what to render by putting recommended example first in
        # the list.
        content_type, example = next(
            _iterexamples(
                media_type,
                self._response_example_preference,
                self._generate_example_from_schema,
            ),
            (None, None),
        )

        if content_type and example:
            example = example["value"]

            if not isinstance(example, str):
                example = json.dumps(example, indent=2)

            # According to OpenAPI v3 spec, status code may be a special value
            # - "default". It's not quite clear what to render in this case.
            # One possible option is to avoid rendering status code at all.
            # This option, however, suffers from broken code highlighting
            # because Pygments relies on the snippet to start with HTTP
            # protocol line. That said, probably the best we can do at the
            # moment is to render some generic status.
            if status_code == "default":
                status_code = "000"
                status_text = "Reason-Phrase"
            else:
                # According to OpenAPI v3 spec, status code may define a range
                # of response codes. Since we're talking about rendered example
                # here, we may show either code from range, but for the sake of
                # simplicity let's pick the first one.
                status_code = status_code.replace("XX", "00")
                status_text = http.client.responses.get(int(status_code), "-")

            yield f".. sourcecode:: http"
            yield f""
            yield f"   HTTP/1.1 {status_code} {status_text}"
            yield f"   Content-Type: {content_type}"
            yield f""
            yield from indented(example.splitlines())
