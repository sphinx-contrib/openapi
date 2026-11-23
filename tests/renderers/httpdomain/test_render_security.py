import pytest

from sphinxcontrib.openapi.renderers import HttpdomainRenderer


@pytest.mark.parametrize("enabled", [False, True])
def test_operation_security(oas_fragment, enabled):
    renderer = HttpdomainRenderer(None, {"security": None} if enabled else {})
    spec = oas_fragment("""
        openapi: 3.1.0
        info:
          title: Example API
          version: "1"
        components:
          securitySchemes:
            bearer:
              type: http
              scheme: bearer
            key:
              type: apiKey
              name: X-API-Key
              in: header
        security:
          - bearer: []
            oauth: [read, write]
          - key: []
          - {}
        paths:
          /files:
            get:
              responses:
                "204":
                  description: No content
            post:
              security: []
              responses:
                "204":
                  description: No content
        """)
    markup = "\n".join(renderer.render_restructuredtext_markup(spec))
    get, post = markup.split(".. http:post:: /files")
    assert ("**Security**" in get) is enabled
    assert ("**Security**" in post) is enabled
    if enabled:
        assert (
            "* ``bearer`` (HTTP ``bearer``) and "
            "``oauth`` with scopes ``read``, ``write``" in get
        )
        assert "* ``key`` (``X-API-Key`` header)" in get
        assert "* No authentication required." in get
        assert "No authentication required." in post
        assert "bearer" not in post


def test_undeclared_security_is_omitted():
    renderer = HttpdomainRenderer(None, {"security": None})
    assert not list(renderer.render_security(None))
