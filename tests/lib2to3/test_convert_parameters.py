""".convert_parameters() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


_MISSING = object()


@pytest.fixture(scope="function")
def convert_parameters(oas_fragment):
    def _wrapper(parameters):
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
        oas2["paths"]["/test"]["get"]["parameters"] = parameters

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"].get("parameters", _MISSING)

    return _wrapper


def test_header_path_query(convert_parameters, oas_fragment):
    converted = convert_parameters(
        oas_fragment(
            """
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
    assert converted == oas_fragment(
        """
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
        """
    )


def test_body_is_ignored(convert_parameters, oas_fragment):
    converted = convert_parameters(
        oas_fragment(
            """
            - description: user to add to the system
              in: body
              name: user
              required: true
              schema:
                $ref: '#/definitions/User'
            """
        ),
    )
    assert converted is _MISSING


def test_formData_is_ignored(convert_parameters, oas_fragment):
    converted = convert_parameters(
        oas_fragment(
            """
            - description: The avatar of the user
              in: formData
              name: avatar
              type: file
            """
        ),
    )

    assert converted is _MISSING
