"""OpenAPI spec renderer: render_json_schema_description."""

import textwrap

import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_root_object(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON object in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  prop_a:
                    type: string
                  prop_b:
                    type: object
                    properties:
                      eggs:
                        type: boolean
                  prop_c:
                    type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop_a:
        :{typedirective} prop_a: string
        :{directive} prop_b:
        :{typedirective} prop_b: object
        :{directive} prop_b.eggs:
        :{typedirective} prop_b.eggs: boolean
        :{directive} prop_c:
        :{typedirective} prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjsonarr", "reqjsonarrtype", id="req"),
        pytest.param("res", "resjsonarr", "resjsonarrtype", id="res"),
    ],
)
def test_render_json_schema_description_root_array(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON array in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: array
                items:
                  type: object
                  properties:
                    prop:
                      type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop:
        :{typedirective} prop: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
@pytest.mark.parametrize(
    ["schema_type"],
    [
        pytest.param("null"),
        pytest.param("boolean"),
        pytest.param("number"),
        pytest.param("string"),
        pytest.param("integer"),
    ],
)
def test_render_json_schema_description_root_unsupported(
    testrenderer, oas_fragment, schema_type, req_or_res, directive, typedirective
):
    """JSON schema description is not generated for unsupported type in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                f"""
                type: {schema_type}
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        """\
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_root_any_of_object(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for anyOf JSON object in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                anyOf:
                  - type: object
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        type: number
                  - type: object
                    properties:
                      prop_c:
                        type: object
                        properties:
                          eggs:
                            type: boolean
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop_a:
        :{typedirective} prop_a: string
        :{directive} prop_b:
        :{typedirective} prop_b: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjsonarr", "reqjsonarrtype", id="req"),
        pytest.param("res", "resjsonarr", "resjsonarrtype", id="res"),
    ],
)
def test_render_json_schema_description_root_any_of_array(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for anyOf JSON array in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                anyOf:
                  - type: array
                    items:
                      type: object
                      properties:
                        prop:
                          type: string
                  - type: array
                    items:
                      type: object
                      properties:
                        prop:
                          type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop:
        :{typedirective} prop: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
@pytest.mark.parametrize(
    ["schema_type"],
    [
        pytest.param("null"),
        pytest.param("boolean"),
        pytest.param("number"),
        pytest.param("string"),
        pytest.param("integer"),
    ],
)
def test_render_json_schema_description_root_any_of_unsupported(
    testrenderer, oas_fragment, schema_type, req_or_res, directive, typedirective
):
    """JSON schema description is not generated for anyOf unsupported type in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                f"""
                anyOf:
                  - type: {schema_type}
                  - type: object
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        """\
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_root_one_of_object(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for oneOf JSON object in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                oneOf:
                  - type: object
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        type: number
                  - type: object
                    properties:
                      prop_c:
                        type: object
                        properties:
                          eggs:
                            type: boolean
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop_a:
        :{typedirective} prop_a: string
        :{directive} prop_b:
        :{typedirective} prop_b: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjsonarr", "reqjsonarrtype", id="req"),
        pytest.param("res", "resjsonarr", "resjsonarrtype", id="res"),
    ],
)
def test_render_json_schema_description_root_one_of_array(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for oneOf JSON array in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                oneOf:
                  - type: array
                    items:
                      type: object
                      properties:
                        prop:
                          type: string
                  - type: array
                    items:
                      type: object
                      properties:
                        prop:
                          type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} prop:
        :{typedirective} prop: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
