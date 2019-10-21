"""
    sphinxcontrib.openapi.directive
    -------------------------------

    The main directive for the extension.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

import collections
try:
    from functools import lru_cache as simple_cache
except ImportError:
    def simple_cache():
        def decorate(user_function):
            cache = dict()

            def wrapper(*args):
                try:
                    result = cache[args]
                except KeyError:
                    result = user_function(*args)
                    cache[args] = result
                return result
            return wrapper
        return decorate

import io

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
import yaml

from sphinx.util.nodes import nested_parse_with_titles

from sphinxcontrib.openapi import openapi20
from sphinxcontrib.openapi import openapi30


# Dictionaries do not guarantee to preserve the keys order so when we load
# JSON or YAML - we may loose the order. In most cases it's not important
# because we're interested in data. However, in case of OpenAPI spec it'd
# be really nice to preserve them since, for example, endpoints may be
# grouped logically and that improved readability.
class _YamlOrderedLoader(yaml.SafeLoader):
    pass


_YamlOrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))
)


# Locally cache spec to speedup processing of same spec file in multiple
# openapi directives
@simple_cache()
def _get_spec(abspath, encoding):
    with io.open(abspath, 'rt', encoding=encoding) as stream:
        return yaml.load(stream, _YamlOrderedLoader)


def get_openapihttpdomain(options, abspath, encoding):
    spec = _get_spec(abspath, encoding)

    # URI parameter is crucial for resolving relative references. So
    # we need to set this option properly as it's used later down the
    # stack.
    options.setdefault('uri', 'file://%s' % abspath)

    # We support both OpenAPI 2.0 (f.k.a. Swagger) and OpenAPI 3.0.0, so
    # determine which version we are parsing here.
    spec_version = spec.get('openapi', spec.get('swagger', '2.0'))
    if spec_version.startswith('2.'):
        openapihttpdomain = openapi20.openapihttpdomain
    elif spec_version.startswith('3.'):
        openapihttpdomain = openapi30.openapihttpdomain
    else:
        raise ValueError('Unsupported OpenAPI version (%s)' % spec_version)
    return openapihttpdomain, spec


class OpenApi(Directive):

    required_arguments = 1                  # path to openapi spec
    final_argument_whitespace = True        # path may contain whitespaces
    option_spec = {
        'encoding': directives.encoding,    # useful for non-ascii cases :)
        'paths': lambda s: s.split(),       # endpoints to be rendered
        'include': lambda s: s.split(),     # endpoints to be included (regexp)
        'exclude': lambda s: s.split(),     # endpoints to be excluded (regexp)
        'request': directives.flag,         # print the request body structure
        'examples': directives.flag,        # render examples when passed
        'group': directives.flag,           # group paths by tag when passed
        'format': str,                      # "rst" (default) or "markdown"
    }

    def run(self):
        env = self.state.document.settings.env
        relpath, abspath = env.relfn2path(directives.path(self.arguments[0]))

        # Add OpenAPI spec as a dependency to the current document. That means
        # the document will be rebuilt if the spec is changed.
        env.note_dependency(relpath)

        # Read the spec using encoding passed to the directive or fallback to
        # the one specified in Sphinx's config.
        encoding = self.options.get('encoding', env.config.source_encoding)

        # Open the specification file
        openapihttpdomain, spec = \
            get_openapihttpdomain(self.options, abspath, encoding)

        # reStructuredText DOM manipulation is pretty tricky task. It requires
        # passing dozen arguments which is not easy without well-documented
        # internals. So the idea here is to represent OpenAPI spec as
        # reStructuredText in-memory text and parse it in order to produce a
        # real DOM.
        viewlist = ViewList()
        for line in openapihttpdomain(spec, **self.options):
            viewlist.append(line, '<openapi>')

        # Parse reStructuredText contained in `viewlist` and return produced
        # DOM nodes.
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, viewlist, node)
        return node.children
