"""OpenAPI spec renderer: render_parameter."""

import textwrap

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_parameter_path(testrenderer):
    """Usual path parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence identifier to query.",
                "schema": {"type": "string"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        """.rstrip()
    )


def test_render_parameter_path_minimal(testrenderer):
    """Path parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "path", "required": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_description(testrenderer):
    """Path parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence identifier to query.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_multiline_description(testrenderer):
    """Path parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence\nidentifier to query.",
            }
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


def test_render_parameter_path_description_commonmark_default(testrenderer):
    """Path parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence `identifier`\nto __query__.",
            }
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


def test_render_parameter_path_description_commonmark(fakestate):
    """Path parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence `identifier`\nto __query__.",
            }
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


def test_render_parameter_path_description_restructuredtext(fakestate):
    """Path parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "required": True,
                "description": "A unique evidence `identifier`\nto __query__.",
            }
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


def test_render_parameter_path_deprecated(testrenderer):
    """Path parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "path", "required": True, "deprecated": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required, deprecated
        """.rstrip()
    )


def test_render_parameter_path_deprecated_false(testrenderer):
    """Path parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "path", "required": True, "deprecated": False}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_path_type(testrenderer):
    """Path parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "path", "schema": {"type": "string"}}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_path_type_with_format(testrenderer):
    """Path parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "schema": {"type": "string", "format": "uuid4"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_path_type_from_content(testrenderer):
    """Path parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "content": {"text/plain": {"schema": {"type": "string"}}},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query(testrenderer):
    """Usual query parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "path",
                "description": "A unique evidence identifier to query.",
                "schema": {"type": "string"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query_minimal(testrenderer):
    """Query parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter({"name": "evidenceId", "in": "path"})
    )
    assert markup == textwrap.dedent(
        """\
        :param evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_description(testrenderer):
    """Query parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "description": "A unique evidence identifier to query.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence identifier to query.
        """.rstrip()
    )


def test_render_parameter_query_multiline_description(testrenderer):
    """Query parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "description": "A unique evidence\nidentifier to query.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence
           identifier to query.
        """.rstrip()
    )


def test_render_parameter_query_description_commonmark_default(testrenderer):
    """Query parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_query_description_commonmark(fakestate):
    """Query parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_query_description_restructuredtext(fakestate):
    """Query parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
           A unique evidence `identifier`
           to __query__.
        """.rstrip()
    )


def test_render_parameter_query_required(testrenderer):
    """Query parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "required": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: required
        """.rstrip()
    )


def test_render_parameter_query_required_false(testrenderer):
    """Query parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "required": False}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_deprecated(testrenderer):
    """Query parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "deprecated": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: deprecated
        """.rstrip()
    )


def test_render_parameter_query_deprecated_false(testrenderer):
    """Query parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "deprecated": False}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        """.rstrip()
    )


def test_render_parameter_query_required_deprecated(testrenderer):
    """Both query parameter's markers are rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "required": True, "deprecated": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: required, deprecated
        """.rstrip()
    )


def test_render_parameter_query_type(testrenderer):
    """Query parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "query", "schema": {"type": "string"}}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_query_type_with_format(testrenderer):
    """Query parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "schema": {"type": "string", "format": "uuid4"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_query_type_from_content(testrenderer):
    """Query parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "query",
                "content": {"text/plain": {"schema": {"type": "string"}}},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam evidenceId:
        :queryparamtype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_header(testrenderer):
    """Usual header parameter's definition is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "X-Request-Id",
                "in": "header",
                "description": "A unique request identifier.",
                "schema": {"type": "string"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request identifier.
        :reqheadertype X-Request-Id: string
        """.rstrip()
    )


def test_render_parameter_header_minimal(testrenderer):
    """Header parameter's minimal definition is rendered."""

    markup = textify(
        testrenderer.render_parameter({"name": "X-Request-Id", "in": "header"})
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_description(testrenderer):
    """Header parameter's 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "X-Request-Id",
                "in": "header",
                "description": "A unique request identifier.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request identifier.
        """.rstrip()
    )


def test_render_parameter_header_multiline_description(testrenderer):
    """Header parameter's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "X-Request-Id",
                "in": "header",
                "description": "A unique request\nidentifier.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
           A unique request
           identifier.
        """.rstrip()
    )


def test_render_parameter_header_description_commonmark_default(testrenderer):
    """Header parameter's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "header",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_header_description_commonmark(fakestate):
    """Header parameter's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "header",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence ``identifier``
           to **query**.
        """.rstrip()
    )


def test_render_parameter_header_description_restructuredtext(fakestate):
    """Header parameter's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "header",
                "description": "A unique evidence `identifier`\nto __query__.",
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
           A unique evidence `identifier`
           to __query__.
        """.rstrip()
    )


def test_render_parameter_header_required(testrenderer):
    """Header parameter's 'required' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "X-Request-Id", "in": "header", "required": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: required
        """.rstrip()
    )


def test_render_parameter_header_required_false(testrenderer):
    """Header parameter's 'required' marker is not rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "X-Request-Id", "in": "header", "required": False}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_deprecated(testrenderer):
    """Header parameter's 'deprecated' marker is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "X-Request-Id", "in": "header", "deprecated": True}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: deprecated
        """.rstrip()
    )


def test_render_parameter_header_deprecated_false(testrenderer):
    """Header parameter's 'deprecated' marker is not rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "X-Request-Id", "in": "header", "deprecated": False}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        """.rstrip()
    )


def test_render_parameter_header_required_deprecated(testrenderer):
    """Both header parameter's markers are rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "X-Request-Id",
                "in": "header",
                "required": True,
                "deprecated": True,
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader X-Request-Id:
        :reqheadertype X-Request-Id: required, deprecated
        """.rstrip()
    )


def test_render_parameter_header_type(testrenderer):
    """Header parameter's type is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {"name": "evidenceId", "in": "header", "schema": {"type": "string"}}
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string
        """.rstrip()
    )


def test_render_parameter_header_type_with_format(testrenderer):
    """Header parameter's type with format is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "header",
                "schema": {"type": "string", "format": "uuid4"},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string:uuid4
        """.rstrip()
    )


def test_render_parameter_header_type_from_content(testrenderer):
    """Header parameter's type from content is rendered."""

    markup = textify(
        testrenderer.render_parameter(
            {
                "name": "evidenceId",
                "in": "header",
                "content": {"text/plain": {"schema": {"type": "string"}}},
            }
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader evidenceId:
        :reqheadertype evidenceId: string
        """.rstrip()
    )
