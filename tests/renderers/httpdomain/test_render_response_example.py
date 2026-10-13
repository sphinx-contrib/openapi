"""OpenAPI spec renderer: render_response_example."""

import json
import sys
import textwrap

import pytest
import responses

from sphinxcontrib.openapi import renderers

if sys.version_info[:2] >= (3, 13):
    http_422_description = "Unprocessable Content"
else:
    http_422_description = "Unprocessable Entity"


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize("source", ["example", "examples", "schema/example"])
def test_render_response_declared_string_example(testrenderer, source):
    """A string instance is quoted for JSON even with legacy example keywords."""
    media_type = {"schema": {"type": "string"}}
    if source == "examples":
        media_type["examples"] = {"first": {"value": "."}}
    elif source == "example":
        media_type["example"] = "."
    else:
        media_type["schema"]["example"] = "."
    markup = textify(
        testrenderer.render_response_example({"application/json": media_type}, "200")
    )
    payload = textwrap.dedent(markup.split("Content-Type: application/json\n\n")[1])
    assert json.loads(payload) == "."


@pytest.mark.parametrize("value", [0, 0.0, False, None, "", [], {}])
@pytest.mark.parametrize(
    "source", ["example", "examples", "schema/example", "schema/examples"]
)
@pytest.mark.parametrize("generate", [False, True])
def test_render_response_explicit_falsey_example(fakestate, value, source, generate):
    """Explicit falsey values override schema examples and generated defaults."""

    schema = {"example": {"fallback": True}, "examples": [{"fallback": False}]}
    media_type = {"schema": schema}
    if source == "example":
        media_type["example"] = value
    elif source == "examples":
        media_type["examples"] = {
            "annotation": {"summary": "No value here"},
            "first": {"value": value},
            "second": {"value": "fallback"},
        }
    elif source == "schema/example":
        schema["example"] = value
    else:
        schema.pop("example")
        schema["examples"] = [value, {"fallback": True}]
    renderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": generate}
    )
    markup = textify(
        renderer.render_response_example({"application/json": media_type}, "200")
    )
    expected_lines = [
        ".. sourcecode:: http",
        "",
        "   HTTP/1.1 200 OK",
        "   Content-Type: application/json",
        "",
    ] + ["   " + line for line in json.dumps(value, indent=2).splitlines()]
    assert markup == "\n".join(expected_lines)


@pytest.mark.parametrize("value", ["literal", '{"value": false}', {"value": False}])
def test_render_response_schema_examples_literal_values(testrenderer, value):
    """Schema examples are instance values, not named Example Objects or raw JSON."""

    markup = textify(
        testrenderer.render_response_example(
            {"application/json": {"schema": {"examples": [value]}}}, "200"
        )
    )
    payload = textwrap.dedent(markup.split("Content-Type: application/json\n\n")[1])
    assert json.loads(payload) == value


@pytest.mark.parametrize("generate", [False, True])
def test_render_response_annotation_only_examples(fakestate, generate):
    """Example Objects without values do not hide available schema examples."""

    content = {
        "application/json": {
            "examples": {"annotation": {"summary": "No value here"}},
            "schema": {"examples": [None]},
        }
    }
    renderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": generate}
    )
    markup = textify(renderer.render_response_example(content, "200"))
    assert markup.endswith("   null")


@responses.activate
def test_render_response_external_empty_payload(testrenderer):
    """Fetched payloads stay verbatim and do not mutate their Example Object."""

    url = "https://example.com/empty.json"
    responses.add(responses.GET, url, body="", content_type="application/json")
    content = {"application/json": {"examples": {"external": {"externalValue": url}}}}
    markup = textify(testrenderer.render_response_example(content, "200"))
    assert markup == "\n".join(
        [
            ".. sourcecode:: http",
            "",
            "   HTTP/1.1 200 OK",
            "   Content-Type: application/json",
            "",
        ]
    )
    assert content["application/json"]["examples"]["external"] == {"externalValue": url}


@pytest.mark.parametrize(
    "content_type",
    [
        "application/problem+json",
        "APPLICATION/JSON",
        "application/json; charset=utf-8",
    ],
)
def test_render_response_schema_examples_json_media_type(testrenderer, content_type):
    """JSON suffixes, case and media-type parameters do not change serialization."""

    markup = textify(
        testrenderer.render_response_example(
            {content_type: {"schema": {"examples": ["literal"]}}}, "200"
        )
    )
    payload = textwrap.dedent(markup.split(f"Content-Type: {content_type}\n\n")[1])
    assert json.loads(payload) == "literal"


def test_render_response_empty_text_example(testrenderer):
    """JSON serialization must not quote empty text/plain examples."""

    markup = textify(
        testrenderer.render_response_example(
            {"text/plain": {"schema": {"examples": [""]}}}, "200"
        )
    )
    assert markup.endswith("   Content-Type: text/plain\n")


