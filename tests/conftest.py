from __future__ import unicode_literals

import textwrap

import pytest

from sphinx.application import Sphinx


@pytest.fixture(scope='function')
def run_sphinx(tmpdir):
    src = tmpdir.ensure('src', dir=True)
    out = tmpdir.ensure('out', dir=True)

    def run(spec, options=None):
        src.join('conf.py').write_text(
            textwrap.dedent('''
                import os

                project = 'sphinxcontrib-openapi-test'
                copyright = '2017, Ihor Kalnytskyi'

                extensions = ['sphinxcontrib.openapi']
                source_suffix = '.rst'
                master_doc = 'index'
            '''),
            encoding='utf-8')

        src.join('index.rst').write_text(
            '.. openapi:: %s' % spec,
            encoding='utf-8')

        Sphinx(
            srcdir=src.strpath,
            confdir=src.strpath,
            outdir=out.strpath,
            doctreedir=out.join('.doctrees').strpath,
            buildername='html'
        ).build()

    yield run
