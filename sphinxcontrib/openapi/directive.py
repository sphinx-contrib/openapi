"""
    sphinxcontrib.openapi.directive
    -------------------------------

    The main directive for the extension.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

import functools

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective
import yaml


# Locally cache spec to speedup processing of same spec file in multiple
# openapi directives
@functools.lru_cache()
def _get_spec(abspath, encoding):
    with open(abspath, 'rt', encoding=encoding) as stream:
        return yaml.safe_load(stream)


def create_directive_from_renderer(renderer_cls):
    """Create rendering directive from a renderer class."""

    class _RenderingDirective(SphinxDirective):
        required_arguments = 1                  # path to openapi spec
        final_argument_whitespace = True        # path may contain whitespaces
        option_spec = dict(
            {
                'encoding': directives.encoding,    # useful for non-ascii cases :)
            },
            **renderer_cls.option_spec
        )

        def run(self):
            relpath, abspath = self.env.relfn2path(directives.path(self.arguments[0]))

            # URI parameter is crucial for resolving relative references. So we
            # need to set this option properly as it's used later down the
            # stack.
            self.options.setdefault('uri', 'file://%s' % abspath)

            # Add a given OpenAPI spec as a dependency of the referring
            # reStructuredText document, so the document is rebuilt each time
            # the spec is changed.
            self.env.note_dependency(relpath)

            # Read the spec using encoding passed to the directive or fallback to
            # the one specified in Sphinx's config.
            encoding = self.options.get('encoding', self.config.source_encoding)
            spec = _get_spec(abspath, encoding)
            return renderer_cls(self.state, self.options).render(spec)

    return _RenderingDirective
