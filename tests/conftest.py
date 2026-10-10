import io
import os
import pathlib
import sys
import textwrap

import pytest
import yaml

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.openapi import utils


_testspecs_dir = pathlib.Path(os.path.dirname(__file__), "testspecs")
_testspecs = [str(path.relative_to(_testspecs_dir)) for path in _testspecs_dir.glob("*/*")]


def pytest_addoption(parser):
    parser.addoption("--regenerate-rendered-specs", action="store_true")


def pytest_collection_modifyitems(items):
    items_new = []

    for item in items:
        has_mark = bool(list(item.iter_markers(name="regenerate_rendered_specs")))

        if any(
            [
                item.config.getoption("--regenerate-rendered-specs") and has_mark,
                not item.config.getoption("--regenerate-rendered-specs") and not has_mark,
            ]
        ):
            items_new.append(item)

    items[:] = items_new


class _Tee(io.StringIO):
    """Accumulate everything written, and pass it through to a stream."""

    def __init__(self, stream):
        super().__init__()
        self._stream = stream

    def write(self, text):
        self._stream.write(text)
        return super().write(text)


def _format_option_raw(key, val):
    if isinstance(val, bool) and val:
        return ':%s:' % key
    return ':%s: %s' % (key, val)


@pytest.fixture(scope='function')
def run_sphinx(tmpdir):
    src = tmpdir.ensure('src', dir=True)
    out = tmpdir.ensure('out', dir=True)

    def run(spec, options={}, renderer=None, *, warningiserror=False, return_app=False):
        options_raw = '\n'.join([
            '   %s' % _format_option_raw(key, val)
            for key, val in options.items()])

        conf_raw = ''
        if renderer:
            conf_raw = "openapi_default_renderer = '%s'" % renderer

        src.join('conf.py').write_text(
            textwrap.dedent('''
                import os

                project = 'sphinxcontrib-openapi-test'
                copyright = '2017, Ihor Kalnytskyi'

                extensions = ['sphinxcontrib.openapi']
                source_suffix = '.rst'
                master_doc = 'index'
            ''') + conf_raw,
            encoding='utf-8')

        src.join('index.rst').write_text(
            '.. openapi:: %s\n%s' % (spec, options_raw),
            encoding='utf-8')

        # Preserve the warning-text result used by the option tests. Tests
        # inspecting the doctree or domain registry can explicitly request app.
        warning = _Tee(sys.stderr)
        # Isolate docutils registrations between Sphinx builds so strict
        # warning checks do not fail on prior tests' nodes and directives.
        with docutils_namespace():
            app = Sphinx(
                srcdir=src.strpath,
                confdir=src.strpath,
                outdir=out.strpath,
                doctreedir=out.join('.doctrees').strpath,
                buildername='html',
                warning=warning,
                warningiserror=warningiserror,
            )
            app.build()
            return app if return_app else warning.getvalue()

    yield run


@pytest.fixture(scope="function")
def get_testspec():
    def get_testspec(*args, encoding="utf-8", resolve_refs=True):
        with _testspecs_dir.joinpath(*args).open(encoding=encoding) as f:
            spec = yaml.safe_load(f)
            if resolve_refs:
                spec = utils._resolve_refs("", spec)
            return spec
    return get_testspec


@pytest.fixture(scope="function", params=_testspecs)
def testspec(request, get_testspec):
    return request.param, get_testspec(request.param)
