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
    return renderers.HttpdomainRenderer(fakestate, {})


@pytest.fixture(scope="function")
def oas_fragment():
    def oas_fragment(fragment):
        return yaml.safe_load(textwrap.dedent(fragment))

    return oas_fragment
