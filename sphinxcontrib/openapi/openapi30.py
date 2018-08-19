"""
    sphinxcontrib.openapi.openapi30
    -------------------------------

    The OpenAPI 3.0.0 spec renderer. Based on ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

import itertools

from sphinxcontrib.openapi import utils

try:
    from httplib import responses as http_status_codes  # python2
except ImportError:
    from http.client import responses as http_status_codes  # python3


def _example(media_type_objects, method=None, endpoint=None, status=None,
             nb_indent=0):
    """
    Format examples in `Media Type Object` openapi v3 to HTTP request or
    HTTP response example.
    If method and endpoint is provided, this fonction prints a request example
    else status should be provided to print a response example.

    Arguments:
        media_type_objects (Dict[str, Dict]): Dict containing
            Media Type Objects.
        method: The HTTP method to use in example.
        endpoint: The HTTP route to use in example.
        status: The HTTP status to use in example.
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


def _httpresource(endpoint, method, properties):
    # https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.0.md#operation-object
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

    # print request's path params
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

    # print request example
    request_content = properties.get('requestBody', {}).get('content', {})
    for line in _example(
            request_content, method, endpoint=endpoint, nb_indent=1):
        yield line

    # print response status codes
    for status, response in responses.items():
        yield '{indent}:status {status}:'.format(**locals())
        for line in response['description'].splitlines():
            yield '{indent}{indent}{line}'.format(**locals())

        # print response example
        for line in _example(
                response.get('content', {}), status=status, nb_indent=2):
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


def openapihttpdomain(spec, **options):
    generators = []

    # OpenAPI spec may contain JSON references, common properties, etc.
    # Trying to render the spec "As Is" will require to put multiple
    # if-s around the code. In order to simplify flow, let's make the
    # spec to have only one (expected) schema, i.e. normalize it.
    utils.normalize_spec(spec, **options)

    # If 'paths' are passed we've got to ensure they exist within an OpenAPI
    # spec; otherwise raise error and ask user to fix that.
    if 'paths' in options:
        if not set(options['paths']).issubset(spec['paths']):
            raise ValueError(
                'One or more paths are not defined in the spec: %s.' % (
                    ', '.join(set(options['paths']) - set(spec['paths'])),
                )
            )

    # https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.0.md#paths-object
    for endpoint in options.get('paths', spec['paths']):
        for method, properties in spec['paths'][endpoint].items():
            generators.append(_httpresource(endpoint, method, properties))

    return iter(itertools.chain(*generators))
