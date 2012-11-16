#!/usr/bin/env python
# encoding: utf-8

import datetime
import logging
import subprocess
import sys
import time

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
    <title>Oration Output</title>
    <meta charset="utf-8" />

    <!-- Stylesheets here -->
    <link rel="stylesheet" href="foundation.min.css"/>
  </head>

  <body>
  </body>
</html>"""

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

def build_html():
    service = docs.setup_api_service()

    html = etree.fromstring(HTML_TEMPLATE)
    body = html.xpath("/x:html/x:body", namespaces=NSS)[0]


    the_google_docs = _collect_google_docs_inside_folder(service)

    first_doc_created_at = the_google_docs[0]['createdDate']
    last_doc_created_at = the_google_docs[-1]['createdDate']
    end_search_timestamp = _minutes_later(last_doc_created_at, num_minutes=5)

    tweet_search_results = tweets.hashtag_search_in_daterange(first_doc_created_at, end_search_timestamp)

    for i, child in enumerate(the_google_docs):
        log.info(u"Appending slide %s" % child['title'])
        slide = html5parser.fromstring(docs.export_file(service, child))
        created_time = child['createdDate']
        slide_body = slide.xpath("/x:html/x:body", namespaces=NSS)[0]

        the_slide_html_section = _generate_slide_html_section(slide_body, created_time, the_google_docs, i, tweet_search_results)

        body.append(the_slide_html_section)

    return html

def _collect_google_docs_inside_folder(service):
    # Collect all the Google Docs in the Folder as HTML
    children = docs.folder_contents(service)
    sorted_children = sorted(children, key=lambda x: x['createdDate'])
    return sorted_children

def _generate_slide_html_section(slide_body, created_time, the_google_docs, doc_idx, tweet_search_results):
    section = etree.Element(XHTML + "section", nsmap=NSMAP) 
    section.set("data-ts", created_time )
    section.set("class", "row")

    comments_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP) 
    comments_div.set("class", "comments three columns") # classes work well with Zurb foundation
    comments_div.text = " "
    comments_div.tail = "\n"

    slide_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP)
    slide_div.set("class", "slide six columns")
    slide_div.tail = "\n"

    tweets_div = etree.SubElement(section, XHTML + "div", nsmap=NSMAP) 
    tweets_div.set("class", "tweets three columns")
    tweets_div.text = " "
    tweets_div.tail = "\n"

    top_gradient = etree.SubElement(section, XHTML + "span", nsmap=NSMAP) 
    top_gradient.set("class", "top-gradient")
    top_gradient.text = " "
    bottom_gradient = etree.SubElement(section, XHTML + "span", nsmap=NSMAP) 
    bottom_gradient.set("class", "bottom-gradient")
    bottom_gradient.text = " "

    for slide_body_child in slide_body:
        # SUPER GROSS insertion of Google Docs comments
        num_comments = len(slide_body_child.xpath(".//x:a[starts-with(@href, '#cmnt_ref')]", namespaces=NSS))
        if num_comments > 0:
            comments_div.append(slide_body_child)
        else:
            slide_div.append(slide_body_child)

    next_created_time = None
    try:
        next_created_time = the_google_docs[doc_idx + 1]['createdDate']
    except IndexError:
        pass

    slide_tweets = _match_tweets(tweet_search_results, created_time, next_created_time)
    log.debug("Matching tweets for slide %s [%s]: %s" % (doc_idx, created_time, slide_tweets))

    for tweet in slide_tweets:
        tweet_p = _generate_tweet_html(tweet)
        tweets_div.append(tweet_p)

    section.tail = "\n"
    return section

def _generate_tweet_html(tweet):
    # Note that Twitter would like you to add all sorts of other formatting but
    # doesn't bother to help you do this, so use at your own risk...
    tweet_p = etree.Element(XHTML + "p", nsmap=NSMAP)
    tweet_p.set("class", "tweet")

    avatar = etree.SubElement(tweet_p, XHTML + "a", nsmap=NSMAP)
    avatar.set("href", tweet["from_url"])
    avatar.set("class", "tweet-avatar")
    avatar_img = etree.SubElement(avatar, XHTML + "img", nsmap=NSMAP)
    avatar_img.set("src", tweet['avatar'])

    who = etree.SubElement(tweet_p, XHTML + "span", nsmap=NSMAP)
    who.set("class", "tweet-who")
    who_a = etree.SubElement(who, XHTML + "a", nsmap=NSMAP)
    who_a.set("href", tweet["from_url"])
    who_a.text = tweet["from_name"]

    who_user = etree.SubElement(tweet_p, XHTML + "span", nsmap=NSMAP)
    who_user.set("class", "tweet-who-at")
    who_user_a = etree.SubElement(who_user, XHTML + "a", nsmap=NSMAP)
    who_user_a.set("href", tweet["from_url"])
    who_user_a.text = tweet["from_at_name"]

    follow_iframe = etree.SubElement(tweet_p, XHTML + "iframe", nsmap=NSMAP)
    follow_iframe.set("allowtransparency", "true")
    follow_iframe.set("frameborder", "0")
    follow_iframe.set("scrolling", "no")
    follow_iframe.set("src", "//platform.twitter.com/widgets/follow_button.html?screen_name=%s&show_count=false&show_screen_name=false" % tweet["from_at_name"].lstrip("@"))
    follow_iframe.set("style", "width: 300px; height:20px;")
    follow_iframe.text = " "

    txt = etree.SubElement(tweet_p, XHTML + "span", nsmap=NSMAP)
    txt.text = tweet['text']
    txt.set("class", "tweet-text")
    when = etree.SubElement(tweet_p, XHTML + "span", nsmap=NSMAP)
    when.set("class", "tweet-when")
    when_a = etree.SubElement(when, XHTML + "a", nsmap=NSMAP)
    when_a.set("href", tweet['permalink'])
    when_a.text = tweet['when']
    
    tweet_p.tail = "\n"
    return tweet_p

def _git_publish(fn):
    log.info("\nPublishing to git repo now...\n")
    subprocess.call(["git", 
                     "commit", 
                     "-m'Automated commit from oration.generate_html at %s'" % datetime.datetime.utcnow().isoformat(),
                     fn])
    subprocess.call(["git", 
                     "push"])

def _match_tweets(the_tweets, start, end=None):
    matches = []
    for tweet in the_tweets:
        when = tweet['when']
        if when >= start and end is None:
            matches.append(tweet)
        elif when >= start and when < end:
            matches.append(tweet)
    matches.reverse()
    return matches

def _minutes_later(timestamp, num_minutes=5):
    # Add n minutes to 2012-10-21T18:18:45.610Z
    # gross
    timestamp_split = timestamp.split(":")
    num_minutes = 5
    add_some_minutes = str(float(timestamp_split[2].rstrip("Z")) + num_minutes)
    end = ":".join([timestamp_split[0], timestamp_split[1], add_some_minutes]) + "Z"
    return end




if __name__ == "__main__":
    args = sys.argv[1:]

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.add_option("-c", "--continuous", action="store_true", dest="continuous", help="Run the code generation continuously, commit to a git repo, and push on every generation")
    parser.add_option("-g", "--get-api-code", action="store_true", dest="get_api_code", help="Generate a new API code (do this first!)")

    (options, args) = parser.parse_args(args)    

    if options.get_api_code:
        authorize_url = docs.generate_authorization_url()
        print "Open a browser to %s" % authorize_url
        code = raw_input('Enter verification code: ').strip()
        docs.save_credentials(code)

        print "\nThanks, now run this with different arguments next time (or none)"

        sys.exit(0)
    elif options.continuous:
        while True:
            html_content = build_html()
            with open(EXPORT_FILENAME, "w") as f:
                f.write(lxml.html.tostring(html_content, pretty_print=True))

            _git_publish(EXPORT_FILENAME)

            log.info("\nNow sleeping %s seconds...\n" % CONTINUOUS_WAIT_SECONDS)
            time.sleep(CONTINUOUS_WAIT_SECONDS)
    else:
        html_content = build_html()
        with open(EXPORT_FILENAME, "w") as f:
            lxml.html.tostring(html_content)
            f.write(lxml.html.tostring(html_content, pretty_print=True))

