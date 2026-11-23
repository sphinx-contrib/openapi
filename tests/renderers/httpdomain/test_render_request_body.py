"""OpenAPI spec renderer: render_request_body."""

import textwrap

import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    "content_type", ["application/json", "application/foobar+json"]
)
def test_render_request_body_schema_description(
    testrenderer, oas_fragment, content_type
):
    """JSON schema description is rendered."""

    markup = textify(
        testrenderer.render_request_body(
            oas_fragment(f"""
                content:
                  {content_type}:
                    schema:
                      properties:
                        foo:
                          type: string
                        bar:
                          type: integer
                """),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent("""\
        :reqjson foo:
        :reqjsonobj foo: string
        :reqjson bar:
        :reqjsonobj bar: integer

        """)


def test_render_request_body_media_types(testrenderer, oas_fragment):
    markup = textify(
        testrenderer.render_request_body(
            oas_fragment("""
                content:
                  application/json:
                    schema:
                      properties:
                        text:
                          type: string
                  multipart/form-data:
                    schema:
                      type: object
                      required: [file]
                      properties:
                        file:
                          type: string
                          format: binary
                          description: File to upload
                        method:
                          type: string
                  application/x-www-form-urlencoded:
                    schema:
                      properties:
                        name:
                          type: string
                  text/csv:
                    schema:
                      type: string
                """),
            "/files",
            "POST",
        )
    )
    assert "**Request body** (``application/json``)" in markup
    assert ":reqjson text:" in markup
    assert "**Request body** (``multipart/form-data``)" in markup
    assert ":form file:\n   ``string:binary``, ``required``" in markup
    assert "File to upload" in markup
    assert ":form method:" in markup
    assert "**Request body** (``application/x-www-form-urlencoded``)" in markup
    assert ":form name:" in markup
    assert "**Request body** (``text/csv``)\n\n``string``" in markup


def test_render_request_body_schema_description_turned_off(fakestate, oas_fragment):
    """JSON schema description is not rendered b/c feature is off."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate,
        {"no-json-schema-description": True},
    )

    markup = textify(
        testrenderer.render_request_body(
            oas_fragment("""
                content:
                  application/json:
                    schema:
                      properties:
                        foo:
                          type: string
                        bar:
                          type: integer
                """),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent("""\
        """)
