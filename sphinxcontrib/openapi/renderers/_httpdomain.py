"""OpenAPI spec renderer."""

import collections
import collections.abc
import copy
import functools
import http.client
import json
import re
from urllib.parse import urlencode

import deepmerge
import docutils.parsers.rst.directives as directives
import requests
import sphinx.util.logging as logging
import sphinx_mdinclude

from sphinxcontrib.openapi import _lib2to3 as lib2to3, utils
from sphinxcontrib.openapi.renderers import abc
from sphinxcontrib.openapi.schema_utils import NoExampleError, example_from_schema

CaseInsensitiveDict = requests.structures.CaseInsensitiveDict


logger = logging.getLogger(__name__)


def indented(generator, indent=3):
    for item in generator:
        if item:
            item = " " * indent + item
        yield item


def _split_option(value):
    """Parse a whitespace delimited option value into a list of tokens."""

    # An option may be passed with no value at all, in which case docutils
    # hands over 'None' instead of a string. Since every option parsed here
    # takes one or more values, and since an empty one would silently turn
    # 'response-examples-for' into "no examples at all", let's reject it. The
    # 'ValueError' is turned into a directive error by docutils.
    tokens = (value or "").split()
    if not tokens:
        raise ValueError("expected one or more whitespace delimited values")
    return tokens


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
        example = None

        # Look for an example in a bunch of possible places. According to
        # OpenAPI v3 spec, `examples` and `example` keys are mutually
        # exclusive, so there's no much difference between their
        # inspection order, while both must take precedence over a
        # schema example.
        if media_type.get("examples", {}):
            for example in media_type["examples"].values():
                # Keep fetched content and rendering metadata out of the spec.
                example = example.copy()
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
                        example["_serialize_json"] = False
                        example.pop("externalValue")
                    except Exception:
                        logger.error(
                            "Cannot retrieve example from: '%s'",
                            example["externalValue"],
                        )
                        continue
                # Example Objects can contain annotations without a value.
                # An explicitly supplied falsey value is nevertheless valid.
                if "value" not in example:
                    continue
                break
            else:
                example = None

        if example is None:
            if "example" in media_type:
                example = {"value": media_type["example"]}
            elif isinstance(media_type.get("schema"), dict) and (
                "example" in media_type["schema"]
                or media_type["schema"].get("examples")
            ):
                # Schema examples are literal values, unlike media-type examples.
                # Preserve singular-example precedence for legacy specifications.
                schema = media_type["schema"]
                example = {"value": example_from_schema(schema)}
                if "example" not in schema:
                    example["_serialize_json"] = True
            elif "schema" in media_type and examples_from_schemas:
                # A valid OAS 3.1 schema can forbid all values. In that case there
                # is no generated example to render; try another media type.
                try:
                    example = {
                        "value": example_from_schema(media_type["schema"]),
                        "_serialize_json": True,
                    }
                except NoExampleError:
                    continue
            else:
                continue

        schema = media_type.get("schema")
        if isinstance(schema, dict):
            schema_types = schema.get("type", [])
            if isinstance(schema_types, str):
                schema_types = [schema_types]
            if "string" in schema_types:
                # A declared string schema makes these JSON instance values,
                # not legacy preformatted structured payloads. Fetched content
                # retains its explicit verbatim marker.
                example.setdefault("_serialize_json", True)
        yield content_type, example


def _get_markers_from_object(oas_object, schema):
    """Retrieve a bunch of OAS object markers."""

    markers = []
    if isinstance(schema, bool):
        schema = {}

    schema_type = _get_schema_type(schema)
    if schema_type:
        schema_types = schema_type if isinstance(schema_type, list) else [schema_type]
        for schema_type in schema_types:
            if schema_type != "null" and schema.get("format"):
                schema_type = f"{schema_type}:{schema['format']}"
            elif schema_type != "null" and schema.get("enum"):
                schema_type = f"{schema_type}:enum"
            markers.append(schema_type)
    elif schema.get("enum"):
        markers.append("enum")

    if oas_object.get("required"):
        markers.append("required")

    if oas_object.get("deprecated"):
        markers.append("deprecated")

    if schema.get("deprecated"):
        markers.append("deprecated")

    return markers


