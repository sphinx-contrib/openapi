""".convert_operation() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_operation(oas_fragment):
    def _wrapper(operation):
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
        oas2["paths"]["/test"]["get"] = operation

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"]

    return _wrapper


def test_minimal(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
            responses:
              '200':
                description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        responses:
          '200':
            description: a response description
        """
    )


def test_complete(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
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
              - in: path
                name: username
                required: true
                type: string
              - in: query
                name: id
                type: string
            deprecated: false
            responses:
              '200':
                description: a response description
                schema:
                  items:
                    format: int32
                    type: integer
                  type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
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
          - in: path
            name: username
            required: true
            schema:
              type: string
          - in: query
            name: id
            schema:
              type: string
        deprecated: false
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


def test_request_body(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
            description: an operation description
            consumes:
              - application/json
            parameters:
              - in: path
                name: username
                required: true
                type: string
              - in: body
                name: inventory
                schema:
                  type: object
                  properties:
                    t-shirt:
                      type: boolean
                required: true
            responses:
              '200':
                description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        description: an operation description
        parameters:
          - in: path
            name: username
            required: true
            schema:
              type: string
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  t-shirt:
                    type: boolean
          required: true
        responses:
          '200':
             description: a response description
        """
    )


def test_request_body_formdata(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
            description: an operation description
            consumes:
              - application/x-www-form-urlencoded
            parameters:
              - in: path
                name: username
                required: true
                type: string
              - in: formData
                name: t-shirt
                type: boolean
            responses:
              '200':
                description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        description: an operation description
        parameters:
          - in: path
            name: username
            required: true
            schema:
              type: string
        requestBody:
          content:
            application/x-www-form-urlencoded:
              schema:
                type: object
                properties:
                  t-shirt:
                    type: boolean
        responses:
          '200':
             description: a response description
        """
    )


def test_only_request_body(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
            description: an operation description
            consumes:
              - application/json
            parameters:
              - in: body
                name: inventory
                schema:
                  type: object
                  properties:
                    t-shirt:
                      type: boolean
                required: true
            responses:
              '200':
                description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        description: an operation description
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  t-shirt:
                    type: boolean
          required: true
        responses:
          '200':
             description: a response description
        """
    )


def test_vendor_extensions(convert_operation, oas_fragment):
    converted = convert_operation(
        oas_fragment(
            """
            responses:
              '200':
                description: a response description
            x-vendor-ext: vendor-ext
            """
        ),
    )
    assert converted == oas_fragment(
        """
        responses:
          '200':
            description: a response description
        x-vendor-ext: vendor-ext
        """
    )
