"""Tests for OpenAPI reference resolution."""

from io import BytesIO
import json
from unittest import mock

import pytest
from referencing.exceptions import Unresolvable
import yaml

from sphinxcontrib.openapi import utils


@pytest.mark.parametrize("extension", ["json", "yaml", "yml"])
def test_nested_external_refs(tmp_path, extension):
    """Nested refs use their document's scope, including on repeated lookups."""
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    external = {
        "item": {
            "type": "object",
            "properties": {
                "local": {"$ref": "#/value"},
                "external": {"$ref": f"../value.{extension}"},
            },
        },
        "value": {"type": "string"},
    }
    (schemas / f"item.{extension}").write_text(
        json.dumps(external) if extension == "json" else yaml.safe_dump(external),
        encoding="utf-8",
    )
    (tmp_path / f"value.{extension}").write_text(
        '{"type": "integer"}',
        encoding="utf-8",
    )
    spec = {
        "first": {"$ref": f"schemas/item.{extension}#/item"},
        "second": {"$ref": f"schemas/item.{extension}#/item"},
        "value": {"type": "boolean"},
        "last": {"$ref": "#/value"},
    }
    expected = {
        "type": "object",
        "properties": {
            "local": {"type": "string"},
            "external": {"type": "integer"},
        },
    }

    result = utils._resolve_refs((tmp_path / "openapi.yaml").as_uri(), spec)

    assert result is spec
    assert result == {
        "first": expected,
        "second": expected,
        "value": {"type": "boolean"},
        "last": {"type": "boolean"},
    }


@pytest.mark.parametrize("extension", ["json", "yaml", "yml"])
@pytest.mark.parametrize("use_requests", [False, True])
def test_remote_refs_are_cached(extension, use_requests, monkeypatch):
    """Both HTTP backends retrieve each document only once per resolution."""
    document = {"first": {"type": "string"}, "second": {"type": "integer"}}
    text = json.dumps(document) if extension == "json" else yaml.safe_dump(document)
    requests = mock.Mock()
    requests.get.return_value.json.return_value = document
    requests.get.return_value.content = text.encode("utf-8")
    urlopen = mock.Mock(side_effect=lambda uri: BytesIO(text.encode("utf-8")))
    monkeypatch.setattr(utils, "requests", requests if use_requests else None)
    monkeypatch.setattr(utils, "urlopen", urlopen)
    uri = f"https://example.com/schemas/types.{extension}"

    def resolve():
        return utils._resolve_refs(
            "https://example.com/openapi.yaml",
            {
                "first": {"$ref": f"schemas/types.{extension}#/first"},
                "second": {"$ref": f"schemas/types.{extension}#/second"},
                "third": {"$ref": f"schemas/types.{extension}#/first"},
            },
        )

    assert resolve() == {
        "first": {"type": "string"},
        "second": {"type": "integer"},
        "third": {"type": "string"},
    }
    retrieve = requests.get if use_requests else urlopen
    retrieve.assert_called_once_with(uri)
    # Cache lifetime must not extend to another spec/build.
    resolve()
    assert retrieve.call_count == 2


def test_recursive_refs():
    spec = {
        "node": {
            "type": "object",
            "properties": {"child": {"$ref": "#/node"}},
        },
        "item": {"$ref": "#/node"},
    }

    result = utils._resolve_refs("", spec)

    child = result["item"]["properties"]["child"]
    assert child == {"type": "object"}
    assert child is not result["item"]


def test_recursive_external_refs(tmp_path):
    (tmp_path / "first.yaml").write_text(
        "child:\n  $ref: second.yaml\n",
        encoding="utf-8",
    )
    (tmp_path / "second.yaml").write_text(
        "child:\n  $ref: first.yaml\n",
        encoding="utf-8",
    )

    result = utils._resolve_refs(
        (tmp_path / "openapi.yaml").as_uri(),
        {
            "item": {"$ref": "first.yaml"},
        },
    )

    assert result == {"item": {"child": {"child": {"type": "object"}}}}


def test_same_fragment_in_different_documents(tmp_path):
    """Equal fragment strings in different documents do not imply a cycle."""
    (tmp_path / "other.yaml").write_text(
        'item:\n  $ref: "#/value"\nvalue:\n  type: string\n',
        encoding="utf-8",
    )
    spec = {
        "item": {"$ref": "#/value"},
        "value": {"$ref": "other.yaml#/item"},
    }

    result = utils._resolve_refs((tmp_path / "openapi.yaml").as_uri(), spec)

    assert result == {"item": {"type": "string"}, "value": {"type": "string"}}


def test_escaped_json_pointer():
    spec = {
        "definitions": {"a/b~c": {"type": "string"}},
        "item": {"$ref": "#/definitions/a~1b~0c"},
    }

    assert utils._resolve_refs("", spec)["item"] == {"type": "string"}


def test_missing_reference():
    with pytest.raises(Unresolvable):
        utils._resolve_refs("", {"item": {"$ref": "#/missing"}})