@pytest.mark.parametrize(
    ["schema_type"],
    [
        pytest.param("null"),
        pytest.param("boolean"),
        pytest.param("number"),
        pytest.param("string"),
        pytest.param("integer"),
    ],
)
def test_render_json_schema_description_root_one_of_unsupported(
    testrenderer, oas_fragment, schema_type, req_or_res, directive, typedirective
):
    """JSON schema description is not generated for oneOf unsupported type in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                f"""
                oneOf:
                  - type: {schema_type}
                  - type: object
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        """\
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_root_all_of_object(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for allOf in root."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                allOf:
                  - properties:
                      name:
                        properties:
                          first:
                            type: string
                      age:
                        type: integer
                  - properties:
                      name:
                        properties:
                          last:
                            type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} name:
        :{typedirective} name: object
        :{directive} name.first:
        :{typedirective} name.first: string
        :{directive} name.last:
        :{typedirective} name.last: string
        :{directive} age:
        :{typedirective} age: integer
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
@pytest.mark.parametrize(
    ["schema_type"],
    [
        pytest.param("null"),
        pytest.param("boolean"),
        pytest.param("number"),
        pytest.param("string"),
        pytest.param("integer"),
    ],
)
def test_render_json_schema_description_primitive(
    testrenderer, oas_fragment, schema_type, req_or_res, directive, typedirective
):
    """JSON schema description is generated for primitive types."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                f"""
                type: object
                properties:
                  some_key:
                    type: "{schema_type}"
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: {schema_type}
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_object(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON object."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    type: object
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        type: object
                        properties:
                          eggs:
                            type: boolean
                      prop_c:
                        type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: object
        :{directive} root.prop_a:
        :{typedirective} root.prop_a: string
        :{directive} root.prop_b:
        :{typedirective} root.prop_b: object
        :{directive} root.prop_b.eggs:
        :{typedirective} root.prop_b.eggs: boolean
        :{directive} root.prop_c:
        :{typedirective} root.prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_object_implicit(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for implicit JSON object."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        properties:
                          eggs:
                            type: boolean
                      prop_c:
                        type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: object
        :{directive} root.prop_a:
        :{typedirective} root.prop_a: string
        :{directive} root.prop_b:
        :{typedirective} root.prop_b: object
        :{directive} root.prop_b.eggs:
        :{typedirective} root.prop_b.eggs: boolean
        :{directive} root.prop_c:
        :{typedirective} root.prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_array(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON array."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    type: array
                    items:
                      type: object
                      properties:
                        prop_a:
                          type: string
                        prop_b:
                          type: array
                          items:
                            type: number
                        prop_c:
                          type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root[]:
        :{typedirective} root[]: object
        :{directive} root[].prop_a:
        :{typedirective} root[].prop_a: string
        :{directive} root[].prop_b[]:
        :{typedirective} root[].prop_b[]: number
        :{directive} root[].prop_c:
        :{typedirective} root[].prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_array_implicit(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for implicit JSON array."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    items:
                      type: object
                      properties:
                        prop_a:
                          type: string
                        prop_b:
                          items:
                            type: number
                        prop_c:
                          type: number
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root[]:
        :{typedirective} root[]: object
        :{directive} root[].prop_a:
        :{typedirective} root[].prop_a: string
        :{directive} root[].prop_b[]:
        :{typedirective} root[].prop_b[]: number
        :{directive} root[].prop_c:
        :{typedirective} root[].prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_format(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for formatted types."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  created_at:
                    type: string
                    format: date-time
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
        :{typedirective} created_at: string:date-time
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_deprecated(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated with deprecated marker."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  created_at:
                    type: string
                    deprecated: true
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
        :{typedirective} created_at: string, deprecated
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_required(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON object w/ required marker."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    type: object
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        type: object
                        properties:
                          eggs:
                            type: boolean
                        required: [eggs]
                      prop_c:
                        type: number
                    required: [prop_a]
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: object
        :{directive} root.prop_a:
        :{typedirective} root.prop_a: string, required
        :{directive} root.prop_b:
        :{typedirective} root.prop_b: object
        :{directive} root.prop_b.eggs:
        :{typedirective} root.prop_b.eggs: boolean, required
        :{directive} root.prop_c:
        :{typedirective} root.prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_deprecated_and_required(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON object w/ deprecated & required markers."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    type: object
                    properties:
                      prop_a:
                        type: string
                      prop_b:
                        type: object
                        properties:
                          eggs:
                            type: boolean
                            deprecated: true
                        required: [eggs]
                      prop_c:
                        type: number
                    required: [prop_a]
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: object
        :{directive} root.prop_a:
        :{typedirective} root.prop_a: string, required
        :{directive} root.prop_b:
        :{typedirective} root.prop_b: object
        :{directive} root.prop_b.eggs:
        :{typedirective} root.prop_b.eggs: boolean, deprecated, required
        :{directive} root.prop_c:
        :{typedirective} root.prop_c: number
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_description(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated with description."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                description: a resource representation
                properties:
                  created_at:
                    type: string
                    description: a resource creation time
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
           a resource creation time
        :{typedirective} created_at: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_description_commonmark_default(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated with CommonMark description by default."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                description: a resource representation
                properties:
                  created_at:
                    type: string
                    description: a `resource` creation __time__
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
           a ``resource`` creation **time**
        :{typedirective} created_at: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_description_commonmark(
    fakestate, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated with CommonMark description."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                description: a resource representation
                properties:
                  created_at:
                    type: string
                    description: a `resource` creation __time__
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
           a ``resource`` creation **time**
        :{typedirective} created_at: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_description_restructuredtext(
    fakestate, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated with reStructuredText description."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                description: a resource representation
                properties:
                  created_at:
                    type: string
                    description: a `resource` creation __time__
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} created_at:
           a `resource` creation __time__
        :{typedirective} created_at: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_any_of(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for anyOf."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                f"""
                type: object
                properties:
                  some_key:
                    anyOf:
                      - type: integer
                      - type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: integer
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_one_of(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for oneOf."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  some_key:
                    oneOf:
                      - type: integer
                      - type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: integer
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_all_of(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for allOf."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  person:
                    allOf:
                      - properties:
                          name:
                            properties:
                              first:
                                type: string
                          age:
                            type: integer
                      - properties:
                          name:
                            properties:
                              last:
                                type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} person:
        :{typedirective} person: object
        :{directive} person.name:
        :{typedirective} person.name: object
        :{directive} person.name.first:
        :{typedirective} person.name.first: string
        :{directive} person.name.last:
        :{typedirective} person.name.last: string
        :{directive} person.age:
        :{typedirective} person.age: integer
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_all_of_logical_impossible(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for allOf that is logical impossible."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  some_key:
                    allOf:
                      - type: integer
                      - type: string
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_any_of_shared_type(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for anyOf w/ shared 'type'."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  some_key:
                    type: string
                    anyOf:
                      - minLength: 3
                      - maxLength: 5
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_one_of_shared_type(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for oneOf w/ shared 'type'."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  some_key:
                    type: string
                    oneOf:
                      - minLength: 3
                      - maxLength: 5
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_all_of_shared_type(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for allOf w/ shared 'type'."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  some_key:
                    type: string
                    alOf:
                      - minLength: 3
                      - maxLength: 5
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} some_key:
        :{typedirective} some_key: string
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_not(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON *not*."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    not:
                      type: boolean
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_enum(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON enum."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    type: string
                    enum:
                      - foo
                      - bar
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: string:enum
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["req_or_res", "directive", "typedirective"],
    [
        pytest.param("req", "reqjson", "reqjsonobj", id="req"),
        pytest.param("res", "resjson", "resjsonobj", id="res"),
    ],
)
def test_render_json_schema_description_enum_wo_type(
    testrenderer, oas_fragment, req_or_res, directive, typedirective
):
    """JSON schema description is generated for JSON enum wo/ type."""

    markup = textify(
        testrenderer.render_json_schema_description(
            oas_fragment(
                """
                type: object
                properties:
                  root:
                    enum:
                      - foo
                      - bar
                """
            ),
            req_or_res,
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        :{directive} root:
        :{typedirective} root: enum
        """.rstrip()
    )
