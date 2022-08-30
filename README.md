# sphinxcontrib-openapi


**sphinxcontrib-openapi** is a [Sphinx](<https://www.sphinx-doc.org/en/master/>) extension to generate APIs docs from
[OpenAPI](https://github.com/OAI/OpenAPI-Specification) (fka Swagger) spec. It depends on
[sphinxcontrib-httpdomain](https://sphinxcontrib-httpdomain.readthedocs.io/) that
provides an HTTP domain for describing RESTful HTTP APIs, so we don't need to
reinvent the wheel.

``` bash
   $ python3 -m pip install sphinxcontrib-openapi
```

## Usage

Pass ``sphinxcontrib-openapi`` to ``extensions`` list in  Sphinx's ``conf.py``

``` python
   extensions = [
      ...
      'sphinxcontrib.openapi',
   ]
```

and feel free to use the ``openapi`` directive to render OpenAPI specs

``` restructuredtext
   .. openapi:: path/to/openapi.yml
```

## Links

* Documentation: https://sphinxcontrib-openapi.readthedocs.org/
* Source: https://github.com/sphinx-contrib/openapi
* Bugs: https://github.com/sphinx-contrib/openapi/issues
