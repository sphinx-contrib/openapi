""".convert_request_body() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


_MISSING = object()


@pytest.fixture(scope="function")
def convert_request_body(oas_fragment):
    def _wrapper(operation_fragment):
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
        oas2["paths"]["/test"]["get"].update(operation_fragment)

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"].get("requestBody", _MISSING)

    return _wrapper


def test_minimal(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/json
            parameters:
              - in: body
                name: user
                schema:
                  $ref: '#/definitions/User'
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            schema:
              $ref: '#/definitions/User'
        """
    )


def test_complete(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/json
            parameters:
              - description: user to add to the system
                in: body
                name: user
                required: true
                schema:
                  $ref: '#/definitions/User'
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            schema:
              $ref: '#/definitions/User'
        description: user to add to the system
        required: true
        """
    )


def test_no_consumes(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - in: body
                name: user
                schema:
                  $ref: '#/definitions/User'
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          '*/*':
            schema:
              $ref: '#/definitions/User'
        """
    )


def test_header_path_query_are_ignored(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
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
            """
        ),
    )
    assert converted is _MISSING


def test_body_and_others(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - in: header
                name: token
                type: string
              - in: path
                name: username
                required: true
                type: string
              - in: body
                name: user
                schema:
                  $ref: '#/definitions/User'
              - in: query
                name: id
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          '*/*':
            schema:
              $ref: '#/definitions/User'
        """
    )
