"""OpenAPI spec renderer: render_operation."""

import textwrap

import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_operation(testrenderer, oas_fragment):
    """Usual operation definition is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences/{evidenceId}",
            "get",
            oas_fragment(
                """
                summary: Retrieve an evidence by ID.
                description: More verbose description...
                parameters:
                  - name: evidenceId
                    in: path
                    required: true
                    description: A unique evidence identifier to query.
                    schema:
                      type: string
                  - name: details
                    in: query
                    description: If true, information w/ details is returned.
                    schema:
                      type: boolean
                responses:
                  '200':
                    description: An evidence.
                  '404':
                    description: An evidence not found.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:get:: /evidences/{evidenceId}

           **Retrieve an evidence by ID.**

           More verbose description...

           :param evidenceId:
              A unique evidence identifier to query.
           :paramtype evidenceId: string, required
           :queryparam details:
              If true, information w/ details is returned.
           :queryparamtype details: boolean
           :statuscode 200:
              An evidence.
           :statuscode 404:
              An evidence not found.
        """.rstrip()
    )


def test_render_operation_minimal(testrenderer, oas_fragment):
    """Operation minimal definition is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_summary(testrenderer, oas_fragment):
    """Operation's 'summary' is rendered in bold."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                summary: Create an evidence.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           **Create an evidence.**

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_description(testrenderer, oas_fragment):
    """Operation's 'description' is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                description: Create an evidence.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           Create an evidence.

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_description_multiline(testrenderer, oas_fragment):
    """Operation's multiline 'description' is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                description: |
                  Create
                  an evidence.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           Create
           an evidence.

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_description_commonmark_default(testrenderer, oas_fragment):
    """Operation's 'description' must be in commonmark by default."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                description: __Create__ an `evidence`.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           **Create** an ``evidence``.

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_description_commonmark(fakestate, oas_fragment):
    """Operation's 'description' can be in commonmark."""

    testrenderer = renderers.HttpdomainRenderer(fakestate, {"markup": "commonmark"})
    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                description: __Create__ an `evidence`.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           **Create** an ``evidence``.

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_description_commonmark_restructuredtext(
    fakestate, oas_fragment
):
    """Operation's 'description' can be in restructuredtext."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"markup": "restructuredtext"}
    )
    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                description: __Create__ an `evidence`.
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           __Create__ an `evidence`.

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_deprecated(testrenderer, oas_fragment):
    """Operation's 'deprecated' mark is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                responses:
                  '201':
                    description: An evidence created.
                deprecated: true
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences
           :deprecated:

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


def test_render_operation_w_requestbody(testrenderer, oas_fragment):
    """Operation's 'requestBody' is rendered."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            "post",
            oas_fragment(
                """
                requestBody:
                  content:
                    application/json:
                      example:
                        foo: bar
                        baz: 42
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           .. sourcecode:: http

              POST /evidences HTTP/1.1
              Content-Type: application/json

              {
                "foo": "bar",
                "baz": 42
              }

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )


@pytest.mark.parametrize(
    ["method"], [pytest.param("POST"), pytest.param("pOst"), pytest.param("post")]
)
def test_render_operation_caseinsensitive_method(testrenderer, method, oas_fragment):
    """Operation's 'method' is case insensitive."""

    markup = textify(
        testrenderer.render_operation(
            "/evidences",
            method,
            oas_fragment(
                """
                requestBody:
                  content:
                    application/json:
                      example:
                        foo: bar
                        baz: 42
                responses:
                  '201':
                    description: An evidence created.
                """
            ),
        )
    )
    assert markup == textwrap.dedent(
        f"""\
        .. http:{method}:: /evidences

           .. sourcecode:: http

              {method.upper()} /evidences HTTP/1.1
              Content-Type: application/json

              {{
                "foo": "bar",
                "baz": 42
              }}

           :statuscode 201:
              An evidence created.
        """.rstrip()
    )
