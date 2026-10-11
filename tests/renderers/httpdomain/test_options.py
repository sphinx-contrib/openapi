"""Test the directive options the 'httpdomain' renderer accepts."""

import re

import pytest

from sphinxcontrib.openapi import renderers

# Exercises every option below at once. Two methods on one endpoint for
# 'http-methods-order', two kinds of parameter for 'request-parameters-order',
# and two media types carrying distinguishable examples, for both a request and
# a response, for the preference options. The '404' response is what
# 'response-examples-for' has to be widened to reach.
_SPEC = """\
openapi: 3.0.0
info:
  title: An example spec.
  version: 1.0.0
paths:
  /evidences:
    get:
      parameters:
        - name: q
          in: query
          schema:
            type: string
        - name: X-Evidence-Token
          in: header
          schema:
            type: string
      responses:
        '200':
          description: An evidence.
          content:
            application/json:
              example: {'id': 'json-response'}
            text/plain:
              example: plain-response
        '404':
          description: An evidence is not found.
          content:
            text/plain:
              example: no-such-evidence
    post:
      requestBody:
        content:
          application/json:
            example: {'id': 'json-request'}
          text/plain:
            example: plain-request
      responses:
        '201':
          description: An evidence created.
"""


_WHITESPACE_DELIMITED_OPTIONS = [
    pytest.param("http-methods-order", "head get", ["head", "get"]),
    pytest.param(
        "response-examples-for", "200 201 2XX 404", ["200", "201", "2XX", "404"]
    ),
    pytest.param(
        "request-parameters-order",
        "query path header cookie",
        ["query", "path", "header", "cookie"],
    ),
    pytest.param(
        "example-preference",
        "text/plain application/json",
        ["text/plain", "application/json"],
    ),
    pytest.param(
        "request-example-preference",
        "text/plain application/json",
        ["text/plain", "application/json"],
    ),
    pytest.param(
        "response-example-preference",
        "text/plain application/json",
        ["text/plain", "application/json"],
    ),
]


@pytest.fixture(scope="function")
def build_warnings(tmpdir, run_sphinx):
    """Build '_SPEC' with the given options, and return reported warnings."""

    def build_warnings(options):
        tmpdir.join("src", "test-spec.yml").write_text(_SPEC, encoding="utf-8")
        return run_sphinx("test-spec.yml", options=options, renderer="httpdomain")

    return build_warnings


@pytest.fixture(scope="function")
def build(tmpdir, build_warnings):
    """Build '_SPEC' with the given options, and return the rendered text.

    Tags are stripped since httpdomain splits a method and its path into
    separate elements, so the rendered markup can't be searched as is.
    """

    def build(options):
        assert "unknown option" not in build_warnings(options)
        html = tmpdir.join("out", "index.html").read_text(encoding="utf-8")
        return re.sub(r"<[^>]+>", "", html)

    return build


@pytest.mark.parametrize(["option", "value", "expected"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_is_accepted(build, option, value, expected):
    """A whitespace delimited option is not rejected as an unknown one."""

    build({option: value})


@pytest.mark.parametrize(["option", "value", "expected"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_is_parsed(option, value, expected):
    """A whitespace delimited option is parsed into a list of tokens."""

    convertor = renderers.HttpdomainRenderer.option_spec[option]
    assert convertor(value) == expected


@pytest.mark.parametrize(["option", "value", "expected"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_without_value_is_rejected(option, value, expected):
    """A whitespace delimited option passed with no value is an error."""

    convertor = renderers.HttpdomainRenderer.option_spec[option]

    with pytest.raises(ValueError):
        convertor(None)


@pytest.mark.parametrize(
    ["option", "value"],
    [
        pytest.param("response-examples-for", ""),
        pytest.param("response-examples-for", "   "),
    ],
)
def test_option_with_blank_value_is_reported(build_warnings, option, value):
    """A blank option value is reported instead of silently taking effect."""

    # Left to itself, an empty 'response-examples-for' would override the
    # default and quietly disable every response example.
    assert "invalid option value" in build_warnings({option: value})


def test_http_methods_order_is_effective(build):
    """The 'http-methods-order' option reaches the renderer."""

    text = build({"http-methods-order": "post get"})

    # Natural order puts 'get' first, since that's how the spec declares them.
    assert text.index("POST /evidences") < text.index("GET /evidences")


def test_request_parameters_order_is_effective(build):
    """The 'request-parameters-order' option reaches the renderer."""

    text = build({"request-parameters-order": "query header"})

    # The renderer's own default order puts header parameters first.
    assert text.index("Query Parameters") < text.index("Request Headers")


def test_response_examples_for_is_effective(build):
    """The 'response-examples-for' option reaches the renderer."""

    # By default examples are rendered for successful status codes only, so the
    # '404' example is rendered if and only if the option took effect.
    assert "no-such-evidence" not in build({"http-methods-order": "get"})
    assert "no-such-evidence" in build({"response-examples-for": "404"})


@pytest.mark.parametrize(
    ["option", "expected"],
    [
        pytest.param("example-preference", "plain-response"),
        pytest.param("response-example-preference", "plain-response"),
    ],
)
def test_response_example_preference_is_effective(build, option, expected):
    """The response example preference options reach the renderer."""

    # 'application/json' is declared first, so it wins without a preference.
    assert expected not in build({"http-methods-order": "get"})
    assert expected in build({option: "text/plain application/json"})


@pytest.mark.parametrize(
    ["option", "expected"],
    [
        pytest.param("example-preference", "plain-request"),
        pytest.param("request-example-preference", "plain-request"),
    ],
)
def test_request_example_preference_is_effective(build, option, expected):
    """The request example preference options reach the renderer."""

    assert expected not in build({"http-methods-order": "post"})
    assert expected in build({option: "text/plain application/json"})


def test_request_example_preference_takes_precedence(build):
    """A request specific preference wins over the shared one."""

    text = build(
        {
            "example-preference": "application/json text/plain",
            "request-example-preference": "text/plain application/json",
        }
    )

    assert "plain-request" in text
    assert "json-response" in text
