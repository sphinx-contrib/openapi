"""Some shared goodies."""

import textwrap

import pytest
import yaml

from sphinxcontrib.openapi import renderers


@pytest.fixture(scope="function")
def fakestate():
    return None


@pytest.fixture(scope="function")
def testrenderer(fakestate):
    # These fixtures assert the reStructuredText layout of the HTTP directives.
    return renderers.HttpdomainRenderer(fakestate, {"markup": "restructuredtext"})


@pytest.fixture(scope="function")
def oas_fragment():
    def oas_fragment(fragment):
        return yaml.safe_load(textwrap.dedent(fragment))

    return oas_fragment
