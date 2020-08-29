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
            oas_fragment(
                f"""
                content:
                  {content_type}:
                    schema:
                      properties:
                        foo:
                          type: string
                        bar:
                          type: integer
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqjson foo:
        :reqjsonobj foo: string
        :reqjson bar:
        :reqjsonobj bar: integer

        """
    )


def test_render_request_body_schema_description_non_json(testrenderer, oas_fragment):
    """JSON schema is not rendered for non JSON mimetype."""

    markup = textify(
        testrenderer.render_request_body(
            oas_fragment(
                """
                content:
                  text/csv:
                    schema:
                      properties:
                        foo:
                          type: string
                        bar:
                          type: integer
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        """
    )


def test_render_request_body_schema_description_turned_off(fakestate, oas_fragment):
    """JSON schema description is not rendered b/c feature is off."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"no-json-schema-description": True},
    )

    markup = textify(
        testrenderer.render_request_body(
            oas_fragment(
                """
                content:
                  application/json:
                    schema:
                      properties:
                        foo:
                          type: string
                        bar:
                          type: integer
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        """
    )
