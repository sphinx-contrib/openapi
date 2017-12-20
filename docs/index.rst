=====================
sphinxcontrib-openapi
=====================

.. hint::

    Check out `sphinxcontrib-redoc`_ if you are interested in separate
    three-panel OpenAPI spec rendering.

**sphinxcontrib-openapi** is a `Sphinx`_ extension to generate APIs docs from
`OpenAPI`_ (fka Swagger) spec. It depends on `sphinxcontrib-httpdomain`_ that
provides an HTTP domain for describing RESTful HTTP APIs, so we don't need to
reinvent the wheel.

.. code:: bash

   pip install sphinxcontrib-openapi


How To Use?
===========

Consider you have the following OpenAPI spec saved at ``specs/openapi.yml``:

.. literalinclude:: specs/openapi.yml
   :language: yaml

You can render it by using the ``openapi`` directive:

.. code:: restructuredtext

   .. openapi:: specs/openapi.yml

and it will be rendered into something like:

.. openapi:: specs/openapi.yml


Options
=======

The ``openapi`` directive supports the following options:

encoding
  Encoding to be used to read an OpenAPI spec. If not passed, Sphinx's
  source encoding will be used.

paths
  A comma separated list of paths to filter the included openapi spec by.
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :paths:
           /persons
           /evidence
        :encoding: utf-8

  Would only render the endpoints at ``/persons`` and ``/evidence``,
  ignoring all others.

include
  A line separated list of regular expressions to filter the included openapi
  spec by. For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :include:
           /evid.*
        :encoding: utf-8

  Would render the endpoints at ``/evidence`` and ``/evidence/{pk}``

exclude
  A line separated list of regular expressions to filter the included openapi
  spec by (excluding matches). For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :exclude:
           /evidence/{pk}
        :encoding: utf-8

  Would render ``/persons`` and ``/evidence`` endpoints, but not
  ``/evidence/{pk}`` endpoints

`exclude`, `include` and `paths` can also be used together (`exclude` taking
precedence over `include` and `paths`)



.. _Sphinx: https://sphinx.pocoo.org
.. _OpenAPI: https://openapis.org/specification
.. _sphinxcontrib-httpdomain: https://pythonhosted.org/sphinxcontrib-httpdomain/
.. _sphinxcontrib-redoc: https://sphinxcontrib-redoc.readthedocs.io/
