"""Build and verify examples from OAI/learn.openapis.org."""

import collections
import glob
import os
import pathlib

from docutils import nodes
import py
import pytest
from sphinx import addnodes
import yaml

from sphinxcontrib.openapi import utils


_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def _operation_signatures(endpoint, path):
    for method, operation in path.items():
        if method not in _METHODS:
            continue
        yield f"{method.upper()} {endpoint}"
        for callback in operation.get("callbacks", {}).values():
            for expression, callback_path in callback.items():
                if expression.startswith("x-"):
                    continue
                yield from _operation_signatures(expression, callback_path)


def assert_rendered_operations(app, specfile, render_examples=None):
    """A successful build must not silently omit specified operations."""
    assert app.statuscode == 0
    with open(specfile, encoding="utf-8") as stream:
        spec = yaml.safe_load(stream)
    spec = utils._resolve_refs(pathlib.Path(specfile).as_uri(), spec)
    expected = []
    for endpoint, path in spec.get("paths", {}).items():
        if not endpoint.startswith("x-"):
            expected.extend(_operation_signatures(endpoint, path))
    for path in spec.get("webhooks", {}).values():
        expected.extend(_operation_signatures("{webhook_url}", path))
    doctree = app.env.get_doctree("index")
    actual = [
        node[0].astext() for node in doctree.findall(addnodes.desc)
        if node.get("domain") == "http"
    ]
    assert collections.Counter(actual) == collections.Counter(expected)
    if render_examples is False:
        assert not any(
            node.get("language") == "http"
            for node in doctree.findall(nodes.literal_block)
        )
    return doctree


@pytest.mark.parametrize("spec", [
    *glob.glob(os.path.join(os.path.dirname(__file__), "examples", "v2.0", "json", "*.json")),
    *glob.glob(os.path.join(os.path.dirname(__file__), "examples", "v2.0", "yaml", "*.yaml")),
])
def test_openapi2_success(tmpdir, run_sphinx, spec):
    py.path.local(spec).copy(tmpdir.join("src", "test-spec.yml"))
    app = run_sphinx("test-spec.yml", renderer="httpdomain", return_app=True)
    assert_rendered_operations(app, os.path.abspath(spec))


@pytest.mark.parametrize("group_paths", [False, True])
@pytest.mark.parametrize("render_examples", [False, True])
@pytest.mark.parametrize("render_request", [False, True])
@pytest.mark.parametrize("spec", glob.glob(
    os.path.join(os.path.dirname(__file__), "examples", "v3.0", "*.yaml")
))
def test_openapi30_success(tmpdir, run_sphinx, spec, render_examples, render_request, group_paths):
    py.path.local(spec).copy(tmpdir.join("src", "test-spec.yml"))
    app = run_sphinx("test-spec.yml", options={
        "examples": render_examples, "request": render_request, "group": group_paths,
    }, renderer="httpdomain", return_app=True,
        warningiserror=os.path.basename(spec) == "callback-example.yaml")
    doctree = assert_rendered_operations(app, os.path.abspath(spec), render_examples)
    if os.path.basename(spec) == "callback-example.yaml":
        text = doctree.astext()
        assert "Callback: onData" in text
        assert "Your server implementation should return this HTTP status code" in text
        assert ("timestamp" in text) == (render_request or render_examples)
        assert ("userData" in text) == (render_request or render_examples)


@pytest.mark.parametrize("render_examples", [False, True])
@pytest.mark.parametrize("render_request", [False, True])
@pytest.mark.parametrize("spec", glob.glob(
    os.path.join(os.path.dirname(__file__), "examples", "v3.1", "*.yaml")
))
def test_openapi31_success(tmpdir, run_sphinx, spec, render_examples, render_request):
    py.path.local(spec).copy(tmpdir.join("src", "test-spec.yml"))
    app = run_sphinx("test-spec.yml", options={
        "examples": render_examples, "request": render_request,
    }, renderer="httpdomain", return_app=True,
        warningiserror=os.path.basename(spec) == "webhook-example.yaml")
    doctree = assert_rendered_operations(app, os.path.abspath(spec), render_examples)
    if os.path.basename(spec) == "webhook-example.yaml":
        text = doctree.astext()
        assert "Webhook: newPet" in text
        assert "Return a 200 status to indicate that the data was received successfully" in text
        assert ("Request JSON Object" in text) == render_request
        assert any(
            node.get("language") == "http"
            for node in doctree.findall(nodes.literal_block)
        ) == render_examples


@pytest.mark.parametrize("group", [False, True])
def test_outbound_operations_do_not_register_routes(tmpdir, run_sphinx, group):
    """Repeated callback URLs and webhook destinations must not clash with routes."""
    path = {
        "post": {
            "requestBody": {"content": {"application/json": {
                "schema": {"type": "object", "properties": {"active": {"type": "boolean"}}},
            }}},
            "responses": {"200": {"description": "Accepted"}},
        },
    }
    callback = {"callbacks": {"onEvent": {"/shared": path}},
                "responses": {"200": {"description": "Subscribed"}}}
    spec = {
        "openapi": "3.1.0", "info": {"title": "Events", "version": "1"},
        "paths": {"/first": {"get": callback}, "/second": {"get": callback}, "/shared": path},
        "webhooks": {"firstEvent": path, "secondEvent": path},
    }
    specfile = tmpdir.join("src", "events.yaml")
    specfile.write_text(yaml.safe_dump(spec), encoding="utf-8")
    app = run_sphinx(
        "events.yaml", options={"group": group},
        renderer="httpdomain", return_app=True, warningiserror=True,
    )
    doctree = assert_rendered_operations(app, str(specfile))
    http = app.env.get_domain("http")
    assert set(http.data["get"]) == {"/first", "/second"}
    assert set(http.data["post"]) == {"/shared"}
    outbound = [node for node in doctree.findall(addnodes.desc)
                if node.get("objtype", "").startswith("openapi-")]
    assert len(outbound) == 4
    for node in outbound:
        assert not node[0].get("ids")
        assert "Request JSON Object" in node.astext()
        assert "active" in node.astext()
    html = tmpdir.join("out", "index.html").read_text("utf-8")
    assert "Callback: onEvent" in html
    assert "Webhook: firstEvent" in html
    assert "Webhook: secondEvent" in html
