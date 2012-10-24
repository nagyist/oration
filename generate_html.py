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
    last_start = sorted_children[-1]['createdDate']
    # Add a minute to 2012-10-21T18:18:45.610Z
    last_start_split = last_start.split(":")
    add_two_minutes = str(float(last_start_split[2].rstrip("Z")) + 2)
    end = ":".join([last_start_split[0], last_start_split[1], add_two_minutes]) + "Z"
    tweet_search_results = tweets.hashtag_search_in_daterange(start, end)

    for i, child in enumerate(sorted_children):
        log.info(u"Appending slide %s" % child['title'])
        slide = html5parser.fromstring(docs.export_file(service, child))
        created_time = child['createdDate']
        slide_body = slide.xpath("/x:html/x:body", namespaces=NSS)[0]
        section = etree.Element(XHTML + "section", nsmap=NSMAP) 
        section.set("data-ts", created_time )
        section.set("class", "row")

        comments_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP) 
        comments_div.set("class", "comments three columns")
        comments_div.text = " "

        slide_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP)
        slide_div.set("class", "slide six columns")

        tweets_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP) 
        tweets_div.set("class", "tweets three columns")
        tweets_div.text = " "

        #log.debug(etree.tostring(slide))
        for slide_body_child in slide_body:
            num_comments = len(slide_body_child.xpath(".//x:a[starts-with(@href, '#cmnt_ref')]", namespaces=NSS))
            if num_comments > 0:
                comments_div.append(slide_body_child)
            else:
                slide_div.append(slide_body_child)


        next_created_time = None
        try:
            next_created_time = sorted_children[i + 1]['createdDate']
        except IndexError:
            pass

        slide_tweets = _match_tweets(tweet_search_results, created_time, next_created_time)
        log.debug("Matching tweets for slide %s [%s]: %s" % (i, created_time, slide_tweets))

        #if i % 2:
        #    if i == 3:
        #        slide_tweets = [{'text': u'This is totally not a test tweet #bib12', 'when': created_time, 'avatar': u'https://twimg0-a.akamaihd.net/profile_images/1884823295/k_baylands_sq_normal.jpg'},
        #                        {'text': u'Neither is this. @abdelazer: This is totally not a test tweet #bib12', 'when': created_time, 'avatar': u'https://si0.twimg.com/profile_images/1448591106/liza-headshot-light-square_normal.jpg'}]
        #    else:
        #        slide_tweets = [{'text': u'Neither is this. @abdelazer: This is totally not a test tweet #bib12', 'when': created_time, 'avatar': u'https://si0.twimg.com/profile_images/1448591106/liza-headshot-light-square_normal.jpg'}]


        for tweet in slide_tweets:
            p = etree.SubElement(tweets_div, XHTML + "p", nsmap=NSMAP)
            p.set("class", "tweet")
            txt = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            txt.text = tweet['text']
            txt.set("class", "tweet-text")
            when = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            when.text = tweet['when']
            when.set("class", "tweet-when")
            avatar = etree.SubElement(p, XHTML + "img", nsmap=NSMAP)
            avatar.set("src", tweet['avatar'])
            avatar.set("class", "tweet-avatar")


        body.append(section)



    # Collect all the relevant tweets and try to line them up
    return html


def _match_tweets(the_tweets, start, end=None):
    matches = []
    for tweet in the_tweets:
        when = tweet['when']
        if when >= start and end is None:
            matches.append(tweet)
        elif when >= start and when < end:
            matches.append(tweet)
    return matches



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

