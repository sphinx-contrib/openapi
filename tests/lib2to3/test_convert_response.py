""".convert_response() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_response(oas_fragment):
    def _wrapper(response, produces):
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
        oas2["paths"]["/test"]["get"]["responses"]["200"] = response
        oas2["paths"]["/test"]["get"]["produces"] = produces

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"]["responses"]["200"]

    return _wrapper


def test_minimal(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        description: a response description
        """
    )


def test_schema(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
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


def test_schema_mimetypes(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            schema:
              items:
                format: int32
                type: integer
              type: array
            """
        ),
        produces=["application/json", "text/plain"],
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            schema:
              items:
                format: int32
                type: integer
              type: array
          text/plain:
            schema:
              items:
                format: int32
                type: integer
              type: array
        description: a response description
        """
    )


def test_schema_no_mimetypes(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            schema:
              items:
                format: int32
                type: integer
              type: array
            """
        ),
        produces=None,
    )
    assert converted == oas_fragment(
        """
        content:
          '*/*':
            schema:
              items:
                format: int32
                type: integer
              type: array
        description: a response description
        """
    )


def test_examples(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            examples:
              application/json:
                something: important
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            example:
              something: important
        description: a response description
        """
    )


def test_examples_any_type(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            examples:
              application/json: '{"something": "important"}'
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            example: '{"something": "important"}'
        description: a response description
        """
    )


def test_examples_mimetypes(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            examples:
              application/json:
                something: important
              text/plain: something=imporant
            """
        ),
        produces=["application/json", "text/plain"],
    )
    assert converted == oas_fragment(
        """
        content:
          application/json:
            example:
              something: important
          text/plain:
            example: something=imporant
        description: a response description
        """
    )


def test_headers_schema_only(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            headers:
              X-Test:
                type: string
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        description: a response description
        headers:
          X-Test:
            schema:
              type: string
        """
    )


def test_headers_schema_extra(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            headers:
              X-Test:
                description: Is it a test?
                type: string
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        description: a response description
        headers:
          X-Test:
            description: Is it a test?
            schema:
              type: string
        """
    )


def test_headers_multiple(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            headers:
              X-Bar:
                format: int32
                type: integer
              X-Foo:
                type: string
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
        description: a response description
        headers:
          X-Bar:
            schema:
              format: int32
              type: integer
          X-Foo:
            schema:
              type: string
        """
    )


def test_schema_examples_headers(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
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


def test_complete(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
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


def test_vendor_extensions(convert_response, oas_fragment):
    converted = convert_response(
        oas_fragment(
            """
            description: a response description
            examples:
              application/json:
                something: important
            headers:
              X-Test:
                description: Is it a test?
                type: string
                x-header-ext: header-ext
            schema:
              items:
                format: int32
                type: integer
              type: array
              x-schema-ext: schema-ext
            x-response-ext: response-ext
            """
        ),
        produces=["application/json"],
    )
    assert converted == oas_fragment(
        """
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
              x-schema-ext: schema-ext
        headers:
          X-Test:
            description: Is it a test?
            schema:
              type: string
            x-header-ext: header-ext
        x-response-ext: response-ext
        """
    )
