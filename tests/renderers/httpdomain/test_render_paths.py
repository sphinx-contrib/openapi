"""OpenAPI spec renderer: render_paths."""

import textwrap

from sphinxcontrib.openapi import renderers


def textify(generator):
    return "\n".join(generator)


def test_render_paths(testrenderer, oas_fragment):
    """Usual paths definition is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences/{evidenceId}:
                  summary: Ignored
                  description: Ignored
                  servers:
                    url: https://example.com
                  parameters:
                    - name: evidenceId
                      in: path
                      required: true
                      description: A unique evidence identifier to query.
                      schema:
                        type: string
                  get:
                    summary: Retrieve an evidence by ID.
                    description: More verbose description...
                    parameters:
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
            )
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
        """
    )


def test_render_paths_minimal(testrenderer, oas_fragment):
    """Minimal paths definition is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences:
                  get:
                    responses:
                      '200':
                        description: A list of evidences.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:get:: /evidences

           :statuscode 200:
              A list of evidences.
        """
    )


def test_render_paths_multiple(testrenderer, oas_fragment):
    """Paths definition with multiple paths is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences/{evidenceId}:
                  get:
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
                /evidences:
                  post:
                    summary: Create an evidence.
                    responses:
                      '201':
                        description: An evidence created.
                """
            )
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

        .. http:post:: /evidences

           **Create an evidence.**

           :statuscode 201:
              An evidence created.
        """
    )


def test_render_paths_parameters_common(testrenderer, oas_fragment):
    """Paths definition with common parameters is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences/{evidenceId}:
                  get:
                    summary: Retrieve an evidence by ID.
                    parameters:
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
                  put:
                    summary: Update an evidence by ID.
                    responses:
                      '200':
                        description: An evidence.
                      '404':
                        description: An evidence not found.
                  parameters:
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
        .. http:get:: /evidences/{evidenceId}

           **Retrieve an evidence by ID.**

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

        .. http:put:: /evidences/{evidenceId}

           **Update an evidence by ID.**

           :param evidenceId:
              A unique evidence identifier to query.
           :paramtype evidenceId: string, required
           :statuscode 200:
              An evidence.
           :statuscode 404:
              An evidence not found.
        """
    )


def test_render_paths_parameters_common_prepend(testrenderer, oas_fragment):
    """Paths definition with common parameters is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences/{evidenceId}/{evidenceSection}:
                  get:
                    summary: Retrieve an evidence by ID.
                    parameters:
                      - name: evidenceSection
                        in: path
                        description: Query a section with a given name.
                        schema:
                          type: string
                    responses:
                      '200':
                        description: An evidence.
                      '404':
                        description: An evidence not found.
                  parameters:
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
        .. http:get:: /evidences/{evidenceId}/{evidenceSection}

           **Retrieve an evidence by ID.**

           :param evidenceId:
              A unique evidence identifier to query.
           :paramtype evidenceId: string, required
           :param evidenceSection:
              Query a section with a given name.
           :paramtype evidenceSection: string
           :statuscode 200:
              An evidence.
           :statuscode 404:
              An evidence not found.
        """
    )


def test_render_paths_parameters_common_overwritten(testrenderer, oas_fragment):
    """Paths definition with common parameters is rendered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences/{evidenceId}:
                  get:
                    summary: Retrieve an evidence by ID.
                    parameters:
                      - name: evidenceId
                        in: path
                        description: Overwritten description.
                        schema:
                          type: string
                    responses:
                      '200':
                        description: An evidence.
                  parameters:
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
        .. http:get:: /evidences/{evidenceId}

           **Retrieve an evidence by ID.**

           :param evidenceId:
              Overwritten description.
           :paramtype evidenceId: string
           :statuscode 200:
              An evidence.
        """
    )


def test_render_paths_methods_order(testrenderer, oas_fragment):
    """Paths definition is rendered with HTTP methods ordered."""

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences:
                  post:
                    responses:
                      '201':
                        description: An evidence created.
                  options:
                    responses:
                      '200':
                        description: CORS preflight request.
                  get:
                    responses:
                      '200':
                        description: A list of evidences.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:post:: /evidences

           :statuscode 201:
              An evidence created.

        .. http:options:: /evidences

           :statuscode 200:
              CORS preflight request.

        .. http:get:: /evidences

           :statuscode 200:
              A list of evidences.
        """
    )


def test_render_paths_methods_order_custom(fakestate, oas_fragment):
    """Paths definition is rendered with HTTP methods ordered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"http-methods-order": ["delete", "options", "get", "post"]}
    )

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences:
                  post:
                    responses:
                      '201':
                        description: An evidence created.
                  options:
                    responses:
                      '200':
                        description: CORS preflight request.
                  get:
                    responses:
                      '200':
                        description: A list of evidences.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:options:: /evidences

           :statuscode 200:
              CORS preflight request.

        .. http:get:: /evidences

           :statuscode 200:
              A list of evidences.

        .. http:post:: /evidences

           :statuscode 201:
              An evidence created.
        """
    )


def test_render_paths_methods_order_insensitive(fakestate, oas_fragment):
    """Paths definition is rendered with HTTP methods ordered."""

    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"http-methods-order": ["gEt", "post"]}
    )

    markup = textify(
        testrenderer.render_paths(
            oas_fragment(
                """
                /evidences:
                  post:
                    responses:
                      '201':
                        description: An evidence created.
                  get:
                    responses:
                      '200':
                        description: A list of evidences.
                """
            )
        )
    )
    assert markup == textwrap.dedent(
        """\
        .. http:get:: /evidences

           :statuscode 200:
              A list of evidences.

        .. http:post:: /evidences

           :statuscode 201:
              An evidence created.
        """
    )
