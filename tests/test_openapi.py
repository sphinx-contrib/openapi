"""
    tests.test_openapi
    ------------------

    Tests some stuff of ``sphinxcontrib.openapi`` module.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

import textwrap
import collections

from sphinxcontrib import openapi


class TestOpenApi2HttpDomain(object):

    def test_basic(self):
        text = '\n'.join(openapi.openapi2httpdomain({
            'paths': collections.OrderedDict({
                '/resources/{kind}': {
                    'get': {
                        'summary': 'List Resources',
                        'description': '~ some useful description ~',
                        'parameters': [
                            {
                                'name': 'kind',
                                'in': 'path',
                                'type': 'string',
                                'description': 'Kind of resource to list.',
                            },
                            {
                                'name': 'limit',
                                'in': 'query',
                                'type': 'integer',
                                'description': 'Show up to `limit` entries.',
                            },
                            {
                                'name': 'If-None-Match',
                                'in': 'header',
                                'type': 'string',
                                'description': 'Last known resource ETag.'
                            }
                        ],
                        'responses': {
                            '200': {
                                'description': 'An array of resources.',
                                'headers': {
                                    'ETag': {
                                        'description': 'Resource ETag.',
                                        'type': 'string'
                                    }
                                }
                            }
                        }
                    },
                }
            })
        }))

        assert text == textwrap.dedent('''
            .. http:get:: /resources/{kind}
               :synopsis: List Resources

               **List Resources**

               ~ some useful description ~

               :param string kind:
                  Kind of resource to list.
               :query integer limit:
                  Show up to `limit` entries.
               :status 200:
                  An array of resources.
               :reqheader If-None-Match:
                  Last known resource ETag.
               :resheader ETag:
                  Resource ETag.
        ''').lstrip()

    def test_two_resources(self):
        spec = collections.defaultdict(collections.OrderedDict)
        spec['paths']['/resource_a'] = {
            'get': {
                'description': 'resource a',
                'responses': {
                    '200': {'description': 'ok'},
                }
            }
        }
        spec['paths']['/resource_b'] = {
            'post': {
                'description': 'resource b',
                'responses': {
                    '404': {'description': 'error'},
                }
            }
        }

        text = '\n'.join(openapi.openapi2httpdomain(spec))
        assert text == textwrap.dedent('''
            .. http:get:: /resource_a
               :synopsis: null

               resource a

               :status 200:
                  ok

            .. http:post:: /resource_b
               :synopsis: null

               resource b

               :status 404:
                  error
        ''').lstrip()
