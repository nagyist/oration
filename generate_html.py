#!/usr/bin/env python
# encoding: utf-8

import logging
import sys

from optparse import OptionParser


import lxml.html

from lxml import etree
from lxml.html import html5parser


import docs
import tweets

from settings import *

XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
XHTML = "{%s}" % XHTML_NAMESPACE

NSMAP = {None : XHTML_NAMESPACE} 
NSS = {"x": XHTML_NAMESPACE}

HTML_TEMPLATE = """<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>#bib12 Oration Output</title>
    <meta charset="utf-8" />
    <meta name="description" content="Annotated transcript of The self-publishing book: Books in Browsers 2012 presentation" />
    <meta name="author" content="Liza Daly, Keith Fahlgren"/>
      
    <link rel="stylesheet" href="reveal/css/theme/simple.css" id="theme"/>

    <link rel="stylesheet" href="foundation/stylesheets/foundation.min.css" />
    <link rel="stylesheet" href="foundation/stylesheets/app.css"/>

    <script src="foundation/javascripts/modernizr.foundation.js">
    </script>
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

def build_html():
    service = docs.setup_api_service()

    html = etree.fromstring(HTML_TEMPLATE)
    
    body = html.xpath("/x:html/x:body", namespaces=NSS)[0]
    # Collect all the Google Docs in the Folder as HTML
    children = docs.folder_contents(service)
    sorted_children = sorted(children, key=lambda x: x['createdDate'])
    start = sorted_children[0]['createdDate']
    end = sorted_children[-1]['createdDate']
    matching_tweets = tweets.hashtag_search_in_daterange(start, end)
    log.info("Matching tweets: %s" % matching_tweets)
    for child in sorted_children:
        log.info(u"Appending slide %s" % child['title'])
        slide = html5parser.fromstring(docs.export_file(service, child))
        slide_body = slide.xpath("/x:html/x:body", namespaces=NSS)[0]
        section = etree.Element(XHTML + "section", nsmap=NSMAP) 
        section.set("data-ts", child['createdDate'])
        section.set("class", "row six columns")

        #log.debug(etree.tostring(slide))
        for slide_body_child in slide_body:
            section.append(slide_body_child)
        body.append(section)

    # Collect all the relevant tweets and try to line them up
    return html





if __name__ == "__main__":
    args = sys.argv[1:]

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.add_option("-g", "--get-api-code", action="store_true", dest="get_api_code", help="Generate a new API code")

    (options, args) = parser.parse_args(args)    

    if options.get_api_code:
        authorize_url = docs.generate_authorization_url()
        print "Open a browser to %s" % authorize_url
        code = raw_input('Enter verification code: ').strip()
        docs.save_credentials(code)

        sys.exit(0)
    else:
        html_content = build_html()
        with open(EXPORT_FILENAME, "w") as f:
            et = etree.ElementTree(html_content)
            et.write(f)

