"""OpenAPI spec renderer: render_restructuredtext_markup."""

import textwrap

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_oas2_minimal(testrenderer, oas_fragment):
    """Minimal OAS 2 can be rendered."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:get:: /test

           :statuscode 200:
              a response description
        """
    )


def test_oas2_complete(testrenderer, oas_fragment):
    """Feature rich OAS 2 can be rendered."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas2_schema_example(testrenderer, oas_fragment):
    """Schema's 'example' property can be used in example snippets."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas2_complete_generate_examples_from_schema(fakestate, oas_fragment):
    """Schema can be used to generate example snippets."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas3_minimal(testrenderer, oas_fragment):
    """Minimal OAS 3 can be rendered."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:get:: /test

           :statuscode 200:
              a response description
        """
    )


def test_oas3_complete(testrenderer, oas_fragment):
    """Feature rich OAS 3 can be rendered."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas3_schema_example(testrenderer, oas_fragment):
    """Schema's 'example' property can be used in example snippets."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas3_generate_examples_from_schema(fakestate, oas_fragment):
    """Schema can be used to generate example snippets."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"generate-examples-from-schemas": True}
    )
    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas3_request_body(testrenderer, oas_fragment):
    """Request body example is rendered."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )


def test_oas3_response_example_2xx(testrenderer, oas_fragment):
    """Response examples are rendered for 2XX status codes."""

    markup = textify(
        testrenderer.render_restructuredtext_markup(
            oas_fragment(
                """
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
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
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
        """
    )
