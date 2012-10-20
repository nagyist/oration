#!/usr/bin/env python
# encoding: utf-8

import logging
import sys

from optparse import OptionParser


import lxml.html

from lxml import etree
from lxml.html import html5parser


import docs

from settings import *

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <title>#bib12 Oration Output</title>
    <meta charset="utf-8" />
    <meta name="description" content="Annotated transcript of The self-publishing book: Books in Browsers 2012 presentation" />
    <meta name="author" content="Liza Daly, Keith Fahlgren"/>
      
    <link rel="stylesheet" href="reveal/css/reveal.css"/>
    <link rel="stylesheet" href="reveal/css/theme/simple.css" id="theme"/>

    <link rel="stylesheet" href="reveal/lib/css/zenburn.css"/>

    <!-- If the query includes 'print-pdf', use the PDF print sheet -->
    <script>document.write( '<link rel="stylesheet" href="reveal/css/print/' + ( window.location.search.match( /print-pdf/gi ) ? 'pdf' : 'paper' ) + '.css" type="text/css" media="print">' );</script>
      
  </head>

  <body>
  </body>
</html>"""

# Tweet alignment (from Matthew)
# so get all the tweets, use data-ts (or something like it)
# and for each slide, find the first tweet where the ts is > the slide ts (but less than the next)
# but the key is to make them all position: relative
# to get collision detection
# so that you're only adjusting when you need to slide all of them down
# so set the css('top') of the tweet w/the offset().top of the slide
# you might have to calculate it
# get offset().top of both, find the difference, and then that will be the css('top') you want to set
# but the tweets after the first one should just fall under it after you adjust it

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

def build_html(api_code):
    service = docs.setup_api_service(api_code)

    html = lxml.html.document_fromstring(HTML_TEMPLATE)
    body = html.xpath("/html/body")[0]
    # Collect all the Google Docs in the Folder as HTML
    for child in docs.folder_contents(service):
        slide = html5parser.fromstring(docs.export_file(service, child))
        #log.debug(etree.tostring(slide))
        body.append(slide)

    # Collect all the relevant tweets and try to line them up
    return html





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
            et = etree.ElementTree(html_content)
            et.write(f)

