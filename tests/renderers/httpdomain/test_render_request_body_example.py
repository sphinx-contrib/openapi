"""OpenAPI spec renderer: render_request_body_example."""

import textwrap

import pytest
import responses

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    ["content"],
    [
        pytest.param(
            """
            content:
              application/json:
                examples:
                  test:
                    value:
                      foo: bar
                      baz: 42
            """,
            id="examples",
        ),
        pytest.param(
            """
            content:
              application/json:
                example:
                  foo: bar
                  baz: 42
            """,
            id="example",
        ),
        pytest.param(
            """
            content:
              application/json:
                schema:
                  example:
                    foo: bar
                    baz: 42
            """,
            id="schema/example",
        ),
        pytest.param(
            """
            content:
              application/json:
                examples:
                  test:
                    value: |
                      {
                        "foo": "bar",
                        "baz": 42
                      }
            """,
            id="examples::str",
        ),
        pytest.param(
            """
            content:
              application/json:
                example: |
                  {
                    "foo": "bar",
                    "baz": 42
                  }
            """,
            id="example::str",
        ),
        pytest.param(
            """
            content:
              application/json:
                schema:
                  example: |
                    {
                      "foo": "bar",
                      "baz": 42
                    }
            """,
            id="schema/example::str",
        ),
        pytest.param(
            """
            content:
              application/json:
                schema:
                  example:
                    foobar: bazinga
                example:
                  foo: bar
                  baz: 42
            """,
            id="example-beats-schema/example",
        ),
        pytest.param(
            """
            content:
              application/json:
                schema:
                  example:
                    foobar: bazinga
                examples:
                  test:
                    value:
                      foo: bar
                      baz: 42
            """,
            id="examples-beats-schema/example",
        ),
    ],
)
def test_render_request_body_example(testrenderer, content, oas_fragment):
    """Request body is rendered."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(content), "/evidences/{evidenceId}", "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip()
    )


def test_render_request_body_example_1st_from_examples(testrenderer, oas_fragment):
    """Request body's first example is rendered."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    examples:
                      foo:
                        value:
                          foo: bar
                          baz: 42
                      bar:
                        value:
                          foobar: bazinga
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip()
    )


def test_render_request_body_example_1st_from_media_type(testrenderer, oas_fragment):
    """Request body's example from first media type is rendered."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  text/plain:
                    example: |
                      foo = "bar"
                      baz = 42
                  application/json:
                    schema:
                      type: object
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["example_preference_key"],
    [pytest.param("request-example-preference"), pytest.param("example-preference")],
)
def test_render_request_body_example_preference(
    fakestate, oas_fragment, example_preference_key
):
    """Request body's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {example_preference_key: ["text/plain"]}
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                  text/plain:
                    example: |
                      foo = "bar"
                      baz = 42
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["example_preference_key"],
    [pytest.param("request-example-preference"), pytest.param("example-preference")],
)
def test_render_request_body_example_preference_complex(
    fakestate, oas_fragment, example_preference_key
):
    """Request body's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {example_preference_key: ["application/json", "text/plain"]}
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  text/csv:
                    example: |
                      foo,baz
                      bar,42
                  text/plain:
                    example: |
                      foo = "bar"
                      baz = 42
                  application/json:
                    schema:
                      type: object
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


def test_render_request_body_example_preference_priority(fakestate, oas_fragment):
    """Request body's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate,
        {
            "example-preference": ["application/json"],
            "request-example-preference": ["text/plain"],
        },
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    example:
                      foo: bar
                      baz: 42
                  text/plain:
                    example: |
                      foo = "bar"
                      baz = 42
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@responses.activate
def test_render_request_body_example_external(testrenderer, oas_fragment):
    """Request body's example can be retrieved from external location."""

    responses.add(
        responses.GET,
        "https://example.com/json/examples/test.json",
        json={"foo": "bar", "baz": 42},
        status=200,
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    examples:
                      test:
                        externalValue: https://example.com/json/examples/test.json
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: application/json

           {"foo": "bar", "baz": 42}
        """.rstrip()
    )


@responses.activate
def test_render_request_body_example_external_errored_next_example(
    testrenderer, oas_fragment, caplog
):
    """Request body's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    examples:
                      test:
                        externalValue: https://example.com/json/examples/test.json
                      fallback:
                        value: '{"spam": 42}'
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: application/json

           {"spam": 42}
        """.rstrip()
    )


@responses.activate
def test_render_request_body_example_external_errored_next_media_type(
    testrenderer, oas_fragment, caplog,
):
    """Request body's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    examples:
                      test:
                        externalValue: https://example.com/json/examples/test.json
                  text/csv:
                    example: spam,42
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/csv

           spam,42
        """.rstrip()
    )


def test_render_request_body_example_content_type(testrenderer, oas_fragment):
    """Request body's example can render something other than application/json."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  text/csv:
                    example: |
                      foo,baz
                      bar,42
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           POST /evidences/{evidenceId} HTTP/1.1
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


def test_render_request_body_example_noop(testrenderer, oas_fragment):
    """Request body's example is not rendered if there's nothing to render."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  application/json:
                    schema:
                      type: object
                """
            ),
            "/evidences/{evidenceId}",
            "POST",
        )
    )

    assert markup == ""


@pytest.mark.parametrize(
    ["http_method"], [pytest.param("POST"), pytest.param("PUT"), pytest.param("PATCH")]
)
def test_render_request_body_example_http_method(
    testrenderer, oas_fragment, http_method,
):
    """Request body's example shows proper HTTP method."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  text/csv:
                    example: |
                      foo,baz
                      bar,42
                """
            ),
            "/evidences/{evidenceId}",
            http_method,
        )
    )

    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           {http_method} /evidences/{{evidenceId}} HTTP/1.1
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["http_endpoint"],
    [pytest.param("/evidences/{evidenceId}"), pytest.param("/heroes/{heroId}")],
)
def test_render_request_body_example_http_endpoint(
    testrenderer, oas_fragment, http_endpoint,
):
    """Request body's example shows proper HTTP method."""

    markup = textify(
        testrenderer.render_request_body_example(
            oas_fragment(
                """
                content:
                  text/csv:
                    example: |
                      foo,baz
                      bar,42
                """
            ),
            http_endpoint,
            "POST",
        )
    )

    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           POST {http_endpoint} HTTP/1.1
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )
