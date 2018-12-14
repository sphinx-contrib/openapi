"""
    sphinxcontrib.openapi.openapi20
    -------------------------------

    The OpenAPI 2.0 (f.k.a. Swagger) spec renderer. Based on
    ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

import itertools

from sphinxcontrib.openapi import utils


def _httpresource(endpoint, method, properties):
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


def openapihttpdomain(spec, **options):
    if 'examples' in options:
        raise ValueError(
            'Rendering examples is not supported for OpenAPI v2.x specs.')

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

    for endpoint in options.get('paths', spec['paths']):
        for method, properties in spec['paths'][endpoint].items():
            generators.append(_httpresource(endpoint, method, properties))

    return iter(itertools.chain(*generators))
