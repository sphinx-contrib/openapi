"""OpenAPI spec renderer: render_parameters."""

import itertools

import textwrap
import pytest

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_parameters_no_items(testrenderer, oas_fragment):
    """No parameter definitions are rendered."""

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                []
                """
            )
        )
    )
    assert markup == ""


def test_render_parameters_one_item(testrenderer, oas_fragment):
    """One usual parameter definition is rendered."""

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                - name: evidenceId
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


def test_render_parameters_many_items(testrenderer, oas_fragment):
    """Many parameter definitions are rendered."""

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
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
                - name: Api-Version
                  in: header
                  default: '1'
                  description: API version to use for the request.
                  schema:
                    type: integer
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        """.rstrip()
    )


@pytest.mark.parametrize("permutation_seq", itertools.permutations(range(3)))
def test_render_parameters_many_items_ordered(
    testrenderer, oas_fragment, permutation_seq
):
    """Many parameter definitions are rendered and properly ordered."""

    parameters = oas_fragment(
        """
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
        - name: Api-Version
          in: header
          required: false
          default: '1'
          description: API version to use for the request.
          schema:
            type: integer
        """
    )

    markup = textify(
        testrenderer.render_parameters(
            # Since the test receives a permutation sequence as input,
            # we need to ensure that parameters are shuffled according
            # to that sequence, because this is the essence of the test.
            [parameters[seq] for seq in permutation_seq]
        )
    )

    assert markup == textwrap.dedent(
        """\
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        """.rstrip()
    )


def test_render_parameters_many_items_stable_order(testrenderer, oas_fragment):
    """Many parameter definitions are rendered w/ preserved order."""

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                - name: kind
                  in: path
                  required: true
                  description: An evidence kind.
                  schema:
                    type: string
                - name: Api-Version
                  in: header
                  default: '1'
                  description: API version to use for the request.
                  schema:
                    type: integer
                - name: details
                  in: query
                  description: If true, information w/ details is returned.
                  schema:
                    type: boolean
                - name: evidenceId
                  in: path
                  required: true
                  description: A unique evidence identifier to query.
                  schema:
                    type: string
                - name: related
                  in: query
                  description: If true, links to related evidences are returned.
                  schema:
                    type: boolean
                - name: Accept
                  in: header
                  default: application/json
                  description: A desired Content-Type of HTTP response.
                  schema:
                    type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :reqheader Accept:
           A desired Content-Type of HTTP response.
        :reqheadertype Accept: string
        :param kind:
           An evidence kind.
        :paramtype kind: string, required
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        :queryparam related:
           If true, links to related evidences are returned.
        :queryparamtype related: boolean
        """.rstrip()
    )


def test_render_parameters_custom_order(fakestate, oas_fragment):
    """Many parameter definitions are rendered w/ preserved order."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"request-parameters-order": ["query", "path", "header"]}
    )

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                - name: kind
                  in: path
                  required: true
                  description: An evidence kind.
                  schema:
                    type: string
                - name: Api-Version
                  in: header
                  default: '1'
                  description: API version to use for the request.
                  schema:
                    type: integer
                - name: details
                  in: query
                  description: If true, information w/ details is returned.
                  schema:
                    type: boolean
                - name: evidenceId
                  in: path
                  required: true
                  description: A unique evidence identifier to query.
                  schema:
                    type: string
                - name: related
                  in: query
                  description: If true, links to related evidences are returned.
                  schema:
                    type: boolean
                - name: Accept
                  in: header
                  default: application/json
                  description: A desired Content-Type of HTTP response.
                  schema:
                    type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        :queryparam related:
           If true, links to related evidences are returned.
        :queryparamtype related: boolean
        :param kind:
           An evidence kind.
        :paramtype kind: string, required
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :reqheader Accept:
           A desired Content-Type of HTTP response.
        :reqheadertype Accept: string
        """.rstrip()
    )


def test_render_parameters_custom_order_partial(fakestate, oas_fragment):
    """Many parameter definitions are rendered w/ preserved order."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"request-parameters-order": ["query", "path"]}
    )

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                - name: kind
                  in: path
                  required: true
                  description: An evidence kind.
                  schema:
                    type: string
                - name: Api-Version
                  in: header
                  default: '1'
                  description: API version to use for the request.
                  schema:
                    type: integer
                - name: details
                  in: query
                  description: If true, information w/ details is returned.
                  schema:
                    type: boolean
                - name: evidenceId
                  in: path
                  required: true
                  description: A unique evidence identifier to query.
                  schema:
                    type: string
                - name: related
                  in: query
                  description: If true, links to related evidences are returned.
                  schema:
                    type: boolean
                - name: Accept
                  in: header
                  default: application/json
                  description: A desired Content-Type of HTTP response.
                  schema:
                    type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        :queryparam related:
           If true, links to related evidences are returned.
        :queryparamtype related: boolean
        :param kind:
           An evidence kind.
        :paramtype kind: string, required
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :reqheader Accept:
           A desired Content-Type of HTTP response.
        :reqheadertype Accept: string
        """.rstrip()
    )


def test_render_parameters_case_insensitive(fakestate, oas_fragment):
    """Many parameter definitions are rendered w/ preserved order."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"request-parameters-order": ["QUERY", "pAth", "Header"]}
    )

    markup = textify(
        testrenderer.render_parameters(
            oas_fragment(
                """
                - name: kind
                  in: PATH
                  required: true
                  description: An evidence kind.
                  schema:
                    type: string
                - name: Api-Version
                  in: header
                  default: '1'
                  description: API version to use for the request.
                  schema:
                    type: integer
                - name: details
                  in: query
                  description: If true, information w/ details is returned.
                  schema:
                    type: boolean
                - name: evidenceId
                  in: Path
                  required: true
                  description: A unique evidence identifier to query.
                  schema:
                    type: string
                - name: related
                  in: qUery
                  description: If true, links to related evidences are returned.
                  schema:
                    type: boolean
                - name: Accept
                  in: headeR
                  default: application/json
                  description: A desired Content-Type of HTTP response.
                  schema:
                    type: string
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        :queryparam details:
           If true, information w/ details is returned.
        :queryparamtype details: boolean
        :queryparam related:
           If true, links to related evidences are returned.
        :queryparamtype related: boolean
        :param kind:
           An evidence kind.
        :paramtype kind: string, required
        :param evidenceId:
           A unique evidence identifier to query.
        :paramtype evidenceId: string, required
        :reqheader Api-Version:
           API version to use for the request.
        :reqheadertype Api-Version: integer
        :reqheader Accept:
           A desired Content-Type of HTTP response.
        :reqheadertype Accept: string
        """.rstrip()
    )
