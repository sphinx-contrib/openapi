"""
    sphinxcontrib.openapi
    ---------------------

    The OpenAPI spec renderer for Sphinx. It's a new way to document your
    RESTful API. Based on ``sphinxcontrib-httpdomain``.

    :copyright: (c) 2016, Ihor Kalnytskyi.
    :license: BSD, see LICENSE for details.
"""

from __future__ import unicode_literals

from pkg_resources import get_distribution, DistributionNotFound

from sphinxcontrib.openapi import directive

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = None


def setup(app):
    app.setup_extension('sphinxcontrib.httpdomain')
    app.add_directive('openapi', directive.OpenApi)

    return {'version': __version__, 'parallel_read_safe': True}
