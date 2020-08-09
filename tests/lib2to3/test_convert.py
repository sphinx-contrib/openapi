""".convert() test suite."""

import sphinxcontrib.openapi._lib2to3 as lib2to3


def test_minimal(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_complete(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            tags:
              - tag_a
            externalDocs: https://docs.example.com/
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        tags:
          - tag_a
        externalDocs: https://docs.example.com/
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_servers_complete(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            host: example.com
            basePath: /v1
            schemes:
              - https
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        servers:
          - url: https://example.com/v1
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_servers_host_only(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            host: example.com
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        servers:
          - url: example.com
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_servers_basepath_only(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            basePath: /v1
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        servers:
          - url: /v1
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_servers_schemes_multiple(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            host: example.com
            schemes:
              - http
              - https
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        servers:
          - url: http://example.com
          - url: https://example.com
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_servers_schemes_from_operation(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            host: example.com
            schemes:
              - http
            paths:
              /test:
                get:
                  schemes:
                    - ws
                  responses:
                    '200':
                      description: a response description
            """
        ),
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        servers:
          - url: http://example.com
          - url: ws://example.com
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        """
    )


def test_consumes(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            consumes:
              - application/json
            paths:
              /test:
                post:
                  parameters:
                    - in: query
                      name: marker
                      type: string
                    - in: body
                      name: payload
                      schema:
                        type: string
                  responses:
                    '201':
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            post:
              parameters:
                - in: query
                  name: marker
                  schema:
                    type: string
              requestBody:
                content:
                  application/json:
                    schema:
                      type: string
              responses:
                '201':
                  description: a response description
        """
    )


def test_consumes_operation_override(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            consumes:
              - application/xml
            paths:
              /test:
                post:
                  consumes:
                    - application/json
                  parameters:
                    - in: query
                      name: marker
                      type: string
                    - in: body
                      name: payload
                      schema:
                        type: string
                  responses:
                    '201':
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            post:
              parameters:
                - in: query
                  name: marker
                  schema:
                    type: string
              requestBody:
                content:
                  application/json:
                    schema:
                      type: string
              responses:
                '201':
                  description: a response description
        """
    )


def test_produces(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            produces:
              - application/json
            paths:
              /test:
                get:
                  responses:
                    '200':
                      schema:
                        items:
                          format: int32
                          type: integer
                        type: array
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            get:
              responses:
                '200':
                  content:
                    application/json:
                      schema:
                        items:
                          format: int32
                          type: integer
                        type: array
                  description: a response description
        """
    )


def test_produces_operation_override(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            produces:
              - application/xml
            paths:
              /test:
                get:
                  produces:
                    - application/json
                  responses:
                    '200':
                      schema:
                        items:
                          format: int32
                          type: integer
                        type: array
                      description: a response description
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            get:
              responses:
                '200':
                  content:
                    application/json:
                      schema:
                        items:
                          format: int32
                          type: integer
                        type: array
                  description: a response description
        """
    )


def test_vendor_extensions(oas_fragment):
    converted = lib2to3.convert(
        oas_fragment(
            """
            swagger: "2.0"
            info:
              title: An example spec
              version: 1.0
            paths:
              /test:
                get:
                  responses:
                    '200':
                      description: a response description
            x-vendor-ext: vendor-ext
            """
        )
    )
    assert converted == oas_fragment(
        """
        openapi: 3.0.3
        info:
          title: An example spec
          version: 1.0
        paths:
          /test:
            get:
              responses:
                '200':
                  description: a response description
        x-vendor-ext: vendor-ext
        """
    )
