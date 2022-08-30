"""Here lies still breathing and only renderer implementation."""

from docutils.parsers.rst import directives

from sphinxcontrib.openapi import openapi20, openapi30, utils
from sphinxcontrib.openapi.renderers import abc


class HttpdomainOldRenderer(abc.RestructuredTextRenderer):

    option_spec = {
        # A list of endpoints to be rendered. Endpoints must be whitespace
        # delimited.
        "paths": lambda s: s.split(),
        # Regular expression patterns to includes/excludes endpoints to/from
        # rendering. Similar to paths, the patterns must be whitespace
        # delimited.
        "include": lambda s: s.split(),
        "exclude": lambda s: s.split(),
        # Endpoints to be included based on HTTP method names.
        "methods": lambda s: s.split(),
        # Render the request body structure when passed.
        "request": directives.flag,
        # Render request/response examples when passed.
        "examples": directives.flag,  # render examples when passed
        # Group endpoints by tags when passed. By default, no grouping is
        # applied and endpoints are rendered in the order they met in spec.
        "group": directives.flag,
        # Markup format to render OpenAPI descriptions.
        "format": str,
    }

    def __init__(self, state, options):
        self._state = state
        self._options = options

    def render_restructuredtext_markup(self, spec):
        # OpenAPI spec may contain JSON references, common properties, etc.
        # Trying to render the spec "As Is" will require to put multiple if-s
        # around the code. In order to simplify rendering flow, let's make it
        # have only one (expected) schema, i.e. normalize it.
        utils.normalize_spec(spec, **self._options)

        # We support both OpenAPI 2.0 (f.k.a. Swagger) and OpenAPI 3.0.0, so
        # determine which version we are parsing here.
        spec_version = spec.get("openapi", spec.get("swagger", "2.0"))
        if spec_version.startswith("2."):
            openapihttpdomain = openapi20.openapihttpdomain
        elif spec_version.startswith("3."):
            openapihttpdomain = openapi30.openapihttpdomain
        else:
            raise ValueError("Unsupported OpenAPI version (%s)" % spec_version)

        yield from openapihttpdomain(spec, **self._options)
