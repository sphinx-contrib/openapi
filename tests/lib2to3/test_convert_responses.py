""".convert_responses() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_responses(oas_fragment):
    def _wrapper(responses, produces):
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
        oas2["paths"]["/test"]["get"]["responses"] = responses
        oas2["paths"]["/test"]["get"]["produces"] = produces

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"]["responses"]

    return _wrapper


def test_minimal(convert_responses, oas_fragment):
    converted = convert_responses(
        oas_fragment(
            """
            '200':
              description: a response description
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        '200':
          description: a response description
        """
    )


def test_complete(convert_responses, oas_fragment):
    converted = convert_responses(
        oas_fragment(
            """
            '200':
              description: a response description
              examples:
                application/json:
                  something: important
              headers:
                X-Test:
                  description: Is it a test?
                  type: string
              schema:
                items:
                  format: int32
                  type: integer
                type: array
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        '200':
          description: a response description
          content:
            application/json:
              example:
                something: important
              schema:
                items:
                  format: int32
                  type: integer
                type: array
          headers:
            X-Test:
              description: Is it a test?
              schema:
                type: string
        """
    )


def test_multiple(convert_responses, oas_fragment):
    converted = convert_responses(
        oas_fragment(
            """
            '200':
              description: OK
              schema:
                items:
                  format: int32
                  type: integer
                type: array
            '400':
              description: Bad Request
              headers:
                X-Test:
                  description: Is it a test?
                  type: string
            default:
              description: Internal Server Error
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        '200':
          content:
            application/json:
              schema:
                items:
                  format: int32
                  type: integer
                type: array
          description: OK
        '400':
          description: Bad Request
          headers:
            X-Test:
              description: Is it a test?
              schema:
                type: string
        default:
          description: Internal Server Error
        """
    )


def test_vendor_extensions(convert_responses, oas_fragment):
    converted = convert_responses(
        oas_fragment(
            """
            '200':
              description: a response description
            x-vendor-ext: vendor-ext
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        '200':
          description: a response description
        x-vendor-ext: vendor-ext
        """
    )
