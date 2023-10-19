"""Partial OpenAPI v2.x (fka Swagger) to OpenAPI v3.x converter."""

import functools
import urllib

import picobox


__all__ = [
    "convert",
]


def convert(spec):
    """Convert a given OAS 2 spec to OAS 3."""

    return Lib2to3().convert(spec)


def _is_vendor_extension(key):
    """Return 'True' if a given key is a vendor extension."""

    return key.startswith("x-")


def _get_properties(node, properties, *, vendor_extensions=False):
    """Return a subset of 'node' properties w/ or wo/ vendor extensions."""

    return {
        key: value
        for key, value in node.items()
        if any([key in properties, vendor_extensions and _is_vendor_extension(key)])
    }


def _get_schema_properties(node, *, except_for=None):
    """Find and return 'Schema Object' properties."""

    except_for = except_for or set()
    schema = _get_properties(
        node,
        {
            "additionalProperties",
            "allOf",
            "default",
            "description",
            "discriminator",
            "enum",
            "example",
            "exclusiveMaximum",
            "exclusiveMinimum",
            "externalDocs",
            "format",
            "items",
            "maxItems",
            "maxLength",
            "maxProperties",
            "maximum",
            "minItems",
            "minLength",
            "minProperties",
            "minimum",
            "multipleOf",
            "pattern",
            "properties",
            "readOnly",
            "required",
            "title",
            "type",
            "uniqueItems",
            "xml",
        }
        - set(except_for),
    )

    if "discriminator" in schema:
        schema["discriminator"] = {"propertyName": schema["discriminator"]}
    return schema


def _items_wo_vendor_extensions(node):
    """Iterate over 'node' properties excluding vendor extensions."""

    for key, value in node.items():
        if _is_vendor_extension(key):
            continue
        yield key, value


