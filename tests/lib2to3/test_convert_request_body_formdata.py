""".convert_request_body() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


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
        return oas3["paths"]["/test"]["get"]["requestBody"]

    return _wrapper


def test_minimal(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                user:
                  type: string
              type: object
        """
    )


def test_complete(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
                required: true
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                user:
                  description: a name of the user
                  type: string
              required: [user]
        """
    )


def test_complex_schema(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - format: int32
                in: formData
                maximum: 100
                minimum: 5
                name: age
                type: integer
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                age:
                  format: int32
                  maximum: 100
                  minimum: 5
                  type: integer
              type: object
        """
    )


def test_consumes_urlencoded(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/x-www-form-urlencoded
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )


def test_consumes_form_data(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - multipart/form-data
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          multipart/form-data:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )


def test_consumes_urlencoded_and_form_data(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/x-www-form-urlencoded
              - multipart/form-data
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
          multipart/form-data:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )


def test_required(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - description: a name of the user
                in: formData
                name: user
                required: true
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              required:
                - user
              type: object
        """
    )


def test_multiple(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
              - description: a status of the user
                in: formData
                name: status
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                status:
                  description: a status of the user
                  type: string
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )


def test_type_file_implicit_form_data(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            parameters:
              - description: a user pic
                in: formData
                name: userpic
                type: file
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          multipart/form-data:
            schema:
              properties:
                userpic:
                  description: a user pic
                  type: file
              type: object
        """
    )


def test_type_file_consumes_form_data(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - multipart/form-data
            parameters:
              - description: a user pic
                in: formData
                name: userpic
                type: file
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          multipart/form-data:
            schema:
              properties:
                userpic:
                  description: a user pic
                  type: file
              type: object
        """
    )


def test_consumes_json_and_urlencoded(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/json
              - application/x-www-form-urlencoded
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          application/x-www-form-urlencoded:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )


def test_consumes_json_and_form_data(convert_request_body, oas_fragment):
    converted = convert_request_body(
        oas_fragment(
            """
            consumes:
              - application/json
              - multipart/form-data
            parameters:
              - description: a name of the user
                in: formData
                name: user
                type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        content:
          multipart/form-data:
            schema:
              properties:
                user:
                  description: a name of the user
                  type: string
              type: object
        """
    )
