"""
    sphinxcontrib.openapi
    ---------------------

    The OpenAPI spec renderer for Sphinx. It's a new way to document your
    RESTful API. Based on ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

try:
    from importlib.metadata import distribution, PackageNotFoundError
except ImportError:  # python < 3.8
    from importlib_metadata import distribution, PackageNotFoundError

from sphinxcontrib.openapi import renderers, directive

try:
    __version__ = distribution(__name__).version
except PackageNotFoundError:
    # package is not installed
    __version__ = None


_BUILTIN_RENDERERS = {
    "httpdomain": renderers.HttpdomainRenderer,
    "httpdomain:old": renderers.HttpdomainOldRenderer,
}
_DEFAULT_RENDERER_NAME = "httpdomain:old"


def _register_rendering_directives(app, conf):
    """Register rendering directives based on effective configuration."""

    renderers_map = dict(_BUILTIN_RENDERERS, **conf.openapi_renderers)

    for renderer_name, renderer_cls in renderers_map.items():
        app.add_directive(
            "openapi:%s" % renderer_name,
            directive.create_directive_from_renderer(renderer_cls),
        )

    if conf.openapi_default_renderer not in renderers_map:
        raise ValueError(
            "invalid 'openapi_default_renderer' value: "
            "no such renderer: '%s'" % conf.openapi_default_renderer
        )

    app.add_directive(
        "openapi",
        directive.create_directive_from_renderer(
            renderers_map[conf.openapi_default_renderer]
        ),
    )


def setup(app):
    app.add_config_value("openapi_default_renderer", _DEFAULT_RENDERER_NAME, "html")
    app.add_config_value("openapi_renderers", {}, "html")

    from sphinxcontrib import httpdomain

    for idx, fieldtype in enumerate(httpdomain.HTTPResource.doc_field_types):
        if fieldtype.name == 'requestheader':
            httpdomain.HTTPResource.doc_field_types[idx] = httpdomain.TypedField(
                fieldtype.name,
                label=fieldtype.label,
                names=fieldtype.names,
                typerolename='header',
                typenames=('reqheadertype', ),
            )

        if fieldtype.name == 'responseheader':
            httpdomain.HTTPResource.doc_field_types[idx] = httpdomain.TypedField(
                fieldtype.name,
                label=fieldtype.label,
                names=fieldtype.names,
                typerolename='header',
                typenames=('resheadertype', ),
            )

    app.setup_extension("sphinxcontrib.httpdomain")
    app.connect("config-inited", _register_rendering_directives)

    return {"version": __version__, "parallel_read_safe": True}
