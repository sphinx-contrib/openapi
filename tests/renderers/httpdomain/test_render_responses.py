"""OpenAPI spec renderer: render_responses."""

import textwrap

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_responses_no_items(testrenderer, oas_fragment):
    """No response definitions are rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                {}
                """
            )
        )
    )
    assert markup == ""


def test_render_responses_one_item(testrenderer, oas_fragment):
    """One usual response definition is rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '200':
                  description: An evidence.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        """.rstrip()
    )


def test_render_responses_one_item_status_code_int(testrenderer, oas_fragment):
    """One usual response definition is rendered even if status code is integer."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                200:
                  description: An evidence.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        """.rstrip()
    )


def test_render_responses_many_items(testrenderer, oas_fragment):
    """Many response definitions are rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '200':
                  description: An evidence.
                '404':
                  description: An evidence not found.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        :statuscode 404:
           An evidence not found.
        """.rstrip()
    )


def test_render_responses_json_schema_description(testrenderer, oas_fragment):
    """JSON schema description is rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '200':
                  description: An evidence.
                  content:
                    application/json:
                      schema:
                        properties:
                          foo:
                            type: string
                          bar:
                            type: integer
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :resjson foo:
        :resjsonobj foo: string
        :resjson bar:
        :resjsonobj bar: integer

        :statuscode 200:
           An evidence.
        """
    )


def test_render_responses_json_schema_description_4xx(testrenderer, oas_fragment):
    """JSON schema description is rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '400':
                  description: An evidence.
                  content:
                    application/json:
                      schema:
                        properties:
                          foo:
                            type: string
                          bar:
                            type: integer
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 400:
           An evidence.
        """.rstrip()
    )


def test_render_responses_json_schema_description_first_2xx(testrenderer, oas_fragment):
    """JSON schema description is rendered."""

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '400':
                  description: An error.
                  content:
                    application/json:
                      schema:
                        properties:
                          aaa:
                            type: string
                '200':
                  description: An evidence.
                  content:
                    application/json:
                      schema:
                        properties:
                          foo:
                            type: string
                          bar:
                            type: integer
                '201':
                  description: An evidence created.
                  content:
                    application/json:
                      schema:
                        properties:
                          bbb:
                            type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :resjson foo:
        :resjsonobj foo: string
        :resjson bar:
        :resjsonobj bar: integer

        :statuscode 400:
           An error.
        :statuscode 200:
           An evidence.

        :statuscode 201:
           An evidence created.
        """
    )


def test_render_responses_json_schema_description_turned_off(fakestate, oas_fragment):
    """JSON schema description is not rendered b/c feature is off."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"no-json-schema-description": True},
    )

    markup = textify(
        testrenderer.render_responses(
            oas_fragment(
                """
                '200':
                  description: An evidence.
                  content:
                    application/json:
                      schema:
                        properties:
                          foo:
                            type: string
                          bar:
                            type: integer
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        """
    )