def _is_json_mimetype(mimetype):
    """Returns 'True' if a given mimetype implies JSON data."""

    mimetype = mimetype.split(";", 1)[0].strip().lower()
    return any(
        [
            mimetype == "application/json",
            mimetype.startswith("application/") and mimetype.endswith("+json"),
        ]
    )


def _format_example(content_type, example):
    """Serialize instance values while preserving legacy preformatted payloads."""

    value = example["value"]
    mimetype = content_type.split(";", 1)[0].strip().lower()
    if mimetype == "application/x-www-form-urlencoded" and isinstance(value, dict):

        def form_value(item):
            if isinstance(item, str):
                return item
            return json.dumps(item, default=str)

        fields = {
            name: (
                [form_value(item) for item in field]
                if isinstance(field, list)
                else form_value(field)
            )
            for name, field in value.items()
        }
        return urlencode(fields, doseq=True)
    # Generated and schema-level plural examples are literal values. Legacy
    # nonempty strings may contain preformatted payloads, but an empty string
    # cannot be preformatted JSON and must be quoted unless fetched verbatim.
    serialize_json = _is_json_mimetype(content_type) and example.get(
        "_serialize_json", value == ""
    )
    if not isinstance(value, str) or serialize_json:
        return json.dumps(value, indent=2, default=str)
    return value


def _is_2xx_status(status_code):
    """Returns 'True' if a given status code is one of successful."""

    return str(status_code).startswith("2")


def _get_schema_type(schema):
    """Retrieve schema type either by reading 'type' or guessing."""

    if isinstance(schema, bool):
        return None

    # There are a lot of OpenAPI specs out there that may lack 'type' property
    # in their schemas. I fount no explanations on what is expected behaviour
    # in this case neither in OpenAPI nor in JSON Schema specifications. Thus
    # let's assume what everyone assumes, and try to guess schema type at least
    # for two most popular types: 'object' and 'array'.
    if "type" not in schema:
        if "properties" in schema:
            schema_type = "object"
        elif "items" in schema:
            schema_type = "array"
        else:
            schema_type = None
    else:
        schema_type = schema["type"]
    return schema_type


def _get_single_schema_type(schema):
    """Choose a concrete type to traverse while retaining all types in markers."""

    schema_type = _get_schema_type(schema)
    if isinstance(schema_type, list):
        return next((t for t in schema_type if t != "null"), "null")
    return schema_type


def _merge_schema_lists(merger, path, base, nxt):
    # allOf is conjunctive: every required property and nested allOf constraint
    # remains applicable. Other lists retain the existing override policy.
    if path and path[-1] == "required":
        return list(dict.fromkeys(base + nxt))
    if path and path[-1] == "allOf":
        return base + nxt
    return nxt


_merge_mappings = deepmerge.Merger(
    [
        (collections.abc.Mapping, deepmerge.strategy.dict.DictStrategies("merge")),
        (list, [_merge_schema_lists]),
    ],
    ["override"],
    ["override"],
).merge


_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def _to_list(val):
    if val is None:
        return None
    if isinstance(val, str):
        return val.split()
    return list(val)


def _flag_or_bool(argument):
    if argument is None:
        return True
    val = str(argument).strip().lower()
    if val in ("true", "yes", "1"):
        return True
    if val in ("false", "no", "0"):
        return False
    raise ValueError(f"Invalid boolean value: {argument}")


def _header(title):
    yield title
    yield "=" * len(title)
    yield ""


