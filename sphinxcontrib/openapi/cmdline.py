
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

class OpenApi(object):

    def __init__(self):
        self.options = {}

    def run(self,options):

        encoding = "ascii" #
        with io.open(options.input, 'rt', encoding=encoding) as stream:
            spec = yaml.load(stream, _YamlOrderedLoader)

        # URI parameter is crucial for resolving relative references. So
        # we need to set this option properly as it's used later down the
        # stack.
        self.options.setdefault('uri', 'file://%s' % options.input)

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

        for line in openapihttpdomain(spec, examples=True,**self.options):
            options.output.write(line+'\n')
            logging.debug(line)

def main():
    
    parser = argparse.ArgumentParser(prog='oas2rst',description='Export OpenAPI Specification files to reStructuredText files')
    parser.add_argument("-l", "--level",action='store',default=logging.INFO,dest='level',help="Logging level")
    parser.add_argument("-i", "--input",dest='input',required=True,help="Input file")
    parser.add_argument("-o", "--output",type=argparse.FileType('w'),required=True,dest='output',help="Output file")

    options = parser.parse_args()
    logging.getLogger().setLevel( options.level) #getattr(logging,options.level) )

    oa = OpenApi()
    oa.run(options)

def mime_sample():
    import email
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.mime.nonmultipart import MIMENonMultipart

    related = MIMEMultipart('mixed')

    def noop_encoder(msg):
        pass

    document = MIMENonMultipart('application', 'pdf')
    document.set_payload("%PDF-1.4...".encode("ascii"))
    del document['MIME-Version']
    related.attach(document)

    document = MIMENonMultipart('image', 'png')
    document.set_payload("%PNG...") #.encode("latin-1"))
    del document['MIME-Version']
    related.attach(document)

    document = MIMENonMultipart('image', 'jpeg')
    document.set_payload("ÿØÿá...") #.encode("ascii"))
    del document['MIME-Version']
    related.attach(document)

    data = related.as_string()
    print(data)
    
import sys
if __name__=='__main__':
    main()

