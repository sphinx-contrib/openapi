"""
    sphinxcontrib.openapi.utils
    ---------------------------

    Common functionality shared across the various renderers.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

import collections
import collections.abc

from contextlib import closing
import jsonschema
import yaml
import sphinx_mdinclude

from urllib.parse import urlsplit
from urllib.request import urlopen

import os.path


class OpenApiRefResolver(jsonschema.RefResolver):
    """
    Overrides resolve_remote to support both YAML and JSON
    OpenAPI schemas.
    """

    try:
        import requests
        _requests = requests
    except ImportError:
        _requests = None

    def resolve_remote(self, uri):
        scheme, _, path, _, _ = urlsplit(uri)
        _, extension = os.path.splitext(path)

        if extension not in [".yml", ".yaml"] or scheme in self.handlers:
            return super(OpenApiRefResolver, self).resolve_remote(uri)

        if scheme in [u"http", u"https"] and self._requests:
            response = self._requests.get(uri)
            result = yaml.safe_load(response.content)
        else:
            # Otherwise, pass off to urllib and assume utf-8
            with closing(urlopen(uri)) as url:
                response = url.read().decode("utf-8")
                result = yaml.safe_load(response)

        if self.cache_remote:
            self.store[uri] = result
        return result


def _resolve_refs(uri, spec):
    """Resolve JSON references in a given dictionary.

    OpenAPI spec may contain JSON references to its nodes or external
    sources, so any attempt to rely that there's some expected attribute
    in the spec may fail. So we need to resolve JSON references before
    we use it (i.e. replace with referenced object). For details see:

        https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-02

    The input spec is modified in-place despite being returned from
    the function.
    """

    resolver = OpenApiRefResolver(uri, spec)

    def _do_resolve(node, seen=[]):
        if isinstance(node, collections.abc.Mapping) and '$ref' in node:
            ref = node['$ref']
            with resolver.resolving(ref) as resolved:
                if ref in seen:
                    return {type: 'object'}  # return a distinct object for recursive data type
                return _do_resolve(resolved, seen + [ref])  # might have other references
        elif isinstance(node, collections.abc.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v, seen)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i], seen)
        return node

    return _do_resolve(spec)


def normalize_spec(spec, **options):
    # OpenAPI spec may contain JSON references, so we need resolve them
    # before we access the actual values trying to build an httpdomain
    # markup. Since JSON references may be relative, it's crucial to
    # pass a document URI in order to properly resolve them.
    spec = _resolve_refs(options.get('uri', ''), spec)

    # OpenAPI spec may contain common endpoint's parameters top-level.
    # In order to do not place if-s around the code to handle special
    # cases, let's normalize the spec and push common parameters inside
    # endpoints definitions.
    for endpoint in spec.get('paths', {}).values():
        parameters = endpoint.pop('parameters', [])
        for method in endpoint.values():
            method.setdefault('parameters', [])
            method['parameters'].extend(parameters)


def get_text_converter(options):
    """Decide on a text converter for prose."""
    if 'format' in options:
        if options['format'] == 'markdown':
            return sphinx_mdinclude.convert

    # No conversion needed.
    return lambda s: s
