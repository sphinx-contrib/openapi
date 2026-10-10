"""OpenAPI spec renderer: render_restructuredtext_markup."""

import copy
import textwrap

import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_oas2_minimal(testrenderer, oas_fragment):
    """Minimal OAS 2 can be rendered."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                swagger: "2.0"
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      responses:
                        '200':
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           :statuscode 200:
              a response description
        """)


def test_oas2_complete(testrenderer, oas_fragment):
    """Feature rich OAS 2 can be rendered."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                swagger: "2.0"
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      responses:
                        '200':
                          description: a response description
                  /{username}:
                    parameters:
                      - in: path
                        name: username
                        required: true
                        type: string
                    get:
                      tags:
                        - tag_a
                        - tag_b
                      summary: an operation summary
                      description: an operation description
                      externalDocs: https://docs.example.com/
                      operationId: myOperation
                      produces:
                        - application/json
                      parameters:
                        - in: header
                          name: token
                          type: string
                        - in: query
                          name: id
                          type: string
                      responses:
                        '200':
                          schema:
                            items:
                              format: int32
                              type: integer
                            type: array
                          description: a response description
                        '404':
                          description: a username not found
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           :statuscode 200:
              a response description

        .. http:get:: /{username}

           **an operation summary**

           an operation description

           :reqheader token:
           :reqheadertype token: string
           :param username:
           :paramtype username: string, required
           :queryparam id:
           :queryparamtype id: string

           :statuscode 200:
              a response description

           :statuscode 404:
              a username not found
        """)


def test_oas2_schema_example(testrenderer, oas_fragment):
    """Schema's 'example' property can be used in example snippets."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                swagger: "2.0"
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      produces:
                        - application/json
                      responses:
                        '200':
                          schema:
                            example: |
                              [
                                19,
                                84
                              ]
                            items:
                              format: int32
                              type: integer
                            type: array
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description


           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 [
                   19,
                   84
                 ]
        """)


def test_oas2_complete_generate_examples_from_schema(fakestate, oas_fragment):
    """Schema can be used to generate example snippets."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                swagger: "2.0"
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      produces:
                        - application/json
                      responses:
                        '200':
                          schema:
                            items:
                              format: int32
                              type: integer
                            type: array
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description


           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 [
                   1,
                   1
                 ]
        """)


def test_oas3_minimal(testrenderer, oas_fragment):
    """Minimal OAS 3 can be rendered."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      responses:
                        '200':
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           :statuscode 200:
              a response description
        """)


def test_oas3_complete(testrenderer, oas_fragment):
    """Feature rich OAS 3 can be rendered."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      responses:
                        '200':
                          description: a response description
                  /{username}:
                    parameters:
                      - in: path
                        name: username
                        schema:
                          type: string
                        required: true
                    get:
                      tags:
                        - tag_a
                        - tag_b
                      summary: an operation summary
                      description: an operation description
                      externalDocs: https://docs.example.com/
                      operationId: myOperation
                      parameters:
                        - in: header
                          name: token
                          schema:
                            type: string
                        - in: query
                          name: id
                          schema:
                            type: string
                      responses:
                        '200':
                          content:
                            application/json:
                              schema:
                                items:
                                  format: int32
                                  type: integer
                                type: array
                          description: a response description
                        '404':
                          description: a username not found
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           :statuscode 200:
              a response description

        .. http:get:: /{username}

           **an operation summary**

           an operation description

           :reqheader token:
           :reqheadertype token: string
           :param username:
           :paramtype username: string, required
           :queryparam id:
           :queryparamtype id: string

           :statuscode 200:
              a response description

           :statuscode 404:
              a username not found
        """)


def test_oas3_schema_example(testrenderer, oas_fragment):
    """Schema's 'example' property can be used in example snippets."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      responses:
                        '200':
                          content:
                            application/json:
                              schema:
                                example: |
                                  [
                                    19,
                                    84
                                  ]
                                items:
                                  format: int32
                                  type: integer
                                type: array
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description


           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 [
                   19,
                   84
                 ]
        """)