class Lib2to3:
    _target_version = "3.0.3"
    _injector = picobox.Stack()

    def _insert_into_injector(name):
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(self, node, *args, **kwargs):
                with Lib2to3._injector.push(picobox.Box(), chain=True) as box:
                    box.put(name, factory=lambda: node, scope=picobox.threadlocal)
                    return fn(self, node, *args, **kwargs)

            return wrapper

        return decorator

    def __init__(self):
        self._schemes = set()

    @_insert_into_injector("spec")
    def convert(self, spec):
        # The following OAS 2 fields are ignored and not converted. Mostly due
        # to the fact that we expect *resolved* spec as input, and most of its
        # fields are used to group shared (i.e. referenced) objects that will
        # not exist in the resolved spec.
        #
        #  - definitions
        #  - parameters
        #  - responses
        #  - securityDefinitions
        #  - security
        #
        # By no means one must assume that these fields will never be
        # converted. I simply have no time to work on this, and for
        # sphixcontrib-openapi purposes it's not actually needed.

        converted = {
            "info": spec["info"],
            "openapi": self._target_version,
            "paths": self.convert_paths(spec["paths"]),
        }
        converted.update(
            _get_properties(spec, {"tags", "externalDocs"}, vendor_extensions=True),
        )

        servers = self.convert_servers(spec)
        if servers:
            converted["servers"] = servers

        return converted

    @_insert_into_injector("paths")
    def convert_paths(self, paths):
        converted = _get_properties(paths, {}, vendor_extensions=True)

        for endpoint, path in _items_wo_vendor_extensions(paths):
            converted[endpoint] = self.convert_path(path)

        return converted

    @_insert_into_injector("path")
    def convert_path(self, path):
        converted = _get_properties(path, {}, vendor_extensions=True)

        for key, value in _items_wo_vendor_extensions(path):
            if key == "parameters":
                converted[key] = self.convert_parameters(value)
            else:
                converted[key] = self.convert_operation(value)

        return converted

    @_insert_into_injector("operation")
    def convert_operation(self, operation):
        converted = _get_properties(
            operation,
            {
                "tags",
                "summary",
                "description",
                "externalDocs",
                "operationId",
                "deprecated",
                "security",
            },
            vendor_extensions=True,
        )

        # Memorize every encountered 'schemes'. Since this property does not
        # exist in OAS 3, it seems the best we can do is to use them in OAS 3
        # 'servers' object.
        self._schemes.update(operation.get("schemes", []))

        if "parameters" in operation:
            parameters = self.convert_parameters(operation["parameters"])

            # Both 'body' and 'formData' parameters are mutually exclusive,
            # therefore there's no way we may end up with both kinds at once.
            request_body = self.convert_request_body(operation)
            request_body = request_body or self.convert_request_body_formdata(operation)

            if parameters:
                converted["parameters"] = parameters

            if request_body:
                converted["requestBody"] = request_body

        converted["responses"] = self.convert_responses(operation["responses"])
        return converted

    @_injector.pass_("spec")
    def convert_request_body(self, operation, *, spec):
        # OAS 3 expects an explicitly specified mimetype of the request body.
        # It's not clear what to do if OAS 2 'consumes' is not defined. Let's
        # start with a glob pattern and figure out what a better option could
        # be later on.
        consumes = operation.get("consumes") or spec.get("consumes") or ["*/*"]

        for parameter in operation["parameters"]:
            if parameter["in"] == "body":
                # Since 'requestBody' is completely new and nested object in
                # OAS 3, it's not clear what should we insert possible vendor
                # extensions. Thus, let's ignore them until we figure it out.
                converted = _get_properties(parameter, {"description", "required"})
                converted["content"] = {
                    consume: {"schema": parameter["schema"]} for consume in consumes
                }
                return converted

        return None

    @_injector.pass_("spec")
    def convert_request_body_formdata(self, operation, *, spec):
        consumes = (
            operation.get("consumes")
            or spec.get("consumes")
            or ["application/x-www-form-urlencoded"]
        )
        supported = {
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        }
        mimetypes = supported.intersection(consumes)
        schema = {"type": "object", "properties": {}}

        for parameter in operation["parameters"]:
            if parameter["in"] == "formData":
                schema["properties"][parameter["name"]] = _get_schema_properties(
                    parameter, except_for={"name", "in", "required"}
                )

                if parameter.get("required"):
                    schema.setdefault("required", []).append(parameter["name"])

                # Excerpt from OpenAPI 2.x spec:
                #
                # > If type is "file", the consumes MUST be either
                # > "multipart/form-data", "application/x-www-form-urlencoded"
                # > or both and the parameter MUST be in "formData".
                #
                # This is weird since HTTP does not allow file uploading in
                # 'application/x-www-form-urlencoded'. Moreover, Swagger
                # editor complains if 'file' is detected and there's no
                # 'multipart/form-data' in `consumes'.
                if parameter["type"] == "file":
                    mimetypes = ["multipart/form-data"]

        if not schema["properties"]:
            return None
        return {"content": {mimetype: {"schema": schema} for mimetype in mimetypes}}

    @_insert_into_injector("parameters")
    def convert_parameters(self, parameters):
        return [
            self.convert_parameter(parameter)
            for parameter in parameters
            # If a parameter is one of the backward compatible type, delegate
            # the call to the converter function. Incompatible types, such as
            # 'formData' and 'body', must be handled separately since they are
            # reflected in 'Operation Object' in OAS 3.
            if parameter["in"] in {"query", "header", "path"}
        ]

    @_insert_into_injector("parameter")
    def convert_parameter(self, parameter):
        schema = _get_schema_properties(
            parameter,
            # Some of 'Parameter Object' properties have the same name as some
            # of 'Schema Object' properties. Since we know for sure that in
            # this context they are part of 'Parameter Object', we should
            # ignore their meaning as part of 'Schema Object'.
            except_for={"name", "in", "description", "required"},
        )
        converted = {
            key: value for key, value in parameter.items() if key not in schema
        }
        converted["schema"] = schema
        collection_format = converted.pop("collectionFormat", None)

        if converted["in"] in {"path", "header"} and collection_format == "csv":
            converted["style"] = "simple"
        elif converted["in"] in {"query"} and collection_format:
            styles = {
                "csv": {"style": "form", "explode": False},
                "multi": {"style": "form", "explode": True},
                "ssv": {"style": "spaceDelimited"},
                "pipes": {"style": "pipeDelimited"},
                # OAS 3 does not explicitly say what is the alternative to
                # 'collectionFormat=tsv'. We have no other option but to ignore
                # it. Fortunately, we don't care much as it's not used by the
                # renderer.
                "tsv": {},
            }
            converted.update(styles[collection_format])

        return converted

    @_insert_into_injector("responses")
    def convert_responses(self, responses):
        converted = _get_properties(responses, {}, vendor_extensions=True)

        for status_code, response in _items_wo_vendor_extensions(responses):
            converted[status_code] = self.convert_response(response)

        return converted

    @_injector.pass_("spec")
    @_injector.pass_("operation")
    @_insert_into_injector("response")
    def convert_response(self, response, *, spec, operation):
        converted = _get_properties(response, {"description"}, vendor_extensions=True)

        # OAS 3 expects an explicitly specified mimetype in the response. It's
        # not clear what to do if OAS 2 'produces' is not defined. Let's start
        # with a glob pattern and figure out what a better option could be
        # later on.
        produces = operation.get("produces") or spec.get("produces") or ["*/*"]
        schema = response.get("schema")
        examples = response.get("examples")

        if schema or examples:
            content = converted.setdefault("content", {})

            if schema is not None:
                for mimetype in produces:
                    content.setdefault(mimetype, {})["schema"] = schema

            if examples is not None:
                # According to OAS2, mimetypes in 'examples' property MUST be
                # one of the operation's 'produces'.
                for mimetype, example in examples.items():
                    content.setdefault(mimetype, {})["example"] = example

        if "headers" in response:
            converted["headers"] = {
                key: dict(
                    _get_properties(value, "description", vendor_extensions=True),
                    schema=_get_schema_properties(value, except_for={"description"}),
                )
                for key, value in response["headers"].items()
            }

        return converted

    def convert_servers(self, spec):
        """Convert OAS2 '(host, basePath, schemes)' triplet into OAS3 'servers' node."""

        host = spec.get("host", "")
        basepath = spec.get("basePath", "")
        schemes = self._schemes.union(spec.get("schemes", set()))

        # Since 'host', 'basePath' and 'schemes' are optional in OAS 2, there
        # may be the case when they aren't set. If that's happened it means
        # there's nothing to convert, and thus we simply return an empty list.
        if not host and not basepath and not schemes:
            return []

        if not schemes:
            # If 'host' is not set, the url will contain a bare basePath.
            # According to OAS 3, it's a valid URL, and both the host and the
            # scheme must be assumed to be the same as the server that shared
            # this OAS 3 spec.
            return [{"url": urllib.parse.urljoin(host, basepath)}]

        return [
            {"url": urllib.parse.urlunsplit([scheme, host, basepath, None, None])}
            for scheme in sorted(schemes)
        ]
