import textwrap
import pytest

from sphinx.application import Sphinx


def _format_option_raw(key, val):
    if isinstance(val, bool) and val:
        return ':%s:' % key
    return ':%s: %s' % (key, val)


@pytest.fixture(scope='function')
def run_sphinx(tmpdir):
    src = tmpdir.ensure('src', dir=True)
    out = tmpdir.ensure('out', dir=True)

    def run(spec, options={}):
        options_raw = '\n'.join([
            '   %s' % _format_option_raw(key, val)
            for key, val in options.items()])

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
            '.. openapi:: %s\n%s' % (spec, options_raw),
            encoding='utf-8')

        Sphinx(
            srcdir=src.strpath,
            confdir=src.strpath,
            outdir=out.strpath,
            doctreedir=out.join('.doctrees').strpath,
            buildername='html'
        ).build()

    yield run
