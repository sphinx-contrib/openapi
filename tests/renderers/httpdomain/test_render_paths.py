import pytest

from sphinxcontrib.openapi import renderers


@pytest.mark.parametrize(
    ["order", "methods", "expected"],
    [
        pytest.param(
            [],
            ["get", "post", "put", "delete"],
            ["get", "post", "put", "delete"],
            id="default order",
        ),
        pytest.param(
            ["get", "post", "put", "delete"],
            ["post", "put", "get", "delete"],
            ["get", "post", "put", "delete"],
            id="full order",
        ),
        pytest.param(
            ["get", "post", "put", "delete"],
            ["post", "put", "head", "get", "delete", "trace"],
            ["get", "post", "put", "delete", "head", "trace"],
            id="extra methods",
        ),
    ],
)
def test_sorted_methods(fakestate, order, methods, expected):
    testrenderer = renderers.HttpdomainRenderer(
        fakestate, {"http-methods-order": order}
    )

    methods = {x: x for x in methods}
    expected = [(x, x) for x in expected]
    sorted_methods = list(testrenderer._sorted_methods(methods))
    assert sorted_methods == expected