def test_oas3_generate_examples_from_schema(fakestate, oas_fragment):
    """Schema can be used to generate example snippets."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      responses:
                        '200':
                          content:
                            application/json:
                              schema:
                                items:
                                  format: int32
                                  type: integer
                                type: array
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description


           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 [
                   1,
                   1
                 ]
        """)


@pytest.mark.parametrize("version", ["3.0.3", "3.1.0"])
@pytest.mark.parametrize("combining_keyword", ["oneOf", "anyOf"])
def test_oas3_generate_array_item_examples(fakestate, version, combining_keyword):
    """Generated request and response arrays preserve explicit item examples."""

    content = {
        "application/json": {
            "schema": {
                "type": "array",
                "items": {
                    "example": 42,
                    combining_keyword: [{"type": "integer"}, {"type": "string"}],
                },
            }
        }
    }
    spec = make_spec(
        version,
        {
            "post": {
                "requestBody": {"content": copy.deepcopy(content)},
                "responses": {
                    "200": {
                        "description": "A response.",
                        "content": copy.deepcopy(content),
                    }
                },
            }
        },
    )
    renderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(renderer.render_restructuredtext_markup(spec))
    assert "POST /resources HTTP/1.1" in markup
    assert "HTTP/1.1 200 OK" in markup
    assert [
        line.strip() for line in markup.splitlines() if line.strip() in {"42,", "42"}
    ] == ["42,", "42", "42,", "42"]


def test_oas3_generate_examples_from_schema_with_composed_property(
    fakestate, oas_fragment
):
    """Schema of a property composed with 'allOf' can be used to generate an example."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      responses:
                        '200':
                          content:
                            application/json:
                              schema:
                                type: object
                                properties:
                                  status:
                                    description: a property description
                                    allOf:
                                      - type: string
                                        enum:
                                          - PENDING
                                          - RUNNING
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description

           :resjson status:
              a property description
           :resjsonobj status: string:enum

           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 {
                   "status": "PENDING"
                 }
        """)


def test_oas3_request_body(testrenderer, oas_fragment):
    """Request body example is rendered."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      requestBody:
                        content:
                          application/json:
                            examples:
                              test:
                                value:
                                  foo: bar
                                  baz: 42
                      responses:
                        '200':
                          description: a response description
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description

           .. sourcecode:: http

              GET /test HTTP/1.1
              Content-Type: application/json

              {
                "foo": "bar",
                "baz": 42
              }

           :statuscode 200:
              a response description
        """)


def test_oas3_response_example_2xx(testrenderer, oas_fragment):
    """Response examples are rendered for 2XX status codes."""

    markup = textify(testrenderer.render_restructuredtext_markup(oas_fragment("""
                openapi: 3.0.3
                info:
                  title: An example spec
                  version: 1.0
                paths:
                  /test:
                    get:
                      description: an operation description
                      responses:
                        '200':
                          content:
                            application/json:
                              example: |
                                [
                                  19,
                                  84
                                ]
                          description: a response description
                        '404':
                          content:
                            application/json:
                              example: |
                                {
                                  "message": "an error message"
                                }
                          description: resource not found
                """)))
    assert markup == textwrap.dedent("""\
        .. http:get:: /test

           an operation description

           :statuscode 200:
              a response description

              .. sourcecode:: http

                 HTTP/1.1 200 OK
                 Content-Type: application/json

                 [
                   19,
                   84
                 ]
           :statuscode 404:
              resource not found
        """)


