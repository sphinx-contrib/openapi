import pytest

from sphinxcontrib.openapi.schema_utils import example_from_schema


@pytest.mark.parametrize(
    ["schema", "expected"],
    [
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "string": {"type": "string"},
                    "integer": {"type": "integer"},
                    "number": {"type": "number"},
                    "array_of_numbers": {"type": "array", "items": {"type": "number"}},
                    "array_of_strings": {"type": "array", "items": {"type": "string"}},
                },
            },
            {
                "string": "string",
                "integer": 1,
                "number": 1.0,
                "array_of_numbers": [1.0, 1.0],
                "array_of_strings": ["string", "string"],
            },
            id="no_examples",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "string": {"type": "string", "example": "example_string"},
                    "integer": {"type": "integer", "example": 2},
                    "number": {"type": "number", "example": 2.0},
                    "array_of_numbers": {
                        "type": "array",
                        "items": {"type": "number", "example": 3.0},
                    },
                    "array_of_strings": {
                        "type": "array",
                        "items": {"type": "string", "example": "example_string"},
                    },
                },
            },
            {
                "string": "example_string",
                "integer": 2,
                "number": 2.0,
                "array_of_numbers": [3.0, 3.0],
                "array_of_strings": ["example_string", "example_string"],
            },
            id="with_examples",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "string": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "date-time": {"type": "string", "format": "date-time"},
                    "password": {"type": "string", "format": "password"},
                    "byte": {"type": "string", "format": "byte"},
                    "ipv4": {"type": "string", "format": "ipv4"},
                    "ipv6": {"type": "string", "format": "ipv6"},
                    "unknown": {"type": "string", "format": "unknown"},
                    "max": {"type": "string", "maxLength": 3},
                    "min": {"type": "string", "minLength": 10},
                    "max_min_big": {"type": "string", "maxLength": 15, "minLength": 10},
                    "max_min_small": {"type": "string", "maxLength": 3, "minLength": 1},
                },
            },
            {
                "string": "string",
                "date": "2020-01-01",
                "date-time": "2020-01-01T01:01:01Z",
                "password": "********",
                "byte": "QG1pY2hhZWxncmFoYW1ldmFucw==",
                "ipv4": "127.0.0.1",
                "ipv6": "::1",
                "unknown": "string",
                "max": "str",
                "min": "stringstri",
                "max_min_big": "stringstri",
                "max_min_small": "str",
            },
            id="strings",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "inner_object": {"type": "object"},
                    "inner_array_of_objects": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "inner_array_of_arrays": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}},
                    },
                },
            },
            {
                "inner_object": {},
                "inner_array_of_objects": [{}, {}],
                "inner_array_of_arrays": [[1, 1], [1, 1]],
            },
            id="nested",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "string_enum": {"type": "string", "enum": ["three", "two", "one"]},
                    "integer_enum": {"type": "integer", "enum": [3, 2, 1]},
                },
            },
            {"string_enum": "three", "integer_enum": 3},
            id="enum",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "mixed_type_array": {
                        "type": "array",
                        "items": {"oneOf": {"string", "integer"}},
                    },
                    "any_type_array": {"type": "array", "items": {}},
                    "0_to_1_length_array": {
                        "type": "array",
                        "minItems": 0,
                        "maxItems": 1,
                        "items": {"type": "integer"},
                    },
                    "5_to_10_length_array": {
                        "type": "array",
                        "minItems": 5,
                        "maxItems": 10,
                        "items": {"type": "integer"},
                    },
                },
            },
            {
                "mixed_type_array": [1, 1],
                "any_type_array": ["string", 1],
                "0_to_1_length_array": [1],
                "5_to_10_length_array": [1, 1, 1, 1, 1],
            },
            id="arrays",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "oneOf": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {"one": {"type": "string"}},
                            },
                            {
                                "type": "object",
                                "properties": {"two": {"type": "string"}},
                            },
                        ]
                    },
                    "anyOf": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {"three": {"type": "string"}},
                            },
                            {
                                "type": "object",
                                "properties": {"four": {"type": "string"}},
                            },
                        ]
                    },
                    "allOf": {
                        "allOf": [
                            {
                                "type": "object",
                                "properties": {"five": {"type": "string"}},
                            },
                            {
                                "type": "object",
                                "properties": {"six": {"type": "string"}},
                            },
                        ]
                    },
                },
            },
            {
                "oneOf": {"one": "string"},
                "anyOf": {"three": "string"},
                "allOf": {"five": "string", "six": "string"},
            },
            id="oneOf_anyOf_allOf",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {"anything": {"description": "this can be anything"}},
            },
            {"anything": 1},
            id="any_type",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "min_int": {"type": "integer", "minimum": 10},
                    "max_int": {"type": "integer", "maximum": -10},
                    "min_and_max_int": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 20,
                    },
                    "exclusive_int": {
                        "type": "integer",
                        "minimum": -10,
                        "maximum": 10,
                        "exclusiveMinimum": True,
                        "exclusiveMaximum": True,
                    },
                    "min_num": {"type": "number", "minimum": 10.0},
                    "max_num": {"type": "number", "maximum": -10.0},
                    "exclusive_num": {
                        "type": "number",
                        "minimum": -10,
                        "maximum": 10,
                        "exclusiveMinimum": True,
                        "exclusiveMaximum": True,
                    },
                },
            },
            {
                "min_int": 11,
                "max_int": -11,
                "min_and_max_int": 15,
                "exclusive_int": 0,
                "min_num": 11.0,
                "max_num": -11.0,
                "exclusive_num": 0.0,
            },
            id="min_max",
        ),
    ],
)
def test_generate_example_from_schema(schema, expected):
    assert example_from_schema(schema) == expected
