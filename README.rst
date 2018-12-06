=====================
sphinxcontrib-openapi
=====================

**sphinxcontrib-openapi** is a `Sphinx`_ extension to generate APIs docs from
`OpenAPI`_ (fka Swagger) spec. It depends on `sphinxcontrib-httpdomain`_ that
provides an HTTP domain for describing RESTful HTTP APIs, so we don't need to
reinvent the wheel.

.. code:: bash

   pip install sphinxcontrib-openapi


Usage
=====

Pass ``sphinxcontrib-openapi`` to ``extensions`` list in  Sphinx's ``conf.py``

.. code:: python

   extensions = [
      ...
      'sphinxcontrib.openapi',
   ]

and feel free to use the ``openapi`` directive to render OpenAPI specs

.. code:: restructuredtext

   .. openapi:: path/to/openapi.yml


Links
=====

* Documentation: https://sphinxcontrib-openapi.readthedocs.org/
* Source: https://github.com/ikalnytskyi/sphinxcontrib-openapi
* Bugs: https://github.com/ikalnytskyi/sphinxcontrib-openapi/issues


.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _OpenAPI: https://github.com/OAI/OpenAPI-Specification
.. _sphinxcontrib-httpdomain: https://sphinxcontrib-httpdomain.readthedocs.io/