def test_render_response_empty_schema_examples(fakestate):
    """An empty schema examples array supplies no example, but permits generation."""

    content = {"application/json": {"schema": {"type": "string", "examples": []}}}
    assert (
        textify(
            renderers.HttpdomainRenderer(fakestate, {}).render_response_example(
                content, "200"
            )
        )
        == ""
    )
    renderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(renderer.render_response_example(content, "200"))
    assert (
        json.loads(
            textwrap.dedent(markup.split("Content-Type: application/json\n\n")[1])
        )
        == "string"
    )


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
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip())


def test_render_response_example_1st_from_examples(testrenderer, oas_fragment):
    """Path response's first example is rendered."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                application/json:
                  examples:
                    foo:
                      value:
                        foo: bar
                        baz: 42
                    bar:
                      value:
                        foobar: bazinga
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {
             "foo": "bar",
             "baz": 42
           }
        """.rstrip())


def test_render_response_example_1st_from_media_type(testrenderer, oas_fragment):
    """Path response's example from first media type is rendered."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                text/plain:
                  example: |
                    foo = "bar"
                    baz = 42
                application/json:
                  schema:
                    type: object
                """),
            "200",
        )
    )

    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip())


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
            oas_fragment("""
                application/json:
                  example:
                    foo: bar
                    baz: 42
                text/plain:
                  example: |
                    foo = "bar"
                    baz = 42
                """),
            "200",
        )
    )

    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip())


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
            oas_fragment("""
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
                """),
            "200",
        )
    )

    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip())


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
            oas_fragment("""
                application/json:
                  example:
                    foo: bar
                    baz: 42
                text/plain:
                  example: |
                    foo = "bar"
                    baz = 42
                """),
            "200",
        )
    )

    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/plain

           foo = "bar"
           baz = 42
        """.rstrip())


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
            oas_fragment("""
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {"foo": "bar", "baz": 42}
        """.rstrip())


@responses.activate
def test_render_response_example_external_errored_next_example(
    testrenderer, caplog, oas_fragment
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET,
        "https://example.com/json/examples/test.json",
        status=404,
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                    fallback:
                      value: '{"spam": 42}'
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {"spam": 42}
        """.rstrip())


@responses.activate
def test_render_response_example_external_errored_next_media_type(
    testrenderer, oas_fragment, caplog
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET,
        "https://example.com/json/examples/test.json",
        status=404,
    )

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                application/json:
                  examples:
                    test:
                      externalValue: https://example.com/json/examples/test.json
                text/csv:
                  example: spam,42
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/csv

           spam,42
        """.rstrip())


def test_render_response_example_content_type(testrenderer, oas_fragment):
    """Path response's example can render something other than application/json."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip())


def test_render_response_example_noop(testrenderer, oas_fragment):
    """Path response's example is not rendered if there's nothing to render."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                application/json:
                  schema:
                    type: object
                """),
            "200",
        )
    )

    assert markup == ""


@pytest.mark.parametrize(
    ["status_code", "status_text"],
    [
        pytest.param("201", "Created", id="201"),
        pytest.param("307", "Temporary Redirect", id="307"),
        pytest.param("422", http_422_description, id="422"),
    ],
)
def test_render_response_status_code(
    testrenderer, oas_fragment, status_code, status_text
):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """),
            status_code,
        )
    )
    assert markup == textwrap.dedent(f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip())


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
            oas_fragment("""
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """),
            status_range,
        )
    )
    assert markup == textwrap.dedent(f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip())


@pytest.mark.parametrize(
    ["status_code", "status_text"],
    [
        pytest.param("201", "Created", id="201"),
        pytest.param("307", "Temporary Redirect", id="307"),
        pytest.param("422", http_422_description, id="422"),
    ],
)
def test_render_response_status_code_int(
    testrenderer, oas_fragment, status_code, status_text
):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """),
            status_code,
        )
    )
    assert markup == textwrap.dedent(f"""\
        .. sourcecode:: http

           HTTP/1.1 {status_code} {status_text}
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip())


def test_render_response_status_code_default(testrenderer, oas_fragment):
    """Path response's example is rendered when default is passed."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                text/csv:
                  example: |
                    foo,baz
                    bar,42
                """),
            "default",
        )
    )
    assert markup == textwrap.dedent(f"""\
        .. sourcecode:: http

           HTTP/1.1 000 Reason-Phrase
           Content-Type: text/csv

           foo,baz
           bar,42
        """.rstrip())


def test_render_response_example_with_date_object(testrenderer, oas_fragment):
    """Path response's example handles date objects parsed from YAML."""

    markup = textify(
        testrenderer.render_response_example(
            oas_fragment("""
                application/json:
                  example:
                    date: 2024-01-15
                """),
            "200",
        )
    )
    assert markup == textwrap.dedent("""\
        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json

           {
             "date": "2024-01-15"
           }
        """.rstrip())