@pytest.mark.parametrize("version", ["3.0.3", "3.1.0"])
@pytest.mark.parametrize("provided_example", [False, True])
@pytest.mark.parametrize(
    "options, generate, render_examples, response_codes",
    [
        ({}, False, True, ["200"]),
        ({"examples": True}, True, True, ["200", "400", "000"]),
        ({"examples": False}, False, False, []),
        ({"generate-examples-from-schemas": True}, True, True, ["200"]),
        (
            {"examples": True, "generate-examples-from-schemas": False},
            False,
            True,
            ["200", "400", "000"],
        ),
        ({"examples": False, "generate-examples-from-schemas": True}, True, False, []),
        ({"examples": True, "response-examples-for": "400"}, True, True, ["400"]),
        ({"examples": True, "response-examples-for": []}, True, True, []),
    ],
)
def test_legacy_examples(
    fakestate,
    version,
    provided_example,
    options,
    generate,
    render_examples,
    response_codes,
):
    """Legacy example flags control generation and rendering of both bodies."""

    content = {
        "application/json": {
            "schema": {"type": "object", "properties": {"name": {"type": "string"}}}
        }
    }
    if provided_example:
        content["application/json"]["example"] = {"name": "A supplied example"}
    spec = make_spec(
        version,
        {
            "post": {
                "requestBody": {"content": copy.deepcopy(content)},
                "responses": {
                    status: {
                        "description": "A response.",
                        "content": copy.deepcopy(content),
                    }
                    for status in ["200", "400", "default"]
                },
            }
        },
    )
    renderer = renderers.HttpdomainRenderer(fakestate, options)
    markup = textify(renderer.render_restructuredtext_markup(spec))
    examples_expected = render_examples and (provided_example or generate)
    assert ("POST /resources HTTP/1.1" in markup) == examples_expected
    expected_codes = response_codes if examples_expected else []
    assert [
        line.split()[1]
        for line in markup.splitlines()
        if line.strip().startswith("HTTP/1.1")
    ] == expected_codes
    assert markup.count(".. sourcecode:: http") == (
        1 + len(expected_codes) if examples_expected else 0
    )
    # Disabling examples must not suppress schema descriptions.
    assert ":reqjson name:" in markup
    assert ":resjson name:" in markup
    if examples_expected:
        expected_value = "A supplied example" if provided_example else "string"
        assert f'"name": "{expected_value}"' in markup


@pytest.mark.parametrize(
    "options, request_hints, response_hints",
    [
        ({}, True, True),
        ({"request": True}, True, True),
        ({"request": False}, False, True),
        ({"no-json-schema-description": True}, False, False),
        ({"no-json-schema-description": False}, True, True),
        ({"request": True, "no-json-schema-description": True}, False, False),
        ({"request": False, "no-json-schema-description": False}, False, True),
    ],
)
def test_legacy_request(fakestate, options, request_hints, response_hints):
    """The request flag controls request hints independently of examples."""

    content = {
        "application/json": {
            "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
            "example": {"name": "A supplied example"},
        }
    }
    spec = make_spec(
        "3.0.3",
        {
            "post": {
                "requestBody": {"content": copy.deepcopy(content)},
                "responses": {
                    "200": {
                        "description": "A response.",
                        "content": copy.deepcopy(content),
                    }
                },
            }
        },
    )
    renderer = renderers.HttpdomainRenderer(fakestate, options)
    markup = textify(renderer.render_restructuredtext_markup(spec))
    assert (":reqjson name:" in markup) == request_hints
    assert (":resjson name:" in markup) == response_hints
    assert "POST /resources HTTP/1.1" in markup
    assert "HTTP/1.1 200 OK" in markup


