"""OpenAPI spec renderer: render_response_example."""

import textwrap

import pytest
import responses

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    ["media_type"],
    [
        pytest.param(
            """
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
            application/json:
              example:
                foo: bar
                baz: 42
            """,
            id="example",
        ),
        pytest.param(
            """
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
def test_render_response_example(testrenderer, oas_fragment, media_type):
    """Path response's example is rendered."""

    markup = textify(
        testrenderer.render_response_example(oas_fragment(media_type), "200")
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip()
    )


def test_render_response_example_1st_from_examples(testrenderer, oas_fragment):
    """Path response's first example is rendered."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
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
            "200",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip()
    )


def test_render_response_example_1st_from_media_type(testrenderer, oas_fragment):
    """Path response's example from first media type is rendered."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/plain:
                  example: |
                    foo = "bar"
                    baz = 42
                application/json:
                  schema:
                    type: object
                """
            ),
            "200",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["example_preference_key"],
    [pytest.param("response-example-preference"), pytest.param("example-preference")],
)
def test_render_response_example_preference(
    fakestate, example_preference_key, oas_fragment
):
    """Path response's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {example_preference_key: ["text/plain"]}
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
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
            "200",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["example_preference_key"],
    [pytest.param("response-example-preference"), pytest.param("example-preference")],
)
def test_render_response_example_preference_complex(
    fakestate, example_preference_key, oas_fragment
):
    """Path response's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {example_preference_key: ["application/json", "text/plain"]}
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
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
            "200",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


def test_render_response_example_preference_priority(fakestate, oas_fragment):
    """Path response's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate,
        {
            "example-preference": ["application/json"],
            "response-example-preference": ["text/plain"],
        },
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
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
            "200",
        )
    )

    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip()
    )


@responses.activate
def test_render_response_example_external(testrenderer, oas_fragment):
    """Path response's example can be retrieved from external location."""

    responses.add(
        responses.GET,
        "https://example.com/json/examples/test.json",
        json={"foo": "bar", "baz": 42},
        status=200,
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                """
            ),
            "200",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {"foo": "bar", "baz": 42}
        """.rstrip()
    )


@responses.activate
def test_render_response_example_external_errored_next_example(
    testrenderer, caplog, oas_fragment
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                    fallback:
                      value: '{"spam": 42}'
                """
            ),
            "200",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {"spam": 42}
        """.rstrip()
    )


@responses.activate
def test_render_response_example_external_errored_next_media_type(
    testrenderer, oas_fragment, caplog
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                text/csv:
                  example: spam,42
                """
            ),
            "200",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/csv

           spam,42
        """.rstrip()
    )


def test_render_response_example_content_type(testrenderer, oas_fragment):
    """Path response's example can render something other than application/json."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """
            ),
            "200",
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


def test_render_response_example_noop(testrenderer, oas_fragment):
    """Path response's example is not rendered if there's nothing to render."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                application/json:
                  schema:
                    type: object
                """
            ),
            "200",
        )
    )

    assert markup == ""


@pytest.mark.parametrize(
    ["status_code", "status_text"],
    [
        pytest.param("201", "Created", id="201"),
        pytest.param("307", "Temporary Redirect", id="307"),
        pytest.param("422", "Unprocessable Entity", id="422"),
    ],
)
def test_render_response_status_code(
    testrenderer, oas_fragment, status_code, status_text
):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """
            ),
            status_code,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["status_range", "status_code", "status_text"],
    [
        pytest.param("2XX", "200", "OK", id="2XX"),
        pytest.param("3XX", "300", "Multiple Choices", id="3XX"),
        pytest.param("4XX", "400", "Bad Request", id="4XX"),
    ],
)
def test_render_response_status_code_range(
    testrenderer, oas_fragment, status_range, status_code, status_text
):
    """Path response's example is rendered with proper status range."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """
            ),
            status_range,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["status_code", "status_text"],
    [
        pytest.param("201", "Created", id="201"),
        pytest.param("307", "Temporary Redirect", id="307"),
        pytest.param("422", "Unprocessable Entity", id="422"),
    ],
)
def test_render_response_status_code_int(
    testrenderer, oas_fragment, status_code, status_text
):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """
            ),
            status_code,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )


def test_render_response_status_code_default(testrenderer, oas_fragment):
    """Path response's example is rendered when default is passed."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment(
                """
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """
            ),
            "default",
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        .. sourcecode:: http

           HTTP/1.1 000 Reason-Phrase
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip()
    )
