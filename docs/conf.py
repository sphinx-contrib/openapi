import os

# Unfortunately, Sphinx doesn't support code highlighting for standard
# reStructuredText `code` directive. So let's register 'code' directive
# as alias for Sphinx's own implementation.
#
# https://github.com/sphinx-doc/sphinx/issues/2155
from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock

directives.register_directive("code", CodeBlock)

project = "sphinxcontrib-openapi"
copyright = "2016, Ihor Kalnytskyi"

extensions = ["sphinxcontrib.openapi"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]
pygments_style = "default"

if not os.environ.get("READTHEDOCS") == "True":
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
