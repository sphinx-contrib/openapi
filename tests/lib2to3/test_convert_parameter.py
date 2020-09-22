""".convert_parameter() test suite."""

import pytest

import sphinxcontrib.openapi._lib2to3 as lib2to3


@pytest.fixture(scope="function")
def convert_parameter(oas_fragment):
    def _wrapper(parameter):
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
        oas2["paths"]["/test"]["get"]["parameters"] = [parameter]

        oas3 = lib2to3.convert(oas2)
        return oas3["paths"]["/test"]["get"]["parameters"][0]

    return _wrapper


def test_in_header_complete(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            description: token to be passed as a header
            in: header
            items:
              format: int64
              type: integer
            name: token
            required: true
            type: array
            """
        )
    )
    assert converted == oas_fragment(
        """
        description: token to be passed as a header
        in: header
        name: token
        required: true
        schema:
          items:
            format: int64
            type: integer
          type: array
        """
    )


def test_in_path_complete(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            description: username to fetch
            in: path
            name: username
            required: true
            type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        description: username to fetch
        in: path
        name: username
        required: true
        schema:
          type: string
        """
    )


def test_in_query_complete(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            description: ID of the object to fetch
            in: query
            items:
              type: string
            name: id
            required: false
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        description: ID of the object to fetch
        in: query
        name: id
        required: false
        schema:
          items:
            type: string
          type: array
        """
    )


def test_in_header_minimal(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: header
            name: token
            type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: header
        name: token
        schema:
          type: string
        """
    )


def test_in_path_minimal(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: path
            name: username
            required: true
            type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: path
        name: username
        required: true
        schema:
          type: string
        """
    )


def test_in_query_minimal(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: query
            name: id
            type: string
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: query
        name: id
        schema:
          type: string
        """
    )


def test_collectionFormat_is_csv_path(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: csv
            in: path
            items:
              type: string
            name: username
            required: true
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: path
        name: username
        required: true
        schema:
          items:
            type: string
          type: array
        style: simple
        """
    )


def test_collectionFormat_is_csv_header(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: csv
            in: header
            items:
              type: string
            name: username
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: header
        name: username
        schema:
          items:
            type: string
          type: array
        style: simple
        """
    )


def test_collectionFormat_is_csv(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: csv
            in: query
            items:
              type: string
            name: id
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        explode: false
        in: query
        name: id
        schema:
          items:
            type: string
          type: array
        style: form
        """
    )


def test_collectionFormat_is_multi(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: multi
            in: query
            items:
              type: string
            name: id
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        explode: true
        in: query
        name: id
        schema:
          items:
            type: string
          type: array
        style: form
        """
    )


def test_collectionFormat_is_ssv(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: ssv
            in: query
            items:
              type: string
            name: id
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: query
        name: id
        schema:
          items:
            type: string
          type: array
        style: spaceDelimited
        """
    )


def test_collectionFormat_is_pipes(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: pipes
            in: query
            items:
              type: string
            name: id
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: query
        name: id
        schema:
          items:
            type: string
          type: array
        style: pipeDelimited
        """
    )


def test_collectionFormat_is_tsv(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            collectionFormat: tsv
            in: query
            items:
              type: string
            name: id
            type: array
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: query
        name: id
        schema:
          items:
            type: string
          type: array
        """
    )


def test_in_header_vendor_extensions(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: header
            name: token
            type: string
            x-vendor-ext: vendor-ext
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: header
        name: token
        schema:
          type: string
        x-vendor-ext: vendor-ext
        """
    )


def test_in_path_vendor_extensions(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: path
            name: username
            required: true
            type: string
            x-vendor-ext: vendor-ext
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: path
        name: username
        required: true
        schema:
          type: string
        x-vendor-ext: vendor-ext
        """
    )


def test_in_query_vendor_extensions(convert_parameter, oas_fragment):
    converted = convert_parameter(
        oas_fragment(
            """
            in: query
            name: id
            type: string
            x-vendor-ext: vendor-ext
            """
        ),
    )
    assert converted == oas_fragment(
        """
        in: query
        name: id
        schema:
          type: string
        x-vendor-ext: vendor-ext
        """
    )
