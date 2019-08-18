"""Some shared goodies."""

import pytest

from sphinxcontrib.openapi import renderers


@pytest.fixture(scope="function")
def fakestate():
    return None


@pytest.fixture(scope="function")
def testrenderer(fakestate):
    return renderers.HttpdomainRenderer(fakestate, {})
