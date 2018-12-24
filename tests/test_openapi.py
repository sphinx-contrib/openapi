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

import py
import pytest

from sphinxcontrib.openapi import openapi20
from sphinxcontrib.openapi import openapi30
from sphinxcontrib.openapi import utils


class TestOpenApi2HttpDomain(object):

    def test_basic(self):
        text = '\n'.join(openapi20.openapihttpdomain({
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

        text = '\n'.join(openapi20.openapihttpdomain(spec))
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

        text = '\n'.join(openapi20.openapihttpdomain(spec, paths=[
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

        text = '\n'.join(openapi20.openapihttpdomain(spec))

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
            openapi20.openapihttpdomain(spec, paths=[
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

        text = '\n'.join(openapi20.openapihttpdomain(spec))

        assert text == textwrap.dedent('''
            .. http:get:: /resource_a
               :synopsis: null

               \u041f

               :status 200:
                  ok
        ''').lstrip()


class TestOpenApi3HttpDomain(object):

    def test_basic(self):
        text = '\n'.join(openapi30.openapihttpdomain({
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
        ''').lstrip()

    def test_groups(self):
        text = '\n'.join(openapi30.openapihttpdomain({
            'openapi': '3.0.0',
            'paths': collections.OrderedDict([
                ('/', {
                    'get': {
                        'summary': 'Index',
                        'description': '~ some useful description ~',
                        'responses': {
                            '200': {
                                'description': 'Index',
                                'content': {
                                    'application/json': {
                                        'pets': 'https://example.com/api/pets',
                                        'tags': 'https://example.com/api/tags',
                                    }
                                }
                            },
                        },
                    },
                }),
                ('/pets', {
                    'get': {
                        'summary': 'List Pets',
                        'description': '~ some useful description ~',
                        'responses': {
                            '200': {
                                'description': 'Pets',
                                'content': {
                                    'application/json': [
                                        {
                                            'example': '{"foo": "bar"}'
                                        },
                                    ],
                                },
                            },
                        },
                        'tags': [
                            'pets',
                        ],
                    },
                }),
                ('/pets/{name}', {
                    'get': {
                        'summary': 'Show Pet',
                        'description': '~ some useful description ~',
                        'parameters': [
                            {
                                'name': 'name',
                                'in': 'path',
                                'schema': {'type': 'string'},
                                'description': 'Name of pet.',
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'A Pet',
                                'content': {
                                    'application/json': {
                                        'example': '{"foo": "bar"}'
                                    }
                                }
                            },
                        },
                        'tags': [
                            'pets',
                        ],
                    },
                }),
                ('/tags', {
                    'get': {
                        'summary': 'List Tags',
                        'description': '~ some useful description ~',
                        'responses': {
                            '200': {
                                'description': 'Tags',
                                'content': {
                                    'application/json': [
                                        {
                                            'example': '{"foo": "bar"}'
                                        },
                                    ],
                                }
                            },
                        },
                        'tags': [
                            'tags',
                            'pets',
                        ],
                    },
                }),
            ]),
        }, group=True))
        assert text == textwrap.dedent('''
            default
            =======

            .. http:get:: /
               :synopsis: Index

               **Index**

               ~ some useful description ~

               :status 200:
                  Index

            pets
            ====

            .. http:get:: /pets
               :synopsis: List Pets

               **List Pets**

               ~ some useful description ~

               :status 200:
                  Pets

            .. http:get:: /pets/{name}
               :synopsis: Show Pet

               **Show Pet**

               ~ some useful description ~

               :param string name:
                  Name of pet.
               :status 200:
                  A Pet

            tags
            ====

            .. http:get:: /tags
               :synopsis: List Tags

               **List Tags**

               ~ some useful description ~

               :status 200:
                  Tags
        ''').lstrip()

    def test_example_generation(self):
        text = '\n'.join(openapi30.openapihttpdomain({
            'openapi': '3.0.0',
            'paths': collections.OrderedDict([
                ('/resources/', collections.OrderedDict([
                    ('get', {
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
                        'responses': {
                            '200': {
                                'description': 'An array of resources.',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'array',
                                            'items': {
                                                '$ref': '#/components/schemas/Resource',  # noqa
                                            },
                                        },
                                    }
                                }
                            },
                        },
                    }),
                    ('post', {
                        'summary': 'Create Resource',
                        'description': '~ some useful description ~',
                        'parameters': [],
                        'requestBody': {
                            'content': {
                                'application/json':  {
                                    'schema': {
                                        '$ref': '#/components/schemas/Resource',  # noqa
                                    },
                                }
                            }
                        },
                        'responses': {
                            '200': {
                                'description': 'The created resource.',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            '$ref': '#/components/schemas/Resource',  # noqa
                                        },
                                    }
                                }
                            },
                        },
                    }),
                ])),
                ('/resources/{kind}', collections.OrderedDict([
                    ('get', {
                        'summary': 'Show Resource',
                        'description': '~ some useful description ~',
                        'parameters': [
                            {
                                'name': 'kind',
                                'in': 'path',
                                'schema': {'type': 'string'},
                                'description': 'Kind of resource to list.',
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'The created resource.',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            '$ref': '#/components/schemas/Resource',  # noqa
                                        },
                                    }
                                }
                            },
                        },
                    }),
                    ('patch', {
                        'summary': 'Update Resource (partial)',
                        'description': '~ some useful description ~',
                        'parameters': [
                            {
                                'name': 'kind',
                                'in': 'path',
                                'schema': {'type': 'string'},
                                'description': 'Kind of resource to list.',
                            },
                        ],
                        'requestBody': {
                            'content': {
                                'application/json':  {
                                    'schema': {
                                        '$ref': '#/components/schemas/Resource',  # noqa
                                    },
                                }
                            }
                        },
                        'responses': {
                            '200': {
                                'description': 'The created resource.',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            '$ref': '#/components/schemas/Resource',  # noqa
                                        },
                                    }
                                }
                            },
                        },
                    }),
                ])),
            ]),
            'components': {
                'schemas': {
                    'Resource': {
                        'type': 'object',
                        'properties': collections.OrderedDict([
                            ('kind', {
                                'title': 'Kind',
                                'type': 'string',
                                'readOnly': True,
                            }),
                            ('description', {
                                'title': 'Description',
                                'type': 'string',
                            }),
                        ]),
                    },
                },
            },
        },
        examples=True))

        assert text == textwrap.dedent('''
            .. http:get:: /resources/
               :synopsis: List Resources

               **List Resources**

               ~ some useful description ~

               :param string kind:
                  Kind of resource to list.
               :query integer limit:
                  Show up to `limit` entries.
               :status 200:
                  An array of resources.

                  **Example response:**

                  .. sourcecode:: http

                     HTTP/1.1 200 OK
                     Content-Type: application/json

                     [
                         {
                             "kind": "string",
                             "description": "string"
                         }
                     ]

               :reqheader If-None-Match:
                  Last known resource ETag.

            .. http:post:: /resources/
               :synopsis: Create Resource

               **Create Resource**

               ~ some useful description ~


               **Example request:**

               .. sourcecode:: http

                  POST /resources/ HTTP/1.1
                  Host: example.com
                  Content-Type: application/json

                  {
                      "description": "string"
                  }

               :status 200:
                  The created resource.

                  **Example response:**

                  .. sourcecode:: http

                     HTTP/1.1 200 OK
                     Content-Type: application/json

                     {
                         "kind": "string",
                         "description": "string"
                     }


            .. http:get:: /resources/{kind}
               :synopsis: Show Resource

               **Show Resource**

               ~ some useful description ~

               :param string kind:
                  Kind of resource to list.
               :status 200:
                  The created resource.

                  **Example response:**

                  .. sourcecode:: http

                     HTTP/1.1 200 OK
                     Content-Type: application/json

                     {
                         "kind": "string",
                         "description": "string"
                     }


            .. http:patch:: /resources/{kind}
               :synopsis: Update Resource (partial)

               **Update Resource (partial)**

               ~ some useful description ~

               :param string kind:
                  Kind of resource to list.

               **Example request:**

               .. sourcecode:: http

                  PATCH /resources/{kind} HTTP/1.1
                  Host: example.com
                  Content-Type: application/json

                  {
                      "description": "string"
                  }

               :status 200:
                  The created resource.

                  **Example response:**

                  .. sourcecode:: http

                     HTTP/1.1 200 OK
                     Content-Type: application/json

                     {
                         "kind": "string",
                         "description": "string"
                     }

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

        assert utils._resolve_refs('', data) == {
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

        assert utils._resolve_refs(baseuri, data) == {
            'bar': {
                'c': True,
            }
        }


def test_openapi2_examples(tmpdir, run_sphinx):
    spec = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'OpenAPI-Specification',
        'examples',
        'v2.0',
        'json',
        'uber.json')
    py.path.local(spec).copy(tmpdir.join('src', 'test-spec.yml'))

    with pytest.raises(ValueError) as excinfo:
        run_sphinx('test-spec.yml', options={'examples': True})

    assert str(excinfo.value) == (
        'Rendering examples is not supported for OpenAPI v2.x specs.')


@pytest.mark.parametrize('render_examples', [False, True])
def test_openapi3_examples(tmpdir, run_sphinx, render_examples):
    spec = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'OpenAPI-Specification',
        'examples',
        'v3.0',
        'petstore.yaml')
    py.path.local(spec).copy(tmpdir.join('src', 'test-spec.yml'))
    run_sphinx('test-spec.yml', options={'examples': render_examples})

    rendered_html = tmpdir.join('out', 'index.html').read_text('utf-8')

    assert ('<strong>Example response:</strong>' in rendered_html) \
        == render_examples
