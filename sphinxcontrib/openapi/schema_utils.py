"""OpenAPI schema utility functions."""

from io import StringIO

_DEFAULT_EXAMPLES = {
    "string": "string",
    "integer": 1,
    "number": 1.0,
    "boolean": True,
    "array": [],
    "null": None,
}


_DEFAULT_STRING_EXAMPLES = {
    "date": "2020-01-01",
    "date-time": "2020-01-01T01:01:01Z",
    "password": "********",
    "byte": "QG1pY2hhZWxncmFoYW1ldmFucw==",
    "ipv4": "127.0.0.1",
    "ipv6": "::1",
}


# Keywords an example can possibly be derived from. A schema that has none of
# them carries annotations only, and thus contributes no example. Please note,
# '$ref' is absent because references are expected to be resolved before a
# schema gets here, and 'default' because it's not consulted below.
_EXAMPLE_KEYWORDS = frozenset(
    ["example", "oneOf", "anyOf", "allOf", "enum", "type", "properties", "items"]
)


# Tells "no example has been found yet" apart from an example that is 'None',
# which is what an explicit 'example: null' produces. Never returned.
_NO_EXAMPLE = object()


class NoExampleError(ValueError):
    """A schema cannot contribute a generated example."""


def example_from_schema(schema):
    """
    Generates an example request/response body from the provided schema.

    >>> schema = {
    ...     "type": "object",
    ...     "required": ["id", "name"],
    ...     "properties": {
    ...         "id": {
    ...             "type": "integer",
    ...             "format": "int64"
    ...         },
    ...         "name": {
    ...             "type": "string",
    ...             "example": "John Smith"
    ...         },
    ...         "tag": {
    ...             "type": "string"
    ...         }
    ...     }
    ... }
    >>> example = example_from_schema(schema)
    >>> assert example == {
    ...     "id": 1,
    ...     "name": "John Smith",
    ...     "tag": "string"
    ... }
    """
    # JSON Schema boolean schemas accept every value or no value at all.
    if schema is True:
        return _DEFAULT_EXAMPLES["integer"]
    if schema is False:
        raise NoExampleError("A false schema accepts no values")

    # If an example was provided then we use that
    if "example" in schema:
        return schema["example"]

    elif "oneOf" in schema or "anyOf" in schema:
        alternatives = schema.get("oneOf", schema.get("anyOf"))
        for alternative in alternatives:
            try:
                return example_from_schema(alternative)
            except NoExampleError:
                continue
        raise NoExampleError("No alternative can contribute an example")

    elif "allOf" in schema:
        # Combine schema examples
        example = {}

        # Merging examples only makes sense for objects. If a subschema is of
        # any other type, an instance of the composed schema is a value of that
        # type, so the composed example is that value and there's nothing to
        # merge it into. Every subschema is still visited, so that the outcome
        # doesn't depend on their order, and an explicitly provided example wins
        # over one derived from a type.
        non_object_example = _NO_EXAMPLE
        non_object_example_is_explicit = False

        for sub_schema in schema["allOf"]:
            # True adds no constraints; False makes the conjunction impossible.
            if sub_schema is False:
                raise NoExampleError("An allOf subschema accepts no values")
            if sub_schema is True:
                continue

            # A subschema that carries annotations only, a lone 'description'
            # being the common case, has no example to contribute either.
            if not _EXAMPLE_KEYWORDS & sub_schema.keys():
                continue

            sub_example = example_from_schema(sub_schema)

            if not isinstance(sub_example, dict):
                is_explicit = "example" in sub_schema
                if non_object_example is _NO_EXAMPLE or (
                    is_explicit and not non_object_example_is_explicit
                ):
                    non_object_example = sub_example
                    non_object_example_is_explicit = is_explicit
                continue

            example.update(sub_example)

        if non_object_example is not _NO_EXAMPLE:
            return non_object_example
        return example

    elif "enum" in schema:
        return schema["enum"][0]

    elif isinstance(schema.get("type"), list):
        # Prefer a non-null example for nullable schemas, retaining declaration
        # order for other unions. Do not mutate the caller's schema.
        schema_types = [t for t in schema["type"] if t != "null"]
        if "null" in schema["type"]:
            schema_types.append("null")
        for schema_type in schema_types:
            try:
                return example_from_schema({**schema, "type": schema_type})
            except NoExampleError:
                continue
        raise NoExampleError("No declared type can contribute an example")

    elif "type" not in schema:
        # Any type
        return _DEFAULT_EXAMPLES["integer"]

    elif schema["type"] == "object":
        example = {}
        required = set(schema.get("required", []))
        for prop, prop_schema in schema.get("properties", {}).items():
            try:
                example[prop] = example_from_schema(prop_schema)
            except NoExampleError:
                if prop in required:
                    raise
        return example

    elif schema["type"] == "array":
        # In OAS 3.1, omitting items leaves array elements unconstrained.
        items = schema.get("items", {})
        min_length = schema.get("minItems", 0)
        max_length = schema.get("maxItems", max(min_length, 2))
        assert min_length <= max_length
        # Try generate at least 2 example array items
        gen_length = min(2, max_length) if min_length <= 2 else min_length

        # In OAS 3.1, prefixItems constrains initial positions, while items
        # applies only to the remaining positions (including items: false).
        example = []
        for item_schema in schema.get("prefixItems", [])[:gen_length]:
            try:
                example.append(example_from_schema(item_schema))
            except NoExampleError:
                if len(example) < min_length:
                    raise
                return example
        if len(example) == gen_length:
            return example

        example_items = []
        if items is True or items == {}:
            # Any-type arrays
            example_items.extend(_DEFAULT_EXAMPLES.values())
        else:
            # Treat the whole item schema like any other schema, preserving
            # explicit examples before considering oneOf/anyOf subschemas.
            try:
                example_items.append(example_from_schema(items))
            except NoExampleError:
                if len(example) < min_length:
                    raise
                return example

        example.extend(
            example_items[i % len(example_items)]
            for i in range(gen_length - len(example))
        )
        return example

    elif schema["type"] == "string":
        example_string = _DEFAULT_STRING_EXAMPLES.get(
            schema.get("format", None), _DEFAULT_EXAMPLES["string"]
        )
        min_length = schema.get("minLength", 0)
        max_length = schema.get("maxLength", max(min_length, len(example_string)))
        gen_length = (
            min(len(example_string), max_length)
            if min_length <= len(example_string)
            else min_length
        )
        assert 0 <= min_length <= max_length
        if min_length <= len(example_string) <= max_length:
            return example_string
        else:
            example_builder = StringIO()
            for i in range(gen_length):
                example_builder.write(example_string[i % len(example_string)])
            example_builder.seek(0)
            return example_builder.read()

    elif schema["type"] in ("integer", "number"):
        example = _DEFAULT_EXAMPLES[schema["type"]]
        if "minimum" in schema and "maximum" in schema:
            # Take average
            example = schema["minimum"] + (schema["maximum"] - schema["minimum"]) / 2
        elif "minimum" in schema and example <= schema["minimum"]:
            example = schema["minimum"] + 1
        elif "maximum" in schema and example >= schema["maximum"]:
            example = schema["maximum"] - 1
        return float(example) if schema["type"] == "number" else int(example)

    else:
        return _DEFAULT_EXAMPLES[schema["type"]]