def make_spec(version, path, endpoint="/resources"):
    spec = {
        "info": {"title": "An example API", "version": "1.0"},
        "paths": {endpoint: path},
    }
    spec["swagger" if version == "2.0" else "openapi"] = version
    return spec


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize("version", ["3.0.3", "3.1.0"])
@pytest.mark.parametrize(
    "metadata",
    [
        {"summary": "A path summary"},
        {"description": "A path description"},
        {"servers": [{"url": "https://example.com"}]},
        {"x-codegen-name": "customName"},
        {"x-amazon-apigateway-any-method": {"some": "config"}},
    ],
)
def test_path_metadata(fakestate, version, group, metadata):
    """Path metadata is not normalized or rendered as an operation."""

    path = {
        **metadata,
        "get": {"responses": {"200": {"description": "A response."}}},
    }
    original_metadata = copy.deepcopy(metadata)
    renderer = renderers.HttpdomainRenderer(fakestate, {"group": group})
    markup = "\n".join(
        renderer.render_restructuredtext_markup(make_spec(version, path))
    )
    assert {key: path[key] for key in metadata} == original_metadata
    expected = textwrap.dedent("""\
        .. http:get:: /resources

           :statuscode 200:
              A response.
        """)
    if group:
        expected = "default\n=======\n\n" + expected
    assert markup == expected


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize("version", ["2.0", "3.0.3", "3.1.0"])
def test_parameter_overrides(fakestate, version, group):
    """Operations override parameters by both name and location."""

    def parameter(name, location, schema_type, description):
        result = {"name": name, "in": location, "description": description}
        schema = {"type": schema_type}
        if version == "2.0":
            result.update(schema)
        else:
            result["schema"] = schema
        if location == "path":
            result["required"] = True
        return result

    path = {
        "parameters": [
            parameter("id", "path", "string", "An inherited path parameter."),
            parameter("q", "query", "string", "An inherited query parameter."),
            parameter("q", "header", "string", "An inherited header parameter."),
        ],
        "get": {
            "parameters": [
                parameter("q", "query", "integer", "An overridden query parameter.")
            ],
            "responses": {"200": {"description": "A response."}},
        },
        "post": {"responses": {"201": {"description": "Another response."}}},
    }
    spec = make_spec(version, path, endpoint="/resources/{id}")
    # Exercise reference resolution before parameter identity is inspected.
    shared = path["parameters"][1]
    if version == "2.0":
        spec["parameters"] = {"query": shared}
        path["parameters"][1] = {"$ref": "#/parameters/query"}
    else:
        spec["components"] = {"parameters": {"query": shared}}
        path["parameters"][1] = {"$ref": "#/components/parameters/query"}

    renderer = renderers.HttpdomainRenderer(fakestate, {"group": group})
    markup = "\n".join(renderer.render_restructuredtext_markup(spec))
    get_markup, post_markup = markup.split(".. http:post::")
    for operation_markup in (get_markup, post_markup):
        assert operation_markup.count(":param id:") == 1
        assert ":paramtype id: string, required" in operation_markup
        assert operation_markup.count(":reqheader q:") == 1
        assert "An inherited header parameter." in operation_markup
        assert operation_markup.count(":queryparam q:") == 1
    assert ":queryparamtype q: integer" in get_markup
    assert "An overridden query parameter." in get_markup
    assert "An inherited query parameter." not in get_markup
    assert ":queryparamtype q: string" in post_markup
    assert "An inherited query parameter." in post_markup
    assert "An overridden query parameter." not in post_markup
    # Reusing a spec must not accumulate inherited parameters.
    assert "\n".join(renderer.render_restructuredtext_markup(spec)) == markup


@pytest.mark.parametrize("group", [False, True])
def test_oas2_inherited_request_body(fakestate, group):
    """Swagger body parameters must be inherited before conversion to OAS 3."""

    spec = make_spec(
        "2.0",
        {
            "x-codegen-name": "customName",
            "parameters": [
                {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "example": {"name": "An inherited body"},
                    },
                }
            ],
            "post": {"responses": {"201": {"description": "A response."}}},
        },
    )
    spec["consumes"] = ["application/json"]
    renderer = renderers.HttpdomainRenderer(fakestate, {"group": group})
    markup = "\n".join(renderer.render_restructuredtext_markup(copy.deepcopy(spec)))
    assert "POST /resources HTTP/1.1" in markup
    assert '"name": "An inherited body"' in markup
    assert ":statuscode 201:" in markup
