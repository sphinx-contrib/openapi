"""
    sphinxcontrib.openapi.openapi30
    -------------------------------

    The OpenAPI 3.0.0 spec renderer. Based on ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

import copy

import collections
import collections.abc

from datetime import datetime
import itertools
import json
import re
from urllib import parse
from http.client import responses as http_status_codes

from sphinx.util import logging

from sphinxcontrib.openapi import utils


LOG = logging.getLogger(__name__)

# https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.0.md#data-types
_TYPE_MAPPING = {
    ('integer', 'int32'): 1,  # integer
    ('integer', 'int64'): 1,  # long
    ('number', 'float'): 1.0,  # float
    ('number', 'double'): 1.0,  # double
    ('boolean', None): True,  # boolean
    ('string', None): 'string',  # string
    ('string', 'byte'): 'c3RyaW5n',  # b'string' encoded in base64,  # byte
    ('string', 'binary'): '01010101',  # binary
    ('string', 'date'): datetime.now().date().isoformat(),  # date
    ('string', 'date-time'): datetime.now().isoformat(),  # dateTime
    ('string', 'password'): '********',  # password

    # custom extensions to handle common formats
    ('string', 'email'): 'name@example.com',
    ('string', 'zip-code'): '90210',
    ('string', 'uri'): 'https://example.com',

    # additional fallthrough cases
    ('integer', None): 1,  # integer
    ('number', None): 1.0,  # <fallthrough>
}

_READONLY_PROPERTY = object()  # sentinel for values not included in requests


def _dict_merge(dct, merge_dct):
    """Recursive dict merge.

    Inspired by :meth:``dict.update()``, instead of updating only top-level
    keys, dict_merge recurses down into dicts nested to an arbitrary depth,
    updating keys. The ``merge_dct`` is merged into ``dct``.

    From https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

    Arguments:
        dct: dict onto which the merge is executed
        merge_dct: dct merged into dct
    """
    for k in merge_dct.keys():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.abc.Mapping)):
            _dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def _parse_schema(schema, method):
    """
    Convert a Schema Object to a Python object.

    Args:
        schema: An ``OrderedDict`` representing the schema object.
    """
    if method and schema.get('readOnly', False):
        return _READONLY_PROPERTY

    # allOf: Must be valid against all of the subschemas
    if 'allOf' in schema:
        schema_ = copy.deepcopy(schema['allOf'][0])
        for x in schema['allOf'][1:]:
            _dict_merge(schema_, x)

        return _parse_schema(schema_, method)

    # anyOf: Must be valid against any of the subschemas
    # TODO(stephenfin): Handle anyOf

    # oneOf: Must be valid against exactly one of the subschemas
    if 'oneOf' in schema:
        # we only show the first one since we can't show everything
        return _parse_schema(schema['oneOf'][0], method)

    if 'enum' in schema:
        # we only show the first one since we can't show everything
        return schema['enum'][0]

    schema_type = schema.get('type', 'object')

    if schema_type == 'array':
        # special case oneOf and anyOf so that we can show examples for all
        # possible combinations
        if 'oneOf' in schema['items']:
            return [
                _parse_schema(x, method) for x in schema['items']['oneOf']
            ]

        if 'anyOf' in schema['items']:
            return [
                _parse_schema(x, method) for x in schema['items']['anyOf']
            ]

        return [_parse_schema(schema['items'], method)]

    if schema_type == 'object':
        if method and 'properties' in schema and \
                all(v.get('readOnly', False)
                    for v in schema['properties'].values()):
            return _READONLY_PROPERTY

        results = []
        for name, prop in schema.get('properties', {}).items():
            result = _parse_schema(prop, method)
            if result != _READONLY_PROPERTY:
                results.append((name, result))

        return collections.OrderedDict(results)

    if (schema_type, schema.get('format')) in _TYPE_MAPPING:
        return _TYPE_MAPPING[(schema_type, schema.get('format'))]

    return _TYPE_MAPPING[(schema_type, None)]  # unrecognized format


def _example(media_type_objects, method=None, endpoint=None, status=None,
             nb_indent=0, profile=None):
    """
    Format examples in `Media Type Object` openapi v3 to HTTP request or
    HTTP response example.
    If method and endpoint is provided, this function prints a request example
    else status should be provided to print a response example.

    Arguments:
        media_type_objects (Dict[str, Dict]): Dict containing
            Media Type Objects.
        method: The HTTP method to use in example.
        endpoint: The HTTP route to use in example.
        status: The HTTP status to use in example.
    """
    indent = '   '
    extra_indent = indent * nb_indent

    if method is not None:
        method = method.upper()
    else:
        try:
            # one of possible values for status might be 'default'.
            # in the case, just fallback to '-'
            status_text = http_status_codes[int(status)]
        except (ValueError, KeyError):
            status_text = '-'

    # Provide request samples for GET requests
    if method == 'GET':
        media_type_objects[''] = {
            'examples': {'default': {'summary': 'Example Request', 'value': ''}}}

    for content_type, content in media_type_objects.items():
        examples = content.get('examples')
        example = content.get('example')

        # Try to get the example from the schema
        if example is None and 'schema' in content:
            example = content['schema'].get('example')

        if examples is None:
            examples = {}
            if method is None:
                if example is None:
                    continue
                examples['default'] = {
                    'value': example
                }
            else:
                if not example:
                    if re.match(r"application/[a-zA-Z\+\.]*json", content_type) is \
                            None:
                        LOG.info('skipping non-JSON example generation.')
                        continue
                    example = _parse_schema(content['schema'], method=method)
                examples['default'] = {
                    'value': example,
                }

        for example in examples.values():
            # According to OpenAPI v3 specs, string examples should be left unchanged
            if not isinstance(example['value'], str):
                example['value'] = json.dumps(
                    example['value'], indent=4, separators=(',', ': '))

        for example_name, example in examples.items():
            if 'summary' in example:
                example_title = '{example[summary]}'.format(**locals())
            else:
                example_title = example_name
                if example_title == 'default':
                    if method is None:
                        example_title = 'Example Respone'
                    else:
                        example_title = 'Example Request'

            yield ''
            yield '{extra_indent}**{example_title}:**'.format(**locals())
            yield ''
            yield '{extra_indent}.. sourcecode:: http'.format(**locals())
            yield ''

            # Print http request example
            if method:
                yield '{extra_indent}{indent}{method} {endpoint} HTTP/1.1' \
                    .format(**locals())
                yield '{extra_indent}{indent}Host: my.scalr.io' \
                    .format(**locals())
                if content_type:
                    yield '{extra_indent}{indent}Content-Type: {content_type}'\
                        .format(**locals())
                if profile:
                    yield f'{extra_indent}{indent}Prefer: profile={profile}'

            # Print http response example
            else:
                yield '{extra_indent}{indent}HTTP/1.1 {status} {status_text}' \
                    .format(**locals())
                yield '{extra_indent}{indent}Content-Type: {content_type}' \
                    .format(**locals())
                if profile:
                    yield f'{extra_indent}{indent}Preference-Applied: profile={profile}'

            yield ''
            for example_line in example['value'].splitlines():
                yield '{extra_indent}{indent}{example_line}'.format(**locals())
            if example['value'].splitlines():
                yield ''


def _httpresource(endpoint, method, properties, convert, render_examples,
                  render_request, profile=None):
    # https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.0.md#operation-object
    parameters = properties.get('parameters', [])
    responses = properties['responses']
    query_param_examples = []
    indent = '   '

    operation_title = properties.get('summary', '')

    yield operation_title
    yield '^' * len(operation_title)
    yield ''
    yield '.. http:{0}:: {1}'.format(method, endpoint)
    yield '   :synopsis: {0}'.format(properties.get('summary', 'null'))
    yield ''

    if 'description' in properties:
        for line in convert(properties['description']).splitlines():
            yield '{indent}{line}'.format(**locals())
        yield ''

    # print request's path params
    for param in filter(lambda p: p['in'] == 'path', parameters):
        yield indent + ':param {type} {name}:'.format(
            type=param['schema']['type'],
            name=param['name'])

        for line in convert(param.get('description', '')).splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

    # print request's query params
    for param in filter(lambda p: p['in'] == 'query', parameters):
        yield indent + ':query {type} {name}:'.format(
            type=param['schema']['type'],
            name=param['name'])
        for line in convert(param.get('description', '')).splitlines():
            yield '{indent}{indent}{line}'.format(**locals())
        _enum = param.get('schema', {}).get('items', {}).get('enum')
        if _enum:
            _enum = '*(Available values:* ``' + '``, ``'.join(_enum) + r'``\ *)*'
            yield '{indent}{indent}{_enum}'.format(**locals())
        if param.get('required', False):
            yield '{indent}{indent}(Required)'.format(**locals())
            example = _parse_schema(param['schema'], method)
            example = param.get('example', example)
            if param.get('explode', False) and isinstance(example, list):
                for v in example:
                    query_param_examples.append((param['name'], v))
            elif param.get('explode', False) and isinstance(example, dict):
                for k, v in example.items():
                    query_param_examples.append((k, v))
            else:
                query_param_examples.append((param['name'], example))

    # print request content
    if render_request:
        request_content = properties.get('requestBody', {}).get('content', {})
        if request_content and 'application/vnd.api+json' in request_content:
            schema = request_content['application/vnd.api+json']['schema']
            yield '{indent}**Request body:**'.format(**locals())
            yield ''
            yield ''
            for line in _resource_definition(schema, convert=convert, is_request=True):
                yield line

    # print request example
    if render_examples:
        endpoint_examples = endpoint
        if query_param_examples:
            endpoint_examples = endpoint + "?" + \
                parse.urlencode(query_param_examples)

        # print request example
        request_content = properties.get('requestBody', {}).get('content', {})
        for line in _example(
                request_content,
                method,
                endpoint=endpoint_examples,
                nb_indent=1,
                profile=profile):
            yield line

    # print response status codes
    for status, response in responses.items():
        yield '{indent}:status {status}:'.format(**locals())
        for line in convert(response['description']).splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

        # print response example
        if render_examples:
            for line in _example(
                    response.get('content', {}), status=status, nb_indent=2, profile=profile):
                yield line

    # print request header params
    for param in filter(lambda p: p['in'] == 'header', parameters):
        yield indent + ':reqheader {name}:'.format(**param)
        for line in convert(param.get('description', '')).splitlines():
            yield '{indent}{indent}{line}'.format(**locals())
        if param.get('required', False):
            yield '{indent}{indent}(Required)'.format(**locals())

    # print response headers
    for status, response in responses.items():
        for headername, header in response.get('headers', {}).items():
            yield indent + ':resheader {name}:'.format(name=headername)
            for line in convert(header['description']).splitlines():
                yield '{indent}{indent}{line}'.format(**locals())

    for cb_name, cb_specs in properties.get('callbacks', {}).items():
        yield ''
        yield indent + '.. admonition:: Callback: ' + cb_name
        yield ''

        for cb_endpoint in cb_specs.keys():
            for cb_method, cb_properties in cb_specs[cb_endpoint].items():
                for line in _httpresource(
                        cb_endpoint,
                        cb_method,
                        cb_properties,
                        convert=convert,
                        render_examples=render_examples,
                        render_request=render_request,
                        profile=profile):
                    if line:
                        yield indent+indent+line
                    else:
                        yield ''

    yield ''


def _header(title, symbol='='):
    yield title
    yield symbol * len(title)
    yield ''


def _resource_description(schema, convert):
    indent = "   "
    if schema.get("description"):
        for line in convert(schema.get("description")).splitlines():
            yield "{indent}{line}".format(**locals())
        yield ""
        yield ""


def _resource_definition(schema, convert, is_request=False):
    indent = "   "

    yield "{indent}.. role:: raw-html(raw)".format(**locals())
    yield "{indent}   :format: html".format(**locals())
    yield "".format(**locals())
    yield "".format(**locals())
    yield "{indent}.. list-table::".format(**locals())
    yield "{indent}{indent}:header-rows: 1".format(**locals())
    yield "{indent}{indent}:widths: 33 67".format(**locals())
    yield "{indent}{indent}:class: resource-definition".format(**locals())
    yield ""
    yield "{indent}{indent}* - Key path".format(**locals())
    yield "{indent}{indent}  - Description".format(**locals())
    for line in _render_properties(schema, convert, is_request):
        yield line


def _render_properties(schema, convert, is_request=False, parent=None):
    indent = "      "
    properties = copy.deepcopy(schema.get("properties", {}))
    reordered_properties = {}
    for k in ["type", "id", "attributes", "relationships"]:
        if k in properties:
            reordered_properties[k] = properties.pop(k)
    properties = {**reordered_properties, **properties}
    for key, property_schema in properties.items():
        if (is_request and property_schema.get("readOnly", False)) or (
            not is_request and property_schema.get("writeOnly", False)
        ):
            continue
        type = property_schema.get("type", "object")
        is_required = key in schema.get("required", [])
        description = property_schema.get("description", "")
        enum = ""
        if len(property_schema.get("enum", [])) > 0:
            enum = convert(
                "Available values: `" + "`, `".join(property_schema.get("enum", [])) + "`"
            )
        key = f"{parent}.{key}" if parent else key
        _key = (
            (
                f"**{key}**"
                + r'\ :raw-html:`<span style="color:red;" title="required">*</span>`'
            )
            if is_required
            else f"**{key}**"
        )
        sub_props = property_schema.get("properties", {})
        if type == "object" and len(sub_props) > 0:
            if key != "data" and description:
                yield "{indent}* - {_key} (*{type}*)".format(**locals())
                yield ""
                yield "{indent}  - ".format(**locals())
                for line in convert(description).splitlines():
                    yield "{indent}{indent} {line}".format(**locals())
            for line in _render_properties(
                property_schema, convert, is_request, parent=key
            ):
                yield line
        else:
            yield "{indent}* - {_key} (*{type}*)".format(**locals())
            yield ""
            if enum:
                yield "{indent}     | {enum}".format(**locals())
            yield "{indent}  - ".format(**locals())
            for line in convert(description).splitlines():
                yield "{indent}{indent} {line}".format(**locals())


def openapihttpdomain(spec, **options):
    generators = []

    # OpenAPI spec may contain JSON references, common properties, etc.
    # Trying to render the spec "As Is" will require to put multiple
    # if-s around the code. In order to simplify flow, let's make the
    # spec to have only one (expected) schema, i.e. normalize it.
    utils.normalize_spec(spec, **options)

    # Paths list to be processed
    paths = []

    # If 'paths' are passed we've got to ensure they exist within an OpenAPI
    # spec; otherwise raise error and ask user to fix that.
    if 'paths' in options:
        if not set(options['paths']).issubset(spec['paths']):
            raise ValueError(
                'One or more paths are not defined in the spec: %s.' % (
                    ', '.join(set(options['paths']) - set(spec['paths'])),
                )
            )
        paths = options['paths']

    # Check against regular expressions to be included
    if 'include' in options:
        for i in options['include']:
            ir = re.compile(i)
            for path in spec['paths']:
                if ir.match(path):
                    paths.append(path)

    # If no include nor paths option, then take full path
    if 'include' not in options and 'paths' not in options:
        paths = spec['paths']

    included_tags = None
    if 'tags' in options:
        included_tags = options['tags']

    # Remove paths matching regexp
    if 'exclude' in options:
        _paths = []
        for e in options['exclude']:
            er = re.compile(e)
            for path in paths:
                if not er.match(path):
                    _paths.append(path)
        paths = _paths

    render_request = False
    if 'request' in options:
        render_request = True

    convert = utils.get_text_converter(options)

    # https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.0.md#paths-object
    if 'group' in options:
        groups = {}
        tags = {x['name']: x.get('description', x['name']) for x in spec.get('tags', {})}
        group_resources = {}

        for endpoint in paths:
            for method, properties in spec['paths'][endpoint].items():
                key = properties.get('tags', [''])[0]
                key = tags.get(key) if key in tags.keys() else key
                resource = properties.get('x-resource', None)
                if resource:
                    group_resources.setdefault(key, set([])).add(resource)
                groups.setdefault(key, []).append(_httpresource(
                    endpoint,
                    method,
                    properties,
                    convert,
                    render_examples='examples' in options,
                    render_request=render_request,
                    profile=options.get("profile")))

        groups = collections.OrderedDict(sorted(groups.items()))
        for key in groups.keys():
            if included_tags is not None and key not in included_tags:
                continue
            if group_resources.get(key):
                for r in group_resources.get(key):
                    generators.append(_header(f"The {r} resource", '^'))
                    generators.append(
                        _resource_description(spec["components"]["schemas"][r], convert)
                    )
                    generators.append(
                        _resource_definition(spec['components']['schemas'][r], convert)
                    )
            generators.extend(groups[key])
    else:
        for endpoint in paths:
            for method, properties in spec['paths'][endpoint].items():
                tag = properties.get('tags', [''])[0]
                if included_tags is not None and tag not in included_tags:
                    continue
                generators.append(_httpresource(
                    endpoint,
                    method,
                    properties,
                    convert,
                    render_examples='examples' in options,
                    render_request=render_request,
                    profile=options.get("profile")))

    return iter(itertools.chain(*generators))
