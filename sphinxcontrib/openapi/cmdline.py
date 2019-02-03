
from __future__ import unicode_literals

import argparse
import collections
import io
import logging

import yaml

from sphinxcontrib.openapi import openapi20
from sphinxcontrib.openapi import openapi30


class _YamlOrderedLoader(yaml.SafeLoader):
    pass


_YamlOrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))
)

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

    with io.open(options.input, 'rt', encoding="ascii") as stream:
        spec = yaml.load(stream, _YamlOrderedLoader)

    # URI parameter is crucial for resolving relative references. So
    # we need to set this option properly as it's used later down the
    # stack.
    openapi_options = {'uri': 'file://%s' % options.input}

    # We support both OpenAPI 2.0 (f.k.a. Swagger) and OpenAPI 3.0.0, so
    # determine which version we are parsing here.
    spec_version = spec.get('openapi', spec.get('swagger', '2.0'))
    if spec_version.startswith('2.'):
        logging.info("OpenAPI 2.x Specification")
        openapihttpdomain = openapi20.openapihttpdomain
    elif spec_version.startswith('3.'):
        logging.info("OpenAPI 3.x Specification")
        openapihttpdomain = openapi30.openapihttpdomain
    else:
        raise ValueError('Unsupported OpenAPI version (%s)' % spec_version)

    for line in openapihttpdomain(spec, examples=True, **openapi_options):
        options.output.write(line+'\n')
        logging.debug(line)

if __name__ == '__main__':
    main()
