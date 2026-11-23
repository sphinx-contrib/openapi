"""Render OpenAPI CommonMark fragments inside generated HTTP directives."""

import json

from docutils import nodes
from myst_parser.config.main import MdParserConfig
from myst_parser.mdit_to_docutils.base import DocutilsRenderer
from myst_parser.parsers.mdit import create_md_parser
from sphinx.util.docutils import SphinxDirective


DIRECTIVE_NAME = "openapi-commonmark"


def as_directive(text):
    """Pass Markdown through reStructuredText without parsing or dedenting it."""
    if not text.strip():
        return ""
    return f".. {DIRECTIVE_NAME}:: {json.dumps(text)}\n\n"


class CommonMarkDirective(SphinxDirective):
    """Insert parsed Markdown nodes into the surrounding Sphinx document."""

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        try:
            text = json.loads(self.arguments[0])
        except ValueError as exc:
            raise self.error("Expected a JSON-encoded CommonMark string.") from exc
        if not isinstance(text, str):
            raise self.error("Expected a JSON-encoded CommonMark string.")

        fragment = nodes.container()
        self.set_source_info(fragment)
        parser = create_md_parser(
            MdParserConfig(commonmark_only=True), DocutilsRenderer
        )
        parser.options.update(document=self.state.document, current_node=fragment)
        parser.renderer.setup_render(parser.options, {})
        parser.renderer.nested_render_text(text, self.lineno - 1)
        return fragment.children
