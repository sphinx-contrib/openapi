"""Exercise CommonMark descriptions through the public Sphinx directive."""

import re
import textwrap

import pytest


@pytest.mark.parametrize(
    ("renderer", "options"),
    [
        ("httpdomain", {}),
        ("httpdomain", {"markup": "commonmark"}),
        ("httpdomain:old", {"format": "markdown"}),
    ],
)
def test_commonmark_descriptions_build_html(tmpdir, run_sphinx, renderer, options):
    spec = tmpdir.join("src", "literal.yml")
    spec.write_text(
        textwrap.dedent(
            """
            openapi: 3.1.0
            info:
              title: Example
              version: "1"
            paths:
              /files:
                get:
                  description: |
                    Match [a-zA-Z_][a-zA-Z0-9_.]* in docs/screenshots/*.png.

                    Keep *emphasis*, [a link](https://example.com), and `a_b`.

                        an indented code block

                    An extension role stays literal: {ref}`missing-target`.
                  parameters:
                    - in: query
                      name: filter
                      schema:
                        type: string
                      description: Use *.txt here.
                  responses:
                    "200":
                      description: Read **the result**.
                      headers:
                        X-File-Pattern:
                          description: The default is docs/**/*.txt.
                          schema:
                            type: string
            """
        ),
        encoding="utf-8",
    )
    warnings = run_sphinx("literal.yml", options=options, renderer=renderer)
    assert "Inline emphasis start-string" not in warnings
    assert "Unknown target name" not in warnings
    assert "Field list ends without a blank line" not in warnings
    assert "missing-target" not in warnings
    html = tmpdir.join("out", "index.html").read_text(encoding="utf-8")
    assert 'id="get--files"' in html
    assert "[a-zA-Z_][a-zA-Z0-9_.]*" in html
    assert "docs/screenshots/*.png" in html
    assert "<em>emphasis</em>" in html
    assert 'href="https://example.com">a link</a>' in html
    assert "a_b" in html
    assert re.search(r"<pre>(?:<span></span>)?an indented code block", html)
    assert "{ref}" in html
    assert "Use *.txt here." in html
    assert "<strong>the result</strong>" in html
    assert "The default is docs/**/*.txt." in html
