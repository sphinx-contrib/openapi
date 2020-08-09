import textwrap

import pytest
import yaml


@pytest.fixture(scope="function")
def oas_fragment():
    def oas_fragment(fragment):
        return yaml.safe_load(textwrap.dedent(fragment))

    return oas_fragment
