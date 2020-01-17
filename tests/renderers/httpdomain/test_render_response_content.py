"""OpenAPI spec renderer: render_response_content."""

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
            {
                "application/json": {
                    "examples": {"test": {"value": {"foo": "bar", "baz": 42}}}
                }
            },
            id="examples",
        ),
        pytest.param(
            {"application/json": {"example": {"foo": "bar", "baz": 42}}}, id="example",
        ),
        pytest.param(
            {"application/json": {"schema": {"example": {"foo": "bar", "baz": 42}}}},
            id="schema/example",
        ),
        pytest.param(
            {
                "application/json": {
                    "examples": {
                        "test": {
                            "value": textwrap.dedent(
                                """\
                                {
                                  "foo": "bar",
                                  "baz": 42
                                }
                                """
                            )
                        }
                    }
                }
            },
            id="examples::str",
        ),
        pytest.param(
            {
                "application/json": {
                    "example": textwrap.dedent(
                        """\
                        {
                          "foo": "bar",
                          "baz": 42
                        }
                        """
                    )
                }
            },
            id="example::str",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "example": textwrap.dedent(
                            """\
                            {
                              "foo": "bar",
                              "baz": 42
                            }
                            """
                        )
                    }
                }
            },
            id="schema/example::str",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {"example": {"foobar": "bazinga"}},
                    "example": {"foo": "bar", "baz": 42},
                }
            },
            id="example-beats-schema/example",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {"example": {"foobar": "bazinga"}},
                    "examples": {"test": {"value": {"foo": "bar", "baz": 42}}},
                }
            },
            id="examples-beats-schema/example",
        ),
    ],
)
def test_render_response_content_example(testrenderer, media_type):
    """Path response's example is rendered."""

    markup = textify(testrenderer.render_response_content(media_type, "200"))
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


def test_render_response_content_example_1st_from_examples(testrenderer):
    """Path response's first example is rendered."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "application/json": {
                    "examples": {
                        "foo": {"value": {"foo": "bar", "baz": 42}},
                        "bar": {"value": {"foobar": "bazinga"}},
                    }
                }
            },
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


def test_render_response_content_example_1st_from_media_type(testrenderer):
    """Path response's example from first media type is rendered."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/plain": {"example": 'foo = "bar"\nbaz = 42'},
                "application/json": {"schema": {"type": "object"}},
            },
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


