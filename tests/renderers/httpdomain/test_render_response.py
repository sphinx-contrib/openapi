"""OpenAPI spec renderer: render_response."""

import textwrap
import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    ["statuscode"], [pytest.param("200"), pytest.param("4XX"), pytest.param("default")]
)
def test_render_response_status_code(testrenderer, statuscode):
    """Path response's definition is rendered for any status code."""

    markup = textify(
        testrenderer.render_response(statuscode, {"description": "An evidence."})
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode %s:
           An evidence.
        """.rstrip()
        % statuscode
    )


def test_render_response_minimal(testrenderer):
    """Path response's minimal definition is rendered."""

    markup = textify(testrenderer.render_response(200, {"description": "An evidence."}))
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        """.rstrip()
    )


def test_render_response_description_commonmark_default(testrenderer):
    """Path response's 'description' must be in commonmark."""

    markup = textify(
        testrenderer.render_response(
            "200", {"description": "An __evidence__ that matches\nthe `query`."}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An **evidence** that matches
           the ``query``.
        """.rstrip()
    )


def test_render_response_description_commonmark(fakestate):
    """Path response's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_response(
            "200", {"description": "An __evidence__ that matches\nthe `query`."}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An **evidence** that matches
           the ``query``.
        """.rstrip()
    )


def test_render_response_description_restructuredtext(fakestate):
    """Path response's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_response(
            "200", {"description": "An __evidence__ that matches\nthe `query`."}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An __evidence__ that matches
           the `query`.
        """.rstrip()
    )


def test_render_response_content(testrenderer):
    """Path response's 'content' definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            "200",
            {
                "description": "An evidence.",
                "content": {"application/json": {"example": {"foo": "bar", "baz": 42}}},
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

           .. sourcecode:: http

              HTTP/1.1 200 OK
              Content-Type: application/json

              {
                "foo": "bar",
                "baz": 42
              }
        """.rstrip()
    )


def test_render_response_header(testrenderer):
    """Path response's 'header' definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            "200",
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {
                        "description": "A unique request identifier.",
                        "schema": {"type": "string"},
                    }
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique request identifier.
        :resheadertype X-Request-Id: string
        """.rstrip()
    )


def test_render_response_header_minimal(testrenderer):
    """Path response's 'header' minimal definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            200, {"description": "An evidence.", "headers": {"X-Request-Id": {}}},
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_description(testrenderer):
    """Path response's 'header' description is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {"description": "A unique request identifier."}
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique request identifier.
        """.rstrip()
    )


def test_render_response_header_multiline_description(testrenderer):
    """Path response's 'header' multiline description is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {"description": "A unique request\nidentifier."}
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique request
           identifier.
        """.rstrip()
    )


def test_render_response_header_description_commonmark_default(testrenderer):
    """Path response's 'header' description must be in commonmark by default."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {
                        "description": "A unique __request__\n`identifier`.",
                    }
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique **request**
           ``identifier``.
        """.rstrip()
    )


def test_render_response_header_description_commonmark(fakestate):
    """Path response's 'header' description can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {
                        "description": "A unique __request__\n`identifier`.",
                    }
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique **request**
           ``identifier``.
        """.rstrip()
    )


def test_render_response_header_description_restructuredtext(fakestate):
    """Path response's 'header' description can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {
                        "description": "A unique __request__\n`identifier`.",
                    }
                },
            },
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
           A unique __request__
           `identifier`.
        """.rstrip()
    )


def test_render_response_header_content_type(testrenderer):
    """Path response's 'Content-Type' header is ignored."""

    markup = textify(
        testrenderer.render_response(
            200, {"description": "An evidence.", "headers": {"Content-Type": {}}},
        )
    )

    # There's an extra newline at the end of markup if there's at least one
    # response header defined.
    assert markup.rstrip() == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        """.rstrip()
    )


def test_render_response_header_required(testrenderer):
    """Path response's header 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"required": True}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: required
        """.rstrip()
    )


def test_render_response_header_required_false(testrenderer):
    """Path response's header 'required' marker is not rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"required": False}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_deprecated(testrenderer):
    """Path response's header 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"deprecated": True}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: deprecated
        """.rstrip()
    )


def test_render_response_header_deprecated_false(testrenderer):
    """Path response's header 'deprecated' marker is not rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"deprecated": False}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_required_deprecated(testrenderer):
    """Path response's header markers are rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"required": True, "deprecated": True}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: required, deprecated
        """.rstrip()
    )


def test_render_response_header_type(testrenderer):
    """Path response's header type is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {"X-Request-Id": {"schema": {"type": "string"}}},
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: string
        """.rstrip()
    )


def test_render_response_header_type_with_format(testrenderer):
    """Path response's header type with format is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {"schema": {"type": "string", "format": "uuid4"}}
                },
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: string:uuid4
        """.rstrip()
    )


def test_render_response_header_type_from_content(testrenderer):
    """Path response's header type from content is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            {
                "description": "An evidence.",
                "headers": {
                    "X-Request-Id": {
                        "content": {"text/plain": {"schema": {"type": "string"}}}
                    }
                },
            },
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        :resheadertype X-Request-Id: string
        """.rstrip()
    )