class HttpdomainRenderer(abc.RestructuredTextRenderer):
    """Render OpenAPI v3 using `sphinxcontrib-httpdomain` extension."""

    _markup_converters = {
        "commonmark": sphinx_mdinclude.convert,
        "restructuredtext": lambda x: x,
    }
    _response_examples_for = {"200", "201", "202", "2XX"}
    _request_parameters_order = ["header", "path", "query", "cookie"]

    option_spec = {
        "markup": functools.partial(directives.choice, values=_markup_converters),
        "format": str,
        "http-methods-order": _split_option,
        "response-examples-for": _split_option,
        "request-parameters-order": _split_option,
        "example-preference": _split_option,
        "request-example-preference": _split_option,
        "response-example-preference": _split_option,
        "generate-examples-from-schemas": _flag_or_bool,
        "no-json-schema-description": _flag_or_bool,
        "paths": _split_option,
        "include": _split_option,
        "exclude": _split_option,
        "methods": _split_option,
        "group": _flag_or_bool,
        "request": _flag_or_bool,
        "examples": _flag_or_bool,
    }

    def __init__(self, state, options):
        super().__init__(state, options)

        markup = options.get("markup")
        if markup is None and "format" in options:
            fmt = str(options["format"]).strip().lower()
            if fmt == "markdown":
                markup = "commonmark"
            elif fmt in ("rst", "restructuredtext"):
                markup = "restructuredtext"
        self._convert_markup = self._markup_converters[markup or "commonmark"]
        methods_order = _to_list(options.get("http-methods-order")) or []
        self._http_methods_order = [m.lower() for m in methods_order]

        response_examples_for = _to_list(options.get("response-examples-for"))
        if response_examples_for is not None:
            # OpenAPI permits numeric status codes, uppercase ranges 1XX–5XX,
            # and the lowercase special value "default". Preserve their case.
            self._response_examples_for = {str(x) for x in response_examples_for}
        elif options.get("examples"):
            # The legacy flag renders examples for every response. An explicit
            # response-examples-for option still takes precedence.
            self._response_examples_for = None
        else:
            self._response_examples_for = {"200", "201", "202", "2XX"}

        req_params_order = _to_list(options.get("request-parameters-order"))
        if req_params_order is not None:
            self._request_parameters_order = [
                parameter_type.lower() for parameter_type in req_params_order
            ]
        else:
            self._request_parameters_order = ["header", "path", "query", "cookie"]

        self._example_preference = _to_list(options.get("example-preference"))
        self._request_example_preference = (
            _to_list(options.get("request-example-preference"))
            or self._example_preference
        )
        self._response_example_preference = (
            _to_list(options.get("response-example-preference"))
            or self._example_preference
        )
        self._render_examples = bool(options.get("examples", True))
        self._generate_example_from_schema = bool(
            options.get(
                "generate-examples-from-schemas", options.get("examples", False)
            )
        )
        self._json_schema_description = not options.get(
            "no-json-schema-description", False
        )
        self._request_json_schema_description = (
            self._json_schema_description and options.get("request", True)
        )

    def render_restructuredtext_markup(self, spec):
        """Spec render entry point."""
        utils.normalize_spec(spec, **self._options)

        if spec.get("swagger") == "2.0":
            spec = lib2to3.convert(spec)
        yield from self.render_paths(spec.get("paths", {}), spec=spec)
        for name, path in spec.get("webhooks", {}).items():
            yield ""
            yield f".. admonition:: Webhook: {name}"
            yield ""
            yield "   The API provider sends this request to the webhook receiver URL."
            yield "   The webhook name is not an API path; ``{webhook_url}`` is a placeholder."
            yield ""
            for endpoint, method, operation in self._iter_path_operations(
                "{webhook_url}", path
            ):
                yield from indented(
                    self.render_operation(endpoint, method, operation, outbound=True)
                )
                yield ""

    def _iter_path_operations(self, endpoint, path, allowed_methods=None):
        """Yield operations with their own Path Item parameter inheritance."""
        common_parameters = path.get("parameters", [])
        methods = [
            method
            for method in path
            if isinstance(method, str) and method.lower() in _HTTP_METHODS
        ]
        for method in _iterinorder(methods, self._http_methods_order):
            if allowed_methods is not None and method.lower() not in allowed_methods:
                continue
            operation = copy.deepcopy(path[method])
            operation.setdefault("parameters", [])
            parameter_ids = {(p["name"], p["in"]) for p in operation["parameters"]}
            operation["parameters"] = [
                p
                for p in common_parameters
                if (p["name"], p["in"]) not in parameter_ids
            ] + operation["parameters"]
            yield endpoint, method, operation

    def render_paths(self, paths, spec=None):
        """Render OAS paths item."""

        if "paths" in self._options:
            expected_paths = set(_to_list(self._options["paths"]))
            if not expected_paths.issubset(paths):
                raise ValueError(
                    "One or more paths are not defined in the spec: %s."
                    % (", ".join(sorted(expected_paths - set(paths))),)
                )
            paths_to_render = [p for p in paths if p in expected_paths]
        elif "include" in self._options:
            paths_to_render = []
            for i in _to_list(self._options["include"]):
                ir = re.compile(i)
                for path in paths:
                    if ir.match(path) and path not in paths_to_render:
                        paths_to_render.append(path)
        else:
            paths_to_render = list(paths.keys())

        if "exclude" in self._options:
            excluded_patterns = [
                re.compile(pattern) for pattern in _to_list(self._options["exclude"])
            ]
            paths_to_render = [
                path
                for path in paths_to_render
                if not any(pattern.match(path) for pattern in excluded_patterns)
            ]

        allowed_methods = None
        if "methods" in self._options:
            allowed_methods = {m.lower() for m in _to_list(self._options["methods"])}

        if self._options.get("group"):
            tags_order = (
                [x["name"] for x in (spec.get("tags") or []) if "name" in x]
                if spec
                else []
            )
            groups = collections.OrderedDict([(t, []) for t in tags_order])

            for endpoint in paths_to_render:
                for endpoint, method, operation in self._iter_path_operations(
                    endpoint, paths[endpoint], allowed_methods
                ):
                    tag = (
                        operation.get("tags", [""])[0] if operation.get("tags") else ""
                    )
                    groups.setdefault(tag, []).append((endpoint, method, operation))

            for tag, operations in groups.items():
                if not operations:
                    continue
                yield from _header(tag if tag else "default")
                for endpoint, method, operation in operations:
                    yield from self.render_operation(endpoint, method, operation)
                    yield ""
        else:
            for endpoint in paths_to_render:
                for endpoint, method, operation in self._iter_path_operations(
                    endpoint, paths[endpoint], allowed_methods
                ):
                    yield from self.render_operation(endpoint, method, operation)
                    yield ""

    def render_operation(self, endpoint, method, operation, *, outbound=False):
        """Render OAS operation item."""

        directive_method = "openapi-" + method if outbound else method
        yield f".. http:{directive_method}:: {endpoint}"

        if operation.get("deprecated"):
            yield "   :deprecated:"
        yield ""

        if operation.get("summary"):
            yield f"   **{' '.join(operation['summary'].split())}**"
            yield ""

        if operation.get("description"):
            yield from indented(
                self._convert_markup(operation["description"]).strip().splitlines()
            )
            yield ""

        yield from indented(self.render_parameters(operation.get("parameters", [])))
        if "requestBody" in operation:
            if operation.get("parameters"):
                # The body can begin with a literal block rather than more
                # fields, particularly for form data or primitive schemas.
                yield ""
            yield from indented(
                self.render_request_body(operation["requestBody"], endpoint, method)
            )
        yield from indented(self.render_responses(operation.get("responses", {})))
        for name, callback in operation.get("callbacks", {}).items():
            yield ""
            yield f"   .. admonition:: Callback: {name}"
            yield ""
            yield "      The API provider sends this request to the callback URL."
            yield ""
            for expression, path in callback.items():
                # Callback Objects support scalar vendor-extension metadata.
                if not isinstance(expression, str) or expression.startswith("x-"):
                    continue
                for (
                    endpoint,
                    callback_method,
                    callback_operation,
                ) in self._iter_path_operations(expression, path):
                    yield from indented(
                        self.render_operation(
                            endpoint, callback_method, callback_operation, outbound=True
                        ),
                        6,
                    )
                    yield ""

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

        yield f":{kinds[parameter['in']]} {parameter['name']}:"

        if parameter.get("description"):
            yield from indented(
                self._convert_markup(parameter["description"]).strip().splitlines()
            )

        markers = _get_markers_from_object(parameter, schema)
        if markers:
            markers = ", ".join(markers)
            yield f":{kinds[parameter['in']]}type {parameter['name']}: {markers}"

    def render_request_body(self, request_body, endpoint, method):
        """Render OAS operation's requestBody."""

        if self._request_json_schema_description:
            for content_type, content in request_body["content"].items():
                if _is_json_mimetype(content_type) and content.get("schema"):
                    yield from self.render_json_schema_description(
                        content["schema"], "req"
                    )
                    yield ""
                    break

        yield from self.render_request_body_example(request_body, endpoint, method)
        yield ""

    def render_request_body_example(self, request_body, endpoint, method):
        """Render OAS operation's requestBody's example."""

        if not self._render_examples:
            return

        content_type, example = next(
            _iterexamples(
                request_body["content"],
                self._request_example_preference,
                self._generate_example_from_schema,
            ),
            (None, None),
        )

        if content_type and example:
            example = _format_example(content_type, example)

            yield ".. sourcecode:: http"
            yield ""
            yield f"   {method.upper()} {endpoint} HTTP/1.1"
            yield f"   Content-Type: {content_type}"
            yield ""
            yield from indented(example.splitlines())

    def render_responses(self, responses):
        """Render OAS operation's responses."""

        if self._json_schema_description:
            for status_code, response in responses.items():
                if _is_2xx_status(status_code):
                    for content_type, content in response.get("content", {}).items():
                        if _is_json_mimetype(content_type) and content.get("schema"):
                            yield from self.render_json_schema_description(
                                content["schema"], "res"
                            )
                            yield ""
                            break
                    break

        for status_code, response in responses.items():
            # Due to the way how YAML spec is parsed, status code may be
            # infered as integer. In order to spare some cycles on type
            # guessing going on, let's ensure it's always string at this point.
            yield from self.render_response(str(status_code), response)

    def render_response(self, status_code, response):
        """Render OAS operation's response."""

        status_code = str(status_code)
        # httpdomain's statuscode field creates numeric HTTP status roles.
        # OpenAPI's fallback and range keys are not individual status codes.
        field = (
            "response"
            if status_code == "default" or re.fullmatch(r"[1-5]XX", status_code)
            else "statuscode"
        )
        yield f":{field} {status_code}:"
        yield from indented(
            self._convert_markup(response["description"]).strip().splitlines()
        )

        if (
            self._render_examples
            and "content" in response
            and (
                self._response_examples_for is None
                or status_code in self._response_examples_for
            )
        ):
            yield ""
            yield from indented(
                self.render_response_example(response["content"], status_code)
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

                schema = header_value.get("schema", {})
                if "content" in header_value:
                    # According to OpenAPI v3 spec, 'content' in this case may
                    # have one and only one entry. Hence casting its values to
                    # list is not expensive and should be acceptable.
                    schema = list(header_value["content"].values())[0].get("schema", {})

                markers = _get_markers_from_object(header_value, schema)
                if markers:
                    markers = ", ".join(markers)
                    yield f":resheadertype {header_name}: {markers}"

    def render_response_example(self, media_type, status_code):
        if not self._render_examples:
            return

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
            example = _format_example(content_type, example)

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
                # OpenAPI permits numeric status codes and uppercase ranges
                # 1XX–5XX here; the special value "default" is handled above.
                # For a range, show its first code in the rendered example.
                status_code = str(status_code).replace("XX", "00")
                status_text = http.client.responses.get(int(status_code), "-")

            yield ".. sourcecode:: http"
            yield ""
            yield f"   HTTP/1.1 {status_code} {status_text}"
            yield f"   Content-Type: {content_type}"
            yield ""
            yield from indented(example.splitlines())

    def render_json_schema_description(self, schema, req_or_res):
        """Render JSON schema's description."""

        def _resolve_combining_schema(schema):
            if isinstance(schema, bool):
                return schema

            if "oneOf" in schema or "anyOf" in schema:
                merged_schema = schema.copy()
                keyword = "oneOf" if "oneOf" in schema else "anyOf"
                # Keep the existing first-variant description policy, but skip
                # False alternatives: they cannot describe any value.
                first = next(
                    (item for item in merged_schema.pop(keyword) if item is not False),
                    False,
                )
                if first is False:
                    return False
                if first is not True:
                    merged_schema.update(first)
                return merged_schema

            elif "allOf" in schema:
                # Since the item is represented by all schemas from the array,
                # the best we can do is to render them all at once
                # sequentially. Please note, the only way the end result will
                # ever make sense is when all schemas from the array are of
                # object type.
                merged_schema = copy.deepcopy(schema)
                for item in merged_schema.pop("allOf"):
                    item = _resolve_combining_schema(item)
                    if item is False:
                        return False
                    if item is True:
                        continue
                    merged_schema = _merge_mappings(merged_schema, item)
                return merged_schema

            elif "not" in schema:
                # Eh.. do nothing because I have no idea what can we do.
                return {}

            return schema

        def _traverse_schema(schema, name, is_required=False):
            if isinstance(schema, bool):
                return
            schema_type = _get_single_schema_type(schema)

            if {"oneOf", "anyOf", "allOf"} & schema.keys():
                # Since an item can represented by either or any schema from
                # the array of schema in case of `oneOf` and `anyOf`
                # respectively, the best we can do for them is to render the
                # first found variant. In other words, we are going to traverse
                # only a single schema variant and leave the rest out. This is
                # by design and it was decided so in order to keep produced
                # description clear and simple.
                yield from _traverse_schema(
                    _resolve_combining_schema(schema), name, is_required=is_required
                )

            elif "not" in schema:
                yield name, {}, is_required

            elif schema_type == "object":
                if name:
                    yield name, schema, is_required

                required = set(schema.get("required", []))

                for key, value in schema.get("properties", {}).items():
                    # In case of the first recursion call, when 'name' is an
                    # empty string, we should go with 'key' only in order to
                    # avoid leading dot at the beginning.
                    yield from _traverse_schema(
                        value,
                        f"{name}.{key}" if name else key,
                        is_required=key in required,
                    )

            elif schema_type == "array":
                yield from _traverse_schema(
                    schema.get("items", {}), f"{name}[]", is_required=is_required
                )

            elif "enum" in schema:
                yield name, schema, is_required

            elif schema_type is not None:
                yield name, schema, is_required

        schema = _resolve_combining_schema(schema)
        schema_type = _get_single_schema_type(schema)

        # On root level, httpdomain supports only 'object' and 'array' response
        # types. If it's something else, let's do not even try to render it.
        if schema_type not in {"object", "array"}:
            return

        # According to httpdomain's documentation, 'reqjsonobj' is an alias for
        # 'reqjson'. However, since the same name is passed as a type directive
        # internally, it actually can be used to specify its type. The same
        # goes for 'resjsonobj'.
        directives_map = {
            "req": {
                "object": ("reqjson", "reqjsonobj"),
                "array": ("reqjsonarr", "reqjsonarrtype"),
            },
            "res": {
                "object": ("resjson", "resjsonobj"),
                "array": ("resjsonarr", "resjsonarrtype"),
            },
        }

        # These httpdomain's fields always expect either JSON Object or JSON
        # Array. No primitive types are allowed as input.
        directive, typedirective = directives_map[req_or_res][schema_type]

        # Since we use JSON array specific httpdomain directives if a schema
        # we're about to render is an array, there's no need to render that
        # array in the first place.
        if schema_type == "array":
            schema = _resolve_combining_schema(schema.get("items", {}))

            # Even if a root element is an array, items it contain must not be
            # of a primitive types.
            if _get_single_schema_type(schema) not in {"object", "array"}:
                return

        for name, schema, is_required in _traverse_schema(schema, ""):
            yield f":{directive} {name}:"

            if schema.get("description"):
                yield from indented(
                    self._convert_markup(schema["description"]).strip().splitlines()
                )

            markers = _get_markers_from_object({}, schema)

            if is_required:
                markers.append("required")

            if markers:
                markers = ", ".join(markers)
                yield f":{typedirective} {name}: {markers}"
