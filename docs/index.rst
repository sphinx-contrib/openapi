=====================
sphinxcontrib-openapi
=====================

.. hint::

    Check out `sphinxcontrib-redoc`_ if you are interested in separate three-panel OpenAPI spec rendering.

**sphinxcontrib-openapi** is a `Sphinx`_ extension to generate APIs docs from `OpenAPI`_ (fka Swagger) spec.
It depends on `sphinxcontrib-httpdomain`_, which provides an HTTP domain for describing RESTful HTTP APIs so we don't need to reinvent the wheel.

.. code:: bash

   pip install sphinxcontrib-openapi


Usage
=====

Consider you have the following OpenAPI spec saved at ``specs/openapi.yml``:

.. literalinclude:: specs/openapi.yml
   :language: yaml

You can render it by using the ``openapi`` directive:

.. code:: restructuredtext

   .. openapi:: specs/openapi.yml

and it will be rendered into something like:

.. openapi:: specs/openapi.yml

The ``openapi`` directive uses the default renderer (configured by ``openapi_default_renderer``).
In addition, each registered renderer can be invoked directly by suffixing the directive name with the renderer alias:

.. code:: restructuredtext

   .. openapi:httpdomain:: specs/openapi.yml

or:

.. code:: restructuredtext

   .. openapi:httpdomain:old:: specs/openapi.yml


Configuration
=============

The extension provides two configuration options.

``openapi_renderers``
  A mapping of renderer aliases to the classes.
  Two renderer classes are provided but it is possible to define your own renderer class.
  This allows you to add support for things like additional type formats or custom extensions (``x``-prefixed attributes).

  :Type: A mapping of renderer aliases to the implementation class.
  :Default: ``{'httpdomain': sphinxcontrib.openapi.renderers.HttpdomainRenderer, 'httpdomain:old': sphinxcontrib.openapi.renderers.HttpdomainOldRenderer}``

``openapi_default_renderer``
  The renderer to use for the generic ``openapi`` directive.
  This must be one of the renderers defined in ``openapi_renderers``.

  :Type: A string corresponding to the alias of a registered renderer.
  :Default: ``'httpdomain:old'``


Options
=======

The ``openapi`` directive supports different options depending on the renderer in use.

Options for the ``httpdomain`` renderer
---------------------------------------

The following options take a value.

``encoding``
  Encoding to be used to read an OpenAPI spec. If not passed, Sphinx's source encoding will be used.

``markup``
  The format to use when parsing markup.

  :Type: One of ``commonmark``, ``restructuredtext``
  :Default: ``commonmark``

``http-methods-order``
  The preferred order in which to output HTTP methods.

  :Type: A whitespace-delimited sequence of HTTP methods.
  :Default: ``None`` (methods are rendered in declaration order)

  For example:

  .. code:: restructuredtext

     .. openapi:httpdomain:: specs/openapi.yml
        :http-methods-order: head get

  Would render the ``head`` method, followed by the ``get`` method, followed by the rest of the methods in their declared order.

``response-examples-for``
  The response codes to render samples for.

  An explicit value takes precedence over the ``examples`` flag.

  :Type: A whitespace-delimited sequence of strings, with each string corresponding to an `HTTP status code <https://spec.openapis.org/oas/v3.1.0#http-status-codes>`__ that response examples should be rendered for.
  :Default: ``["200", "201", "202", "2XX"]``

``request-parameters-order``
  The preferred order in which to output parameters.

  :Type: A whitespace-delimited sequence of strings, with each string corresponding to a `supported parameter type <https://spec.openapis.org/oas/v3.1.0#fixed-fields-9>`__.
  :Default: ``["header", "path", "query", "cookie"]``

``example-preference``
  The preferred example format to render for requests and responses.

  :Type: A whitespace-delimited sequence of strings, with each string corresponding to a `supported media type <https://spec.openapis.org/oas/v3.1.0#media-types>`__.
  :Default: ``None``

``request-example-preference``
  The preferred example format to render for requests. This takes precedence over ``example-preference``.

  :Type: A whitespace-delimited sequence of strings, with each string corresponding to a `supported media type <https://spec.openapis.org/oas/v3.1.0#media-types>`__.
  :Default: Defaults to the value of ``example-preference``, or ``None``

