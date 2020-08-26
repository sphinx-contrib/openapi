import argparse
import logging

from sphinxcontrib.openapi import directive, renderers


def main():
    parser = argparse.ArgumentParser(
        prog='oas2rst',
        description='Export OpenAPI Specification files to reStructuredText \
            files')
    parser.add_argument(
        "-l", "--level",
        action='store',
        default=logging.INFO,
        dest='level',
        help="Logging level")
    parser.add_argument(
        "-e", "--encoding",
        action='store',
        default="UTF-8",
        dest='encoding',
        help="Source file encoding")
    parser.add_argument(
        "-p", "--paths",
        action='append',
        dest='paths',
        help="Endpoints to be rendered")
    parser.add_argument(
        "-x", "--examples",
        action='store_true',
        dest='examples',
        help="Include examples")
    parser.add_argument(
        "-g", "--group",
        action='store_true',
        dest='group',
        help="Group paths by tag")
    parser.add_argument(
        "-i", "--input",
        dest='input',
        required=True,
        help="Input file")
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w'),
        required=True,
        dest='output',
        help="Output file")

    options = parser.parse_args()
    logging.getLogger().setLevel(options.level)

    openapi_options = {}
    if options.paths:
        openapi_options['paths'] = options.paths
    if options.examples:
        openapi_options['examples'] = True
    if options.group:
        openapi_options['group'] = True

    openapi_options.setdefault('uri', 'file://%s' % options.input)
    spec = directive._get_spec(options.input, options.encoding)
    renderer = renderers.HttpdomainOldRenderer(None, openapi_options)

    for line in renderer.render_restructuredtext_markup(spec):
        options.output.write(line+'\n')
        logging.debug(line)


if __name__ == '__main__':
    main()
