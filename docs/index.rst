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

``encoding``
  Encoding to be used to read an OpenAPI spec. If not passed, Sphinx's
  source encoding will be used.

``paths``
  A comma separated list of paths to filter the included OpenAPI spec by.
  For example:

  .. code:: restructuredtext

     .. openapi:: specs/openapi.yml
        :paths:
           /persons
           /evidence
        :encoding: utf-8

  Would only render the endpoints at ``/persons`` and ``/evidence``,
  ignoring all others.

``examples``
  If passed, both request and response examples will be rendered. Please
  note, if examples are not provided in a spec, they will be generated
  by internal logic based on a corresponding schema.

``group``
  If passed, paths will be grouped by tags. If a path has no tag assigned, it
  will be grouped in a ``default`` group.

``format``
  The format of text in the spec, either ``rst`` or ``markdown``. If
  not supplied, ReStructured Text is assumed.


.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _OpenAPI: https://github.com/OAI/OpenAPI-Specification
.. _sphinxcontrib-httpdomain: https://sphinxcontrib-httpdomain.readthedocs.io/
.. _sphinxcontrib-redoc: https://sphinxcontrib-redoc.readthedocs.io/
