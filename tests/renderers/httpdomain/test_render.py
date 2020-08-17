import pathlib
import os

import pytest


@pytest.fixture(scope="function")
def rendered():
    return pathlib.Path(os.path.dirname(__file__), "rendered")


@pytest.mark.regenerate_rendered_specs
def test_generate(testrenderer, testspec, rendered):
    testspec_name, testspec = testspec
    rendered_markup = "\n".join(testrenderer.render_restructuredtext_markup(testspec))

    rendered.joinpath(os.path.dirname(testspec_name)).mkdir(parents=True, exist_ok=True)
    rendered.joinpath(testspec_name + ".rst").write_text(rendered_markup)


def test_render(testrenderer, testspec, rendered):
    testspec_name, testspec = testspec
    rendered_markup = "\n".join(testrenderer.render_restructuredtext_markup(testspec))

    assert rendered_markup == rendered.joinpath(testspec_name + ".rst").read_text()
