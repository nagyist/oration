#!/usr/bin/env python
# encoding: utf-8

import logging
import sys

from optparse import OptionParser


import lxml.html

from lxml import etree


from settings import *


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

def build_html(api_code):
    service = docs.setup_api_service(api_code)

    # Collect all the Google Docs in the Folder as HTML
    for child in docs.folder_contents(service):
        slide = lxml.html.fragment_fromstring(docs.export_file(child))
        log.debug(etree.tostring(slide))

    # Collect all the relevant tweets and try to line them up





if __name__ == "__main__":
    args = sys.argv[1:]

    usage = "usage: %prog [options] [api code]"

    parser = OptionParser(usage)

    parser.add_option("-g", "--get-api-code", action="store_true", dest="get_api_code", help="Generate a new API code")

    (options, args) = parser.parse_args(args)    

    if len(args) == 0 and not options.get_api_code:
        parser.print_help()
        sys.exit(1)
    elif options.get_api_code:
        authorize_url = docs.generate_authorization_url()
        print "Open a browser to %s" % authorize_url
        sys.exit(0)
    else:
        api_code = args[0]
        html_content = build_html(api_code)
        with open(EXPORT_FILENAME, "w") as f:
            html_content.write(f)

