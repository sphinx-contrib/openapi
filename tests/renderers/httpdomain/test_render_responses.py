"""OpenAPI spec renderer: render_responses."""

import textwrap


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