``response-example-preference``
  The preferred example format to render for responses. This takes precedence over ``example-preference``.

  :Type: A whitespace-delimited sequence of strings, with each string corresponding to a `supported media type <https://spec.openapis.org/oas/v3.1.0#media-types>`__.
  :Default: Defaults to the value of ``example-preference``, or ``None``

The following options are boolean flags. They can be passed without a value to enable them, or with an explicit ``true`` or ``false`` value.

``examples``

  Controls rendering of request and response examples. If enabled, examples are generated from schemas when not supplied in the spec, and examples are rendered for all response codes unless ``response-examples-for`` is set.
  If disabled, neither supplied nor generated examples are rendered.

  :Type: Flag.
  :Default: Supplied examples are rendered, but examples are not generated from schemas.

``request``

  Controls rendering of request JSON schema hints, independently of examples and response schema hints.
  Unlike the old renderer, request structure is described using HTTP domain fields rather than a raw JSON schema dump.
  ``no-json-schema-description`` takes precedence over this option.

  :Type: Flag.
  :Default: Enabled.

``generate-examples-from-schemas``

  Whether examples should be generated from the schema if they are not provided in the spec. If unset, examples will only be generated when ``examples`` is enabled.
  An explicit value overrides the generation setting implied by ``examples``, but ``examples: false`` always suppresses rendering.

  Generation is best effort, not a full JSON Schema constraint solver.
  For OpenAPI 3.1 type arrays, a non-null type is preferred when possible.
  Boolean ``true`` schemas allow any value; ``false`` schemas cannot have an example.
  If a schema cannot contribute an example, generation is skipped for that media type.
  Arrays may omit ``items``, and ``prefixItems`` constrains initial positions independently of ``items``.

  :Type: Flag.

``no-json-schema-description``

  Whether to disable rendering of both request and response JSON schema hints. An explicit ``false`` value leaves schema hints enabled.

  :Type: Flag.

Options for the ``httpdomain:old`` renderer
-------------------------------------------

The following options are supported when using the ``httpdomain:old`` renderer:

``encoding``
  Encoding to be used to read an OpenAPI spec. If not passed, Sphinx's source encoding will be used.

``paths``
  A whitespace-delimited list of paths to filter the included OpenAPI spec by.
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :paths:
           /persons
           /evidence
        :encoding: utf-8

  Would only render the endpoints at ``/persons`` and ``/evidence``, ignoring all others.

``request``
  If passed, the request body structure and schema will be rendered (OpenAPI 3.x only).

``examples``
  If passed, both request and response examples will be rendered.
  Please note, if examples are not provided in a spec, they will be generated by internal logic based on a corresponding schema.

``group``
  If passed, paths will be grouped by tags.
  If a path has no tag assigned, it will be grouped in a ``default`` group.

``format``
  The format of text in the spec, either ``rst`` or ``markdown``.
  If not supplied, reStructuredText is assumed.

``include``
  A line separated list of regular expressions to filter the included OpenAPI spec by.
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :include:
           /evid.*
        :encoding: utf-8

  Would render the endpoints at ``/evidence`` and ``/evidence/{pk}``

``exclude``
  A line separated list of regular expressions to filter the included OpenAPI spec by (excluding matches).
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :exclude:
           /evidence/{pk}
        :encoding: utf-8

  Would render ``/persons`` and ``/evidence`` endpoints, but not ``/evidence/{pk}`` endpoints

``methods``
  A line separated list of HTTP methods to filter included OpenAPI spec.
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :methods:
            get
            post
            put
        :encoding: utf-8

  Would render paths with get, post or put method.

``exclude``, ``include`` and ``paths`` can also be used together.
When used together, ``exclude`` takes precedence over ``include`` and ``paths``.

.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _OpenAPI: https://github.com/OAI/OpenAPI-Specification
.. _sphinxcontrib-httpdomain: https://sphinxcontrib-httpdomain.readthedocs.io/
.. _sphinxcontrib-redoc: https://sphinxcontrib-redoc.readthedocs.io/
