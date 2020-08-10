"""OpenAPI spec renderer: render_parameter."""

import textwrap

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_parameter_path(testrenderer, oas_fragment):
    """Usual path parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: A unique evidence identifier to query.
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        """.rstrip()
    )


def test_render_parameter_path_minimal(testrenderer, oas_fragment):
    """Path parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_description(testrenderer, oas_fragment):
    """Path parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: A unique evidence identifier to query.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_multiline_description(testrenderer, oas_fragment):
    """Path parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: |
                  A unique evidence
                  identifier to query.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence
           identifier to query.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_description_commonmark_default(
    testrenderer, oas_fragment
):
    """Path parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence ``identifier``
           to **query**.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_description_commonmark(fakestate, oas_fragment):
    """Path parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence ``identifier``
           to **query**.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_description_restructuredtext(fakestate, oas_fragment):
    """Path parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence `identifier`
           to __query__.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_deprecated(testrenderer, oas_fragment):
    """Path parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                deprecated: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required, deprecated
        """.rstrip()
    )


def test_render_parameter_path_deprecated_false(testrenderer, oas_fragment):
    """Path parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                required: true
                deprecated: false
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_type(testrenderer, oas_fragment):
    """Path parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_path_type_with_format(testrenderer, oas_fragment):
    """Path parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                schema:
                  type: string
                  format: uuid4
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_path_type_from_content(testrenderer, oas_fragment):
    """Path parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                content:
                  text/plain:
                    schema:
                      type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query(testrenderer, oas_fragment):
    """Usual query parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                description: A unique evidence identifier to query.
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query_minimal(testrenderer, oas_fragment):
    """Query parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: path
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_description(testrenderer, oas_fragment):
    """Query parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                description: A unique evidence identifier to query.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence identifier to query.
        """.rstrip()
    )


def test_render_parameter_query_multiline_description(testrenderer, oas_fragment):
    """Query parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                description: |
                  A unique evidence
                  identifier to query.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence
           identifier to query.
        """.rstrip()
    )


def test_render_parameter_query_description_commonmark_default(
    testrenderer, oas_fragment
):
    """Query parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_query_description_commonmark(fakestate, oas_fragment):
    """Query parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_query_description_restructuredtext(fakestate, oas_fragment):
    """Query parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence `identifier`
           to __query__.
        """.rstrip()
    )


def test_render_parameter_query_required(testrenderer, oas_fragment):
    """Query parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                required: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_query_required_false(testrenderer, oas_fragment):
    """Query parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                required: false
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_deprecated(testrenderer, oas_fragment):
    """Query parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                deprecated: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: deprecated
        """.rstrip()
    )


def test_render_parameter_query_deprecated_false(testrenderer, oas_fragment):
    """Query parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                deprecated: false
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_required_deprecated(testrenderer, oas_fragment):
    """Both query parameter's markers are rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                required: true
                deprecated: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: required, deprecated
        """.rstrip()
    )


def test_render_parameter_query_type(testrenderer, oas_fragment):
    """Query parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query_type_with_format(testrenderer, oas_fragment):
    """Query parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                schema:
                  type: string
                  format: uuid4
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_query_type_from_content(testrenderer, oas_fragment):
    """Query parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: query
                content:
                  text/plain:
                    schema:
                      type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_header(testrenderer, oas_fragment):
    """Usual header parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                description: A unique request identifier.
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request identifier.
        :reqheadertype X-Request-Id: string
        """.rstrip()
    )


def test_render_parameter_header_minimal(testrenderer, oas_fragment):
    """Header parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_description(testrenderer, oas_fragment):
    """Header parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                description: A unique request identifier.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request identifier.
        """.rstrip()
    )


def test_render_parameter_header_multiline_description(testrenderer, oas_fragment):
    """Header parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                description: |
                  A unique request
                  identifier.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request
           identifier.
        """.rstrip()
    )


def test_render_parameter_header_description_commonmark_default(
    testrenderer, oas_fragment
):
    """Header parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_header_description_commonmark(fakestate, oas_fragment):
    """Header parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_header_description_restructuredtext(fakestate, oas_fragment):
    """Header parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                description: |
                  A unique evidence `identifier`
                  to __query__.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence `identifier`
           to __query__.
        """.rstrip()
    )


def test_render_parameter_header_required(testrenderer, oas_fragment):
    """Header parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                required: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: required
        """.rstrip()
    )


def test_render_parameter_header_required_false(testrenderer, oas_fragment):
    """Header parameter's 'required' marker is not rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                required: false
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_deprecated(testrenderer, oas_fragment):
    """Header parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                deprecated: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: deprecated
        """.rstrip()
    )


def test_render_parameter_header_deprecated_false(testrenderer, oas_fragment):
    """Header parameter's 'deprecated' marker is not rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                deprecated: false
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_required_deprecated(testrenderer, oas_fragment):
    """Both header parameter's markers are rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: X-Request-Id
                in: header
                required: true
                deprecated: true
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: required, deprecated
        """.rstrip()
    )


def test_render_parameter_header_type(testrenderer, oas_fragment):
    """Header parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                schema:
                  type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_header_type_with_format(testrenderer, oas_fragment):
    """Header parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                schema:
                  type: string
                  format: uuid4
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_header_type_from_content(testrenderer, oas_fragment):
    """Header parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            oas_fragment(
                """
                name: evidenceId
                in: header
                content:
                  text/plain:
                    schema:
                      type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string
        """.rstrip()
    )
