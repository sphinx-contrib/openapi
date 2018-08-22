"""
    tests.test_openapi
    ------------------

    Tests some stuff of ``sphinxcontrib.openapi`` module.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

import os
import textwrap
import collections

import pytest

from sphinxcontrib import openapi


class TestOpenApi2HttpDomain(object):

    def test_basic(self):
        text = '\n'.join(openapi.openapi2httpdomain({
            'paths': {
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
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'An array of resources.',
                                'headers': {
                                    'ETag': {
                                        'description': 'Resource ETag.',
                                        'type': 'string'
                                    },
                                },
                            },
                        },
                    },
                },
            },
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

    def test_basic_v3(self):
        text = '\n'.join(openapi.openapi2httpdomain({
            'openapi': '3.0.0',
            'paths': {
                '/resources/{kind}': {
                    'get': {
                        'summary': 'List Resources',
                        'description': '~ some useful description ~',
                        'parameters': [
                            {
                                'name': 'kind',
                                'in': 'path',
                                'schema': {'type': 'string'},
                                'description': 'Kind of resource to list.',
                            },
                            {
                                'name': 'limit',
                                'in': 'query',
                                'schema': {'type': 'integer'},
                                'description': 'Show up to `limit` entries.',
                            },
                            {
                                'name': 'If-None-Match',
                                'in': 'header',
                                'schema': {'type': 'string'},
                                'description': 'Last known resource ETag.'
                            },
                        ],
                        'requestBody': {
                            'content': {
                                'application/json':  {
                                    'example': '{"foo2": "bar2"}'
                                }
                            }
                        },
                        'responses': {
                            '200': {
                                'description': 'An array of resources.',
                                'content': {
                                    'application/json': {
                                        'example': '{"foo": "bar"}'
                                    }
                                }
                            },
                        },
                    },
                },
            },
        }))
        open('/tmp/toto', 'w').write(text)
        assert text == textwrap.dedent('''
            .. http:get:: /resources/{kind}
               :synopsis: List Resources

               **List Resources**

               ~ some useful description ~

               :param string kind:
                  Kind of resource to list.
               :query integer limit:
                  Show up to `limit` entries.

               **Example request:**

               .. sourcecode:: http

                  GET /resources/{kind} HTTP/1.1
                  Host: example.com
                  Content-Type: application/json

                  {"foo2": "bar2"}

               :status 200:
                  An array of resources.

                  **Example response:**

                  .. sourcecode:: http

                     HTTP/1.1 200 OK
                     Content-Type: application/json

                     {"foo": "bar"}

               :reqheader If-None-Match:
                  Last known resource ETag.
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

    def test_path_option(self):
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

        text = '\n'.join(openapi.openapi2httpdomain(spec, paths=[
            '/resource_a',
        ]))
        assert text == textwrap.dedent('''
            .. http:get:: /resource_a
               :synopsis: null

               resource a

               :status 200:
                  ok
        ''').lstrip()

    def test_root_parameters(self):
        spec = {'paths': {}}
        spec['paths']['/resources/{name}'] = collections.OrderedDict()

        spec['paths']['/resources/{name}']['parameters'] = [
            {
                'name': 'name',
                'in': 'path',
                'type': 'string',
                'description': 'The name of the resource.',
            }
        ]
        spec['paths']['/resources/{name}']['get'] = {
            'summary': 'Fetch a Resource',
            'description': '~ some useful description ~',
            'responses': {
                '200': {
                    'description': 'The fetched resource.',
                },
            },
        }
        spec['paths']['/resources/{name}']['put'] = {
            'summary': 'Modify a Resource',
            'description': '~ some useful description ~',
            'responses': {
                '200': {
                    'description': 'The modified resource.',
                },
            },
        }

        text = '\n'.join(openapi.openapi2httpdomain(spec))

        assert text == textwrap.dedent('''
            .. http:get:: /resources/{name}
               :synopsis: Fetch a Resource

               **Fetch a Resource**

               ~ some useful description ~

               :param string name:
                  The name of the resource.
               :status 200:
                  The fetched resource.

            .. http:put:: /resources/{name}
               :synopsis: Modify a Resource

               **Modify a Resource**

               ~ some useful description ~

               :param string name:
                  The name of the resource.
               :status 200:
                  The modified resource.
        ''').lstrip()

    def test_path_invalid(self):
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

        with pytest.raises(ValueError) as exc:
            openapi.openapi2httpdomain(spec, paths=[
                '/resource_a',
                '/resource_invalid_name',
            ])

        assert str(exc.value) == (
            'One or more paths are not defined in the spec: '
            '/resource_invalid_name.'
        )

    def test_unicode_is_allowed(self):
        spec = {
            'paths': {
                '/resource_a': {
                    'get': {
                        'description': '\u041f',
                        'responses': {
                            '200': {'description': 'ok'}
                        }
                    }
                }
            }
        }

        text = '\n'.join(openapi.openapi2httpdomain(spec))

        assert text == textwrap.dedent('''
            .. http:get:: /resource_a
               :synopsis: null

               \u041f

               :status 200:
                  ok
        ''').lstrip()


class TestResolveRefs(object):

    def test_ref_resolving(self):
        data = {
            'foo': {
                'a': 13,
                'b': {
                    'c': True,
                }
            },
            'bar': {
                '$ref': '#/foo/b'
            },
            'baz': [
                {'$ref': '#/foo/a'},
                {'$ref': '#/foo/b'},
                'batman',
            ]
        }

        assert openapi._resolve_refs('', data) == {
            'foo': {
                'a': 13,
                'b': {
                    'c': True,
                }
            },
            'bar': {
                'c': True,
            },
            'baz': [
                13,
                {'c': True},
                'batman',
            ]
        }

    def test_relative_ref_resolving_on_fs(self):
        baseuri = 'file://%s' % os.path.abspath(__file__)
        data = {
            'bar': {
                '$ref': 'testdata/foo.json#/foo/b',
            }
        }

        assert openapi._resolve_refs(baseuri, data) == {
            'bar': {
                'c': True,
            }
        }


class TestConvertJsonSchema(object):
    
    schema = {
      'type': 'object',
      'required': ['name', 'surprise'],
      'properties': {
        'name': {
          'type': 'string',
          'description': 'The name of user'},
        'alias': {
          'type': 'array',
          'items': {
            'type': 'string'},
          'description': 'The list of user alias'},
        'id': {
          'type': 'integer',
          'description': 'the id of user',
          'readOnly': True},
        'surprise': {
          'type': 'string'},
        'secret': {
          'type': 'string',
          'readOnly': True}}}

    result = list(openapi.convert_json_schema(schema))

    def test_required_field_with_description(self):
        assert ':<json string name: (required) The name of user' in self.result

    def test_required_field_without_description(self):
        assert ':<json string surprise: (required)' in self.result

    def test_array_field(self):
        assert ':<json string alias[]' in self.result

    def test_read_only_field_with_description(self):
        assert ':<json integer id: (read only) the id of user' in self.result

    def test_read_only_field_without_description(self):
        assert ':<json string secret: (read only)' in self.result

    def test_nested_schema(self):
        schema = {
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'The name of user'
                },
                'friends': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string',
                                'readOnly': True
                            },
                            'age': {'type': 'integer'}
                        }
                    },
                    'description': 'The list of user alias'
                },
                'id': {
                    'type': 'integer',
                    'description': 'the id of user',
                    'readOnly': True
                },
                'car': {
                    'type': 'object',
                    'properties': {
                        'provider': {'type': 'string'},
                        'date': {
                            'type': 'string',
                            'description': 'The car of user'
                        }
                    }
                }
            }
        }

        result = '\n'.join(openapi.convert_json_schema(schema))
        
        expected = textwrap.dedent('''
            :<json string car.date: The car of user
            :<json string car.provider
            :<json integer friends[].age
            :<json string friends[].name: (read only)
            :<json integer id: (read only) the id of user
            :<json string name: (required) The name of user'''.strip('\n'))

        assert result == expected 