def test_render_response_content_example_preference(fakestate):
    """Path response's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"response-example-preference": ["text/plain"]}
    )

    markup = textify(
        testrenderer.render_response_content(
            {
                "application/json": {"example": {"foo": "bar", "baz": 42}},
                "text/plain": {"example": 'foo = "bar"\nbaz = 42'},
            },
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


def test_render_response_content_example_preference_complex(fakestate):
    """Path response's example from preferred media type is rendered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"response-example-preference": ["application/json", "text/plain"]}
    )

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {"example": "foo,baz\nbar,42"},
                "text/plain": {"example": 'foo = "bar"\nbaz = 42'},
                "application/json": {"schema": {"type": "object"}},
            },
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
def test_render_response_content_example_external(testrenderer):
    """Path response's example can be retrieved from external location."""

    responses.add(
        responses.GET,
        "https://example.com/json/examples/test.json",
        json={"foo": "bar", "baz": 42},
        status=200,
    )

    markup = textify(
        testrenderer.render_response_content(
            {
                "application/json": {
                    "examples": {
                        "test": {
                            "externalValue": "https://example.com/json/examples/test.json"
                        }
                    }
                }
            },
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
def test_render_response_content_example_external_errored_next_example(
    testrenderer, caplog
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_response_content(
            {
                "application/json": {
                    "examples": {
                        "test": {
                            "externalValue": "https://example.com/json/examples/test.json"
                        },
                        "fallback": {"value": '{"spam": 42}'},
                    }
                }
            },
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
def test_render_response_content_example_external_errored_next_media_type(
    testrenderer, caplog
):
    """Path response's example fallbacks on next when external cannot be retrieved."""

    responses.add(
        responses.GET, "https://example.com/json/examples/test.json", status=404,
    )

    markup = textify(
        testrenderer.render_response_content(
            {
                "application/json": {
                    "examples": {
                        "test": {
                            "externalValue": "https://example.com/json/examples/test.json"
                        },
                    }
                },
                "text/csv": {"example": "spam,42"},
            },
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


def test_render_response_content_example_content_type(testrenderer):
    """Path response's example can render something other than application/json."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {
                    "example": textwrap.dedent(
                        """\
                        foo,baz
                        bar,42
                        """
                    )
                }
            },
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


def test_render_response_content_example_noop(testrenderer):
    """Path response's example is not rendered if there's nothing to render."""

    markup = textify(
        testrenderer.render_response_content(
            {"application/json": {"schema": {"type": "object"}}}, "200"
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
def test_render_response_content_status_code(testrenderer, status_code, status_text):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {
                    "example": textwrap.dedent(
                        """\
                        foo,baz
                        bar,42
                        """
                    )
                }
            },
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
def test_render_response_content_status_code_range(
    testrenderer, status_range, status_code, status_text
):
    """Path response's example is rendered with proper status range."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {
                    "example": textwrap.dedent(
                        """\
                        foo,baz
                        bar,42
                        """
                    )
                }
            },
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
        pytest.param(201, "Created", id="201"),
        pytest.param(307, "Temporary Redirect", id="307"),
        pytest.param(422, "Unprocessable Entity", id="422"),
    ],
)
def test_render_response_content_status_code_int(
    testrenderer, status_code, status_text
):
    """Path response's example is rendered with proper status code."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {
                    "example": textwrap.dedent(
                        """\
                        foo,baz
                        bar,42
                        """
                    )
                }
            },
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


def test_render_response_content_status_code_default(testrenderer):
    """Path response's example is rendered when default is passed."""

    markup = textify(
        testrenderer.render_response_content(
            {
                "text/csv": {
                    "example": textwrap.dedent(
                        """\
                        foo,baz
                        bar,42
                        """
                    )
                }
            },
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


@pytest.mark.parametrize(
    ["content", "expected"],
    [
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "string": {"type": "string"},
                            "integer": {"type": "integer"},
                            "number": {"type": "number"},
                            "array_of_numbers": {
                                "type": "array",
                                "items": {"type": "number"},
                            },
                            "array_of_strings": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "string": "string",
                 "integer": 1,
                 "number": 1.0,
                 "array_of_numbers": [
                   1.0,
                   1.0
                 ],
                 "array_of_strings": [
                   "string",
                   "string"
                 ]
               }
            """,
            id="no_examples",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "string": {"type": "string", "example": "example_string"},
                            "integer": {"type": "integer", "example": 2},
                            "number": {"type": "number", "example": 2.0},
                            "array_of_numbers": {
                                "type": "array",
                                "items": {"type": "number", "example": 3.0},
                            },
                            "array_of_strings": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "example": "example_string",
                                },
                            },
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "string": "example_string",
                 "integer": 2,
                 "number": 2.0,
                 "array_of_numbers": [
                   3.0,
                   3.0
                 ],
                 "array_of_strings": [
                   "example_string",
                   "example_string"
                 ]
               }
            """,
            id="with_examples",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "format": "date"},
                            "date-time": {"type": "string", "format": "date-time"},
                            "password": {"type": "string", "format": "password"},
                            "byte": {"type": "string", "format": "byte"},
                            "ipv4": {"type": "string", "format": "ipv4"},
                            "ipv6": {"type": "string", "format": "ipv6"},
                            "unknown": {"type": "string", "format": "unknown"},
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "date": "2020-01-01",
                 "date-time": "2020-01-01T01:01:01Z",
                 "password": "********",
                 "byte": "QG1pY2hhZWxncmFoYW1ldmFucw==",
                 "ipv4": "127.0.0.1",
                 "ipv6": "::1",
                 "unknown": "string"
               }
            """,
            id="string_formats",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "inner_object": {"type": "object"},
                            "inner_array_of_objects": {
                                "type": "array",
                                "items": {"type": "object"},
                            },
                            "inner_array_of_arrays": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "inner_object": {},
                 "inner_array_of_objects": [
                   {},
                   {}
                 ],
                 "inner_array_of_arrays": [
                   [
                     1,
                     1
                   ],
                   [
                     1,
                     1
                   ]
                 ]
               }
            """,
            id="nested",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "string_enum": {
                                "type": "string",
                                "enum": ["three", "two", "one"],
                            },
                            "integer_enum": {"type": "integer", "enum": [3, 2, 1]},
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "string_enum": "three",
                 "integer_enum": 3
               }
            """,
            id="enum",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "mixed_type_array": {
                                "type": "array",
                                "items": {"oneOf": {"string", "integer"}},
                            },
                            "any_type_array": {"type": "array", "items": {}},
                            "0_to_1_length_array": {
                                "type": "array",
                                "minItems": 0,
                                "maxItems": 1,
                                "items": {"type": "integer"},
                            },
                            "5_to_10_length_array": {
                                "type": "array",
                                "minItems": 5,
                                "maxItems": 10,
                                "items": {"type": "integer"},
                            },
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "mixed_type_array": [
                   1,
                   1
                 ],
                 "any_type_array": [
                   "string",
                   1
                 ],
                 "0_to_1_length_array": [
                   1
                 ],
                 "5_to_10_length_array": [
                   1,
                   1,
                   1,
                   1,
                   1
                 ]
               }
            """,
            id="arrays",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "oneOf": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "properties": {"one": {"type": "string"}},
                                    },
                                    {
                                        "type": "object",
                                        "properties": {"two": {"type": "string"}},
                                    },
                                ]
                            },
                            "anyOf": {
                                "anyOf": [
                                    {
                                        "type": "object",
                                        "properties": {"three": {"type": "string"}},
                                    },
                                    {
                                        "type": "object",
                                        "properties": {"four": {"type": "string"}},
                                    },
                                ]
                            },
                            "allOf": {
                                "allOf": [
                                    {
                                        "type": "object",
                                        "properties": {"five": {"type": "string"}},
                                    },
                                    {
                                        "type": "object",
                                        "properties": {"six": {"type": "string"}},
                                    },
                                ]
                            },
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "oneOf": {
                   "one": "string"
                 },
                 "anyOf": {
                   "three": "string"
                 },
                 "allOf": {
                   "five": "string",
                   "six": "string"
                 }
               }
            """,
            id="oneOf_anyOf_allOf",
        ),
        pytest.param(
            {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "anything": {"description": "this can be anything"}
                        },
                    }
                }
            },
            """\
            .. sourcecode:: http

               HTTP/1.1 000 Reason-Phrase
               Content-Type: application/json

               {
                 "anything": 1
               }
            """,
            id="any_type",
        ),
    ],
)
def test_generate_example_from_schema(fakestate, content, expected):
    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-example-from-schema": True}
    )
    markup = textify(testrenderer.render_response_content(content, "default"))
    assert markup == textwrap.dedent(expected.rstrip())
