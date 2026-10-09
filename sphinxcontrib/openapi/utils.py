"""
sphinxcontrib.openapi.utils
---------------------------

Common functionality shared across the various renderers.

:copyright: (c) 2016, Ihor Kalnytskyi.
:license: BSD, see LICENSE for details.
"""

import collections.abc
import json
import os.path
from contextlib import closing
from copy import deepcopy
from functools import lru_cache
from urllib.parse import urldefrag, urljoin, urlsplit
from urllib.request import urlopen

import referencing
import sphinx_mdinclude
import yaml

try:
    import requests
except ImportError:
    requests = None


def _retrieve_resource(uri):
    """Retrieve a JSON or YAML document referenced by an OpenAPI spec."""
    scheme, _, path, _, _ = urlsplit(uri)
    _, extension = os.path.splitext(path)
    is_yaml = extension in (".yml", ".yaml")

    if scheme in ("http", "https") and requests is not None:
        response = requests.get(uri)
        response.raise_for_status()
        contents = yaml.safe_load(response.content) if is_yaml else response.json()
    else:
        with closing(urlopen(uri)) as response:
            text = response.read().decode("utf-8")
            contents = yaml.safe_load(text) if is_yaml else json.loads(text)

    # OpenAPI documents (and their fragments) aren't necessarily JSON Schemas.
    return referencing.Resource.opaque(contents)


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

    # Keep unresolved resources separate from the spec we modify in-place.
    # Otherwise, expanding a reference could change the scope of nested refs
    # when the same resource is used again elsewhere.
    registry = referencing.Registry(
        retrieve=lru_cache(maxsize=None)(_retrieve_resource),
    ).with_resource(uri, referencing.Resource.opaque(deepcopy(spec)))

    def _do_resolve(node, resolver, base_uri, seen=()):
        if isinstance(node, collections.abc.Mapping) and "$ref" in node:
            ref = urljoin(base_uri, node["$ref"])
            if ref in seen:
                return {"type": "object"}  # a distinct object for recursive data types
            resolved = resolver.lookup(ref)
            return _do_resolve(
                deepcopy(resolved.contents),
                resolved.resolver,
                urldefrag(ref)[0],
                seen + (ref,),
            )
        elif isinstance(node, collections.abc.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v, resolver, base_uri, seen)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i], resolver, base_uri, seen)
        return node

    return _do_resolve(spec, registry.resolver(uri), uri)


def normalize_spec(spec, **options):
    # OpenAPI spec may contain JSON references, so we need resolve them
    # before we access the actual values trying to build an httpdomain
    # markup. Since JSON references may be relative, it's crucial to
    # pass a document URI in order to properly resolve them.
    spec = _resolve_refs(options.get("uri", ""), spec)

    # OpenAPI spec may contain common endpoint's parameters top-level.
    # In order to do not place if-s around the code to handle special
    # cases, let's normalize the spec and push common parameters inside
    # endpoints definitions.
    for endpoint in spec.get("paths", {}).values():
        parameters = endpoint.pop("parameters", [])
        for method in endpoint.values():
            method.setdefault("parameters", [])
            method["parameters"].extend(parameters)


def get_text_converter(options):
    """Decide on a text converter for prose."""
    if "format" in options:
        if options["format"] == "markdown":
            return sphinx_mdinclude.convert

    # No conversion needed.
    return lambda s: s
