""".convert_paths() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_paths(oas_fragment):
    def _wrapper(paths):
        oas2 = oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: "1.0"
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        )
        oas2["paths"] = paths

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]

    return _wrapper


def test_minimal(convert_paths, oas_fragment):
    converted = convert_paths(
        oas_fragment(
            """
            /test:
              get:
                responses:
                  '200':
                    description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        /test:
          get:
            responses:
              '200':
                description: a response description
        """
    )


def test_complete(convert_paths, oas_fragment):
    pass
    converted = convert_paths(
        oas_fragment(
            """
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
            """
        ),
    )
    assert converted == oas_fragment(
        """
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
        """
    )


def test_multiple(convert_paths, oas_fragment):
    converted = convert_paths(
        oas_fragment(
            """
            /test:
              get:
                responses:
                  '200':
                    description: a test response description
            /eggs:
              post:
                responses:
                  '201':
                    description: an eggs response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        /test:
          get:
            responses:
              '200':
                description: a test response description
        /eggs:
          post:
            responses:
              '201':
                description: an eggs response description
        """
    )


def test_vendor_extensions(convert_paths, oas_fragment):
    converted = convert_paths(
        oas_fragment(
            """
            /test:
              get:
                responses:
                  '200':
                    description: a response description
            x-vendor-ext: vendor-ext
            """
        ),
    )
    assert converted == oas_fragment(
        """
        /test:
          get:
            responses:
              '200':
                description: a response description
        x-vendor-ext: vendor-ext
        """
    )
