"""Abstract Base Classes (ABCs) for OpenAPI renderers."""

import abc

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles


class Renderer(metaclass=abc.ABCMeta):
    """Base class for OpenAPI renderers."""

    def __init__(self, state, options):
        self._state = state
        self._options = options

    @property
    @abc.abstractmethod
    def option_spec(self):
        """Renderer options and their converting functions."""

    @abc.abstractmethod
    def render(self, spec):
        """Render a given OpenAPI spec."""


class RestructuredTextRenderer(Renderer):
    """Base class for reStructuredText OpenAPI renderers.

    Docutils DOM manipulation is quite a tricky task that requires passing
    dozen arguments around. Because of that a lot of Sphinx extensions instead
    of constructing DOM nodes directly produce and parse reStructuredText.
    This Sphinx extension is not an exception, and that's why this class
    exists. It's a convenient extension of :class:`Renderer` that converts
    produced markup text into docutils DOM elements.
    """

    def render(self, spec):
        viewlist = ViewList()
        for line in self.render_restructuredtext_markup(spec):
            viewlist.append(line, "<openapi>")

        node = nodes.section()
        node.document = self._state.document
        nested_parse_with_titles(self._state, viewlist, node)
        return node.children
