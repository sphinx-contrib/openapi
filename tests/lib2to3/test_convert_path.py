""".convert_path() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_path(oas_fragment):
    def _wrapper(path):
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
        oas2["paths"]["/test"] = path

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]

    return _wrapper


@pytest.mark.parametrize(
    "method", ["get", "put", "post", "delete", "options", "head", "patch"]
)
def test_minimal(convert_path, oas_fragment, method):
    converted = convert_path(
        oas_fragment(
            f"""
            {method}:
              responses:
                '200':
                  description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        f"""
        {method}:
          responses:
            '200':
              description: a response description
        """
    )


def test_complete(convert_path, oas_fragment):
    converted = convert_path(
        oas_fragment(
            """
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


def test_shared_parameters(convert_path, oas_fragment):
    converted = convert_path(
        oas_fragment(
            """
            parameters:
              - in: path
                name: username
                required: true
                type: string
            get:
              parameters:
                - in: header
                  name: token
                  type: string
                - in: query
                  name: id
                  type: string
              responses:
                '200':
                  description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        parameters:
          - in: path
            name: username
            schema:
              type: string
            required: true
        get:
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
              description: a response description
        """
    )


def test_multiple(convert_path, oas_fragment):
    converted = convert_path(
        oas_fragment(
            """
            post:
              responses:
                '201':
                  description: a post response description
            get:
              responses:
                '200':
                  description: a get response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        post:
          responses:
            '201':
              description: a post response description
        get:
          responses:
            '200':
              description: a get response description
        """
    )


def test_vendor_extensions(convert_path, oas_fragment):
    converted = convert_path(
        oas_fragment(
            """
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
        get:
          responses:
            '200':
              description: a response description
        x-vendor-ext: vendor-ext
        """
    )
