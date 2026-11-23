import pytest

from sphinxcontrib.openapi.renderers import HttpdomainRenderer


@pytest.mark.parametrize("enabled", [False, True])
def test_render_info(oas_fragment, enabled):
    renderer = HttpdomainRenderer(None, {"info": None} if enabled else {})
    spec = oas_fragment("""
        openapi: 3.1.0
        info:
          title: Example API
          version: "1"
          description: Read the *overview*.
        paths:
          /files:
            get:
              responses:
                "204":
                  description: No content
        """)
    markup = "\n".join(renderer.render_restructuredtext_markup(spec))
    assert (".. rubric:: Example API" in markup) is enabled
    assert ("Read the *overview*." in markup) is enabled
    if enabled:
        assert markup.index("Example API") < markup.index("/files")
