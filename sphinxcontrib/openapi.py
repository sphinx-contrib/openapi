"""
    sphinxcontrib.openapi
    ---------------------

    The OpenAPI spec renderer for Sphinx. It's a new way to document your
    RESTful API. Based on ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

try:
    from httplib import responses as http_status_codes  # python2
except ImportError:
    from http.client import responses as http_status_codes  # python3

import io
import itertools
import collections

import yaml
import jsonschema

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from sphinx.util.nodes import nested_parse_with_titles


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
    resolver = jsonschema.RefResolver(uri, spec)

    def _do_resolve(node):
        if isinstance(node, collections.Mapping) and '$ref' in node:
            with resolver.resolving(node['$ref']) as resolved:
                return resolved
        elif isinstance(node, collections.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i])
        return node

    return _do_resolve(spec)


def _httpresource_v2(endpoint, method, properties):
    parameters = properties.get('parameters', [])
    responses = properties['responses']
    indent = '   '

    yield '.. http:{0}:: {1}'.format(method, endpoint)
    yield '   :synopsis: {0}'.format(properties.get('summary', 'null'))
    yield ''

    if 'summary' in properties:
        for line in properties['summary'].splitlines():
            yield '{indent}**{line}**'.format(**locals())
        yield ''

    if 'description' in properties:
        for line in properties['description'].splitlines():
            yield '{indent}{line}'.format(**locals())
        yield ''

    for param in filter(lambda p: p['in'] == 'path', parameters):
        yield indent + ':param {type} {name}:'.format(**param)
        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print request's query params
    for param in filter(lambda p: p['in'] == 'query', parameters):
        yield indent + ':query {type} {name}:'.format(**param)
        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print response status codes
    for status, response in responses.items():
        yield '{indent}:status {status}:'.format(**locals())
        for line in response['description'].splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print request header params
    for param in filter(lambda p: p['in'] == 'header', parameters):
        yield indent + ':reqheader {name}:'.format(**param)
        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print response headers
    for status, response in responses.items():
        for headername, header in response.get('headers', {}).items():
            yield indent + ':resheader {name}:'.format(name=headername)
            for line in header['description'].splitlines():
                yield '{indent}{indent}{line}'.format(**locals())

    yield ''


def convert_json_schema(schema, directive=':<json'):
    """
    Convert json schema to `:<json` sphinx httmdomain.
    """

    output = []

    def _convert(schema, name='', required=False):
        """
        Fill the output list, with 2-tuple (name, template)

        i.e: ('user.age', 'str user.age: the age of user')

        This allow to sort output by field name
        """

        type_ = schema.get('type', 'any')
        required_properties = schema.get('required', ())
        if type_ == 'object':
            for prop, next_schema in schema['properties'].items():
                _convert(
                    next_schema, '{name}.{prop}'.format(**locals()),
                    (prop in required_properties))

        elif type_ == 'array':
            _convert(schema['items'], name + '[]')

        else:
            if name:
                name = name.lstrip('.')
                constraints = []
                if required:
                    constraints.append('required')
                if schema.get('readOnly', False):
                    constraints.append('read only')
                if constraints:
                    constraints = '({})'.format(', '.join(constraints))
                else:
                    constraints = ''

                if schema.get('description', ''):
                    if constraints:
                        output.append((
                            name,
                            '{type_} {name}:'
                            ' {constraints}'
                            ' {schema[description]}'.format(**locals())))
                    else:
                        output.append((
                            name,
                            '{type_} {name}:'
                            ' {schema[description]}'.format(**locals())))

                else:
                    if constraints:
                        output.append(
                            (name,
                             '{type_} {name}:'
                             ' {constraints}'.format(**locals())))
                    else:
                        output.append(
                            (name,
                             '{type_} {name}'.format(**locals())))

    _convert(schema)

    for _, render in sorted(output):
        yield '{} {}'.format(directive, render)


def _example_v3(media_type_objects, method=None, endpoint=None, status=None,
                nb_indent=0):
    """
    Format examples in `Media Type Object` openapi v3 to HTTP request or
    HTTP response example.
    If method and endpoint is provided, this fonction prints a request example
    else status should be provided to print a response example.

    Args:
        - media_type_objects (Dict[str, Dict]): Dict containing
            Media Type Objects.
        - method: The HTTP method to use in example.
        - endpoint: The HTTP route to use in example.
        - status: The HTTP status to use in example.
    """
    # TODO: According to the openapi 3.0.0 spec, we should get example in
    # `schema` if the `example` or `examples` key is not provided.
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#media-type-object

    indent = '   '
    extra_indent = indent * nb_indent

    if method is not None:
        method = method.upper()
    else:
        status_text = http_status_codes.get(int(status), '-')

    for content_type, content in media_type_objects.items():
        examples = content.get('examples')
        if examples is None:
            examples = {}
            if 'example' in content:
                if method is None:
                    examples['Example response'] = {
                        'value': content['example']
                    }
                else:
                    examples['Example request'] = {
                        'value': content['example']
                    }

        for example_name, example in examples.items():
            if 'summary' in example:
                example_title = '{example_name} - {example[summary]}'.format(
                    **locals())
            else:
                example_title = example_name

            yield ''
            yield '{extra_indent}**{example_title}:**'.format(**locals())
            yield ''
            yield '{extra_indent}.. sourcecode:: http'.format(**locals())
            yield ''

            # Print http response example
            if method:
                yield '{extra_indent}{indent}{method} {endpoint} HTTP/1.1' \
                    .format(**locals())
                yield '{extra_indent}{indent}Host: example.com' \
                    .format(**locals())
                yield '{extra_indent}{indent}Content-Type: {content_type}' \
                    .format(**locals())

            # Print http request example
            else:
                yield '{extra_indent}{indent}HTTP/1.1 {status} {status_text}' \
                    .format(**locals())
                yield '{extra_indent}{indent}Content-Type: {content_type}' \
                    .format(**locals())

            yield ''
            for example_line in example['value'].splitlines():
                yield '{extra_indent}{indent}{example_line}'.format(**locals())
            yield ''


def _httpresource_v3(endpoint, method, properties):
    parameters = properties.get('parameters', [])
    responses = properties['responses']
    indent = '   '

    yield '.. http:{0}:: {1}'.format(method, endpoint)
    yield '   :synopsis: {0}'.format(properties.get('summary', 'null'))
    yield ''

    if 'summary' in properties:
        for line in properties['summary'].splitlines():
            yield '{indent}**{line}**'.format(**locals())
        yield ''

    if 'description' in properties:
        for line in properties['description'].splitlines():
            yield '{indent}{line}'.format(**locals())
        yield ''

    for param in filter(lambda p: p['in'] == 'path', parameters):
        yield indent + ':param {type} {name}:'.format(
            type=param['schema']['type'],
            name=param['name'])

        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print request's query params
    for param in filter(lambda p: p['in'] == 'query', parameters):
        yield indent + ':query {type} {name}:'.format(
            type=param['schema']['type'],
            name=param['name'])
        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print shema request body:
    request_content = properties.get('requestBody', {}).get('content', {})
    for content_type, content in request_content.items():
        if content_type == 'application/json' and 'schema' in content:
            yield ''
            for line in convert_json_schema(content['schema']):
                yield '{indent}{line}'.format(**locals())
            yield ''

    # print request example
    for line in _example_v3(
            request_content, method, endpoint=endpoint, nb_indent=1):
        yield line

    # print response status codes
    for status, response in responses.items():
        yield '{indent}:status {status}:'.format(**locals())
        for line in response['description'].splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

        # print shema response body:
        # note:
        #  Sphinx htmldomain merge schema so we cannot display a shema for
        #  each HTTP response type, we only display the schema of success.
        if int(status) in (200, 201):
            response_content = response.get('content', {})
            for content_type, content in response_content.items():
                if content_type == 'application/json' and 'schema' in content:
                    yield ''
                    for line in convert_json_schema(content['schema'], directive=':>json'):
                        yield '{indent}{line}'.format(**locals())
                    yield ''

        # print response example
        for line in _example_v3(response_content, status=status, nb_indent=2):
            yield line

    # print request header params
    for param in filter(lambda p: p['in'] == 'header', parameters):
        yield indent + ':reqheader {name}:'.format(**param)
        for line in param.get('description', '').splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print response headers
    for status, response in responses.items():
        for headername, header in response.get('headers', {}).items():
            yield indent + ':resheader {name}:'.format(name=headername)
            for line in header['description'].splitlines():
                yield '{indent}{indent}{line}'.format(**locals())

    yield ''


def _normalize_spec(spec, **options):
    # OpenAPI spec may contain JSON references, so we need resolve them
    # before we access the actual values trying to build an httpdomain
    # markup. Since JSON references may be relative, it's crucial to
    # pass a document URI in order to properly resolve them.
    spec = _resolve_refs(options.get('uri', ''), spec)

    # OpenAPI spec may contain common endpoint's parameters top-level.
    # In order to do not place if-s around the code to handle special
    # cases, let's normalize the spec and push common parameters inside
    # endpoints definitions.
    for endpoint in spec['paths'].values():
        parameters = endpoint.pop('parameters', [])
        for method in endpoint.values():
            method.setdefault('parameters', [])
            method['parameters'].extend(parameters)


def openapi2httpdomain(spec, **options):
    generators = []
    spec_version = spec.get('openapi', spec.get('swagger', '2.0'))
    if spec_version.startswith('2.'):
        httpresource = _httpresource_v2
    elif spec_version.startswith('3.'):
        httpresource = _httpresource_v3

    # OpenAPI spec may contain JSON references, common properties, etc.
    # Trying to render the spec "As Is" will require to put multiple
    # if-s around the code. In order to simplify flow, let's make the
    # spec to have only one (expected) schema, i.e. normalize it.
    _normalize_spec(spec, **options)

    # If 'paths' are passed we've got to ensure they exist within an OpenAPI
    # spec; otherwise raise error and ask user to fix that.
    if 'paths' in options:
        if not set(options['paths']).issubset(spec['paths']):
            raise ValueError(
                'One or more paths are not defined in the spec: %s.' % (
                    ', '.join(set(options['paths']) - set(spec['paths'])),
                )
            )

    for endpoint in options.get('paths', spec['paths']):
        for method, properties in spec['paths'][endpoint].items():
            generators.append(httpresource(endpoint, method, properties))

    return iter(itertools.chain(*generators))


class OpenApi(Directive):

    required_arguments = 1                  # path to openapi spec
    final_argument_whitespace = True        # path may contain whitespaces
    option_spec = {
        'encoding': directives.encoding,    # useful for non-ascii cases :)
        'paths': lambda s: s.split(),       # endpoints to be rendered
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
        with io.open(abspath, 'rt', encoding=encoding) as stream:
            spec = yaml.load(stream, _YamlOrderedLoader)

        # URI parameter is crucial for resolving relative references. So
        # we need to set this option properly as it's used later down the
        # stack.
        self.options.setdefault('uri', 'file://%s' % abspath)

        # reStructuredText DOM manipulation is pretty tricky task. It requires
        # passing dozen arguments which is not easy without well-documented
        # internals. So the idea here is to represent OpenAPI spec as
        # reStructuredText in-memory text and parse it in order to produce a
        # real DOM.
        viewlist = ViewList()
        for line in openapi2httpdomain(spec, **self.options):
            print(line)
            viewlist.append(line, '<openapi>')

        # Parse reStructuredText contained in `viewlist` and return produced
        # DOM nodes.
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, viewlist, node)
        return node.children


def setup(app):
    app.setup_extension('sphinxcontrib.httpdomain')
    app.add_directive('openapi', OpenApi)
