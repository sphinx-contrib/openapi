"""OpenAPI spec renderer: render_response."""

import textwrap
import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    ["statuscode"], [pytest.param("200"), pytest.param("4XX"), pytest.param("default")]
)
def test_render_response_status_code(testrenderer, oas_fragment, statuscode):
    """Path response's definition is rendered for any status code."""

    markup = textify(
        testrenderer.render_response(
            statuscode,
            oas_fragment(
                """
                description: An evidence.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode %s:
           An evidence.
        """.rstrip()
        % statuscode
    )


def test_render_response_minimal(testrenderer, oas_fragment):
    """Path response's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.
        """.rstrip()
    )


def test_render_response_description_commonmark_default(testrenderer, oas_fragment):
    """Path response's 'description' must be in commonmark."""

    markup = textify(
        testrenderer.render_response(
            "200",
            oas_fragment(
                """
                description: |
                  An __evidence__ that matches
                  the `query`.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An **evidence** that matches
           the ``query``.
        """.rstrip()
    )


def test_render_response_description_commonmark(fakestate, oas_fragment):
    """Path response's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_response(
            "200",
            oas_fragment(
                """
                description: |
                  An __evidence__ that matches
                  the `query`.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An **evidence** that matches
           the ``query``.
        """.rstrip()
    )


def test_render_response_description_restructuredtext(fakestate, oas_fragment):
    """Path response's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_response(
            "200",
            oas_fragment(
                """
                description: |
                  An __evidence__ that matches
                  the `query`.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An __evidence__ that matches
           the `query`.
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["status_code", "status"],
    [
        pytest.param("200", "OK", id="200"),
        pytest.param("201", "Created", id="201"),
        pytest.param("202", "Accepted", id="202"),
    ],
)
def test_render_response_content_2xx(testrenderer, oas_fragment, status_code, status):
    """Path response's 'content' definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            status_code,
            oas_fragment(
                """
                description: An evidence.
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :statuscode {status_code}:
           An evidence.

           .. sourcecode:: http

              HTTP/1.1 {status_code} {status}
              Content-Type: application/json

              {{
                "foo": "bar",
                "baz": 42
              }}
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["status_code"],
    [
        pytest.param("301"),
        pytest.param("307"),
        pytest.param("401"),
        pytest.param("422"),
        pytest.param("502"),
    ],
)
def test_render_response_content_non_2xx(testrenderer, oas_fragment, status_code):
    """Path response's 'content' definition is NOT rendered."""

    markup = textify(
        testrenderer.render_response(
            status_code,
            oas_fragment(
                """
                description: An evidence.
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :statuscode {status_code}:
           An evidence.
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["status_code", "status"],
    [
        pytest.param("301", "Moved Permanently", id="301"),
        pytest.param("307", "Temporary Redirect", id="307"),
        pytest.param("401", "Unauthorized", id="401"),
        pytest.param("422", "Unprocessable Entity", id="422"),
    ],
)
def test_render_response_content_custom(fakestate, oas_fragment, status_code, status):
    """Path response's 'content' definition is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"response-examples-for": ["301", "307", "401", "422"]}
    )

    markup = textify(
        testrenderer.render_response(
            status_code,
            oas_fragment(
                """
                description: An evidence.
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :statuscode {status_code}:
           An evidence.

           .. sourcecode:: http

              HTTP/1.1 {status_code} {status}
              Content-Type: application/json

              {{
                "foo": "bar",
                "baz": 42
              }}
        """.rstrip()
    )


def test_render_response_content_custom_mismatch(fakestate, oas_fragment):
    """Path response's 'content' definition is NOT rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"response-examples-for": ["301", "307", "401", "422"]}
    )

    markup = textify(
        testrenderer.render_response(
            "200",
            oas_fragment(
                """
                description: An evidence.
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :statuscode 200:
           An evidence.
        """.rstrip()
    )


def test_render_response_header(testrenderer, oas_fragment):
    """Path response's 'header' definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            "200",
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: A unique request identifier.
                    schema:
                      type: string
                """
            ),
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


def test_render_response_header_minimal(testrenderer, oas_fragment):
    """Path response's 'header' minimal definition is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id: {}
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_description(testrenderer, oas_fragment):
    """Path response's 'header' description is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: A unique request identifier.
                """
            ),
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


def test_render_response_header_multiline_description(testrenderer, oas_fragment):
    """Path response's 'header' multiline description is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: |
                      A unique request
                      identifier.
                """
            ),
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


def test_render_response_header_description_commonmark_default(
    testrenderer, oas_fragment
):
    """Path response's 'header' description must be in commonmark by default."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: |
                      A unique __request__
                      `identifier`.
                """
            ),
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


def test_render_response_header_description_commonmark(fakestate, oas_fragment):
    """Path response's 'header' description can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: |
                      A unique __request__
                      `identifier`.
                """
            ),
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


def test_render_response_header_description_restructuredtext(fakestate, oas_fragment):
    """Path response's 'header' description can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    description: |
                      A unique __request__
                      `identifier`.
                """
            ),
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


def test_render_response_header_content_type(testrenderer, oas_fragment):
    """Path response's 'Content-Type' header is ignored."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  Content-Type: {}
                """
            ),
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


def test_render_response_header_required(testrenderer, oas_fragment):
    """Path response's header 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    required: true
                """
            ),
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


def test_render_response_header_required_false(testrenderer, oas_fragment):
    """Path response's header 'required' marker is not rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    required: false
                """
            ),
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_deprecated(testrenderer, oas_fragment):
    """Path response's header 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    deprecated: true
                """
            ),
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


def test_render_response_header_deprecated_false(testrenderer, oas_fragment):
    """Path response's header 'deprecated' marker is not rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    deprecated: false
                """
            ),
        )
    )

    assert markup == textwrap.dedent(
        """\
        :statuscode 200:
           An evidence.

        :resheader X-Request-Id:
        """.rstrip()
    )


def test_render_response_header_required_deprecated(testrenderer, oas_fragment):
    """Path response's header markers are rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    required: true
                    deprecated: true
                """
            ),
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


def test_render_response_header_type(testrenderer, oas_fragment):
    """Path response's header type is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    schema:
                      type: string
                """
            ),
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


def test_render_response_header_type_with_format(testrenderer, oas_fragment):
    """Path response's header type with format is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    schema:
                      type: string
                      format: uuid4
                """
            ),
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


def test_render_response_header_type_from_content(testrenderer, oas_fragment):
    """Path response's header type from content is rendered."""

    markup = textify(
        testrenderer.render_response(
            200,
            oas_fragment(
                """
                description: An evidence.
                headers:
                  X-Request-Id:
                    content:
                      text/plain:
                        schema:
                          type: string
                """
            ),
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
