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
    <title>#bib12 Oration Output</title>
    <meta charset="utf-8" />
    <meta name="description" content="Annotated transcript of The self-publishing book: Books in Browsers 2012 presentation" />
    <meta name="author" content="Liza Daly, Keith Fahlgren"/>
      
    <link href='http://fonts.googleapis.com/css?family=Lato' rel='stylesheet' type='text/css' />

    <link rel="stylesheet" href="reveal/css/theme/simple.css" id="theme"/>

    <link rel="stylesheet" href="foundation/stylesheets/foundation.min.css" />
    <link rel="stylesheet" href="foundation/stylesheets/app.css"/>

    <script src="foundation/javascripts/modernizr.foundation.js">
    </script>
    <script src="foundation/javascripts/sbo.js">
    </script>
    <script type="text/javascript">
    <![CDATA[
refresh = readCookie(refreshCookieName);
if (refresh === null) {
  refresh = refreshCookieCount;
}
else {
  refresh -= 1;
}
createCookie(refreshCookieName, refresh, 1);
if (!refresh) {
  setTimeout(function () { location.href = location.href; }, secondsUntilRefresh * 1000);
}
]]>
  </script>  
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

        top_gradient = etree.SubElement(section, XHTML + "span", nsmap=NSMAP) 
        top_gradient.set("class", "top-gradient")
        top_gradient.text = " "
        bottom_gradient = etree.SubElement(section, XHTML + "span", nsmap=NSMAP) 
        bottom_gradient.set("class", "bottom-gradient")
        bottom_gradient.text = " "

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

#        if i % 2:
#            if i == 3:
#                slide_tweets = [{'text': u'This is totally not a test tweet #bib12', 
#                                 'when': created_time, 
#                                 'from_name': "Keith Fahlgren",
#                                 'from_at_name': "@abdelazer",
#                                 'from_url': "https://twitter.com/abdelazer",
#                                 'permalink': "https://twitter.com/abdelazer/status/260541769521979392",
#                                 'avatar': u'https://twimg0-a.akamaihd.net/profile_images/1884823295/k_baylands_sq_normal.jpg'},
#                                {'text': u'Neither is this. @abdelazer: This is totally not a test tweet #bib12', 
#                                 'when': created_time, 
#                                 'from_name': "Liza Daly",
#                                 'from_at_name': "@liza",
#                                 'from_url': "https://twitter.com/liza",
#                                 'permalink': "https://twitter.com/liza/status/260542218044076032",
#                                 'avatar': u'https://si0.twimg.com/profile_images/1448591106/liza-headshot-light-square_normal.jpg'},
#                                {'permalink': u'https://twitter.com/BiblioCrunch/statuses/260953774904971264',
#                                 'from_name': u'BiblioCrunch', 
#                                 'from_at_name': u'@BiblioCrunch', 
#                                 'text': u"Don't miss the @BiblioCrunch presenation on authoring platforms at #BIB12 Oct. 25th http://t.co/eqytczqr", 
#                                 'when': created_time,
#                                 'avatar': u'https://si0.twimg.com/profile_images/2576727093/joe8u53szbk047f49rf4_normal.jpeg',
#                                 'from_url': u'https://twitter.com/BiblioCrunch'}, 
#                                {'permalink': u'https://twitter.com/concisekathryn/statuses/260942171442671616', 
#                                 'from_name': u'Kathryn', 
#                                 'from_at_name': u'@concisekathryn', 
#                                 'text': u'so excited to be going to #bib12 in San Francisco this week!', 
#                                 'when': created_time,
#                                 'avatar': u'https://si0.twimg.com/profile_images/2675712735/93d52cedfdaf7eb2c288c93b110803d1_normal.png',
#                                 'from_url': u'https://twitter.com/concisekathryn'}, 
#                                {'permalink': u'https://twitter.com/agwieckowski/statuses/260924856613343233', 
#                                 'from_name': u'Ania Wieckowski', 
#                                 'from_at_name': u'@agwieckowski', 
#                                 'text': u'All packed for #bib12! Looking forward to seeing all you folks.', 
#                                 'when': created_time,
#                                 'avatar': u'https://si0.twimg.com/profile_images/1813017413/headshot1bwf_normal.jpg',
#                                 'from_url': u'https://twitter.com/agwieckowski'}, 
#                                {'permalink':
#                                 u'https://twitter.com/hughmcguire/statuses/260917610160472064', 
#                                 'from_name': u'Hugh McGuire', 
#                                 'from_at_name': u'@hughmcguire', 
#                                 'text': u'in sf for #bib12 ... anyone wanna grab a bite?', 
#                                 'when': created_time,
#                                 'avatar': u'https://si0.twimg.com/profile_images/1766808641/hugh-lookout_normal.jpg',
#                                 'from_url': u'https://twitter.com/hughmcguire'}, 
#                                {'permalink': u'https://twitter.com/Porter_Anderson/statuses/260897182373253120',
#                                 'from_name': u'Porter Anderson', 
#                                 'from_at_name': u'@Porter_Anderson', 
#                                 'text': u'"@CreativeCommons..up against the border of the commercial content world." @copyrightandtec w/ @jwikert http://t.co/JbJ5o6xY #BiB12 #TOCcon', 
#                                 'when': created_time, 
#                                 'avatar': u'https://si0.twimg.com/profile_images/1218111533/Porter_Anderson_thumb_close2__Photo_Jeff_Cohen__normal.jpg',
#                                 'from_url': u'https://twitter.com/Porter_Anderson'}
#                               ]
#

        for tweet in slide_tweets:
            p = etree.SubElement(tweets_div, XHTML + "p", nsmap=NSMAP)
            p.set("class", "tweet")

            avatar = etree.SubElement(p, XHTML + "a", nsmap=NSMAP)
            avatar.set("href", tweet["from_url"])
            avatar.set("class", "tweet-avatar")
            avatar_img = etree.SubElement(avatar, XHTML + "img", nsmap=NSMAP)
            avatar_img.set("src", tweet['avatar'])


            who = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            who.set("class", "tweet-who")
            who_a = etree.SubElement(who, XHTML + "a", nsmap=NSMAP)
            who_a.set("href", tweet["from_url"])
            who_a.text = tweet["from_name"]

            who_user = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            who_user.set("class", "tweet-who-at")
            who_user_a = etree.SubElement(who_user, XHTML + "a", nsmap=NSMAP)
            who_user_a.set("href", tweet["from_url"])
            who_user_a.text = tweet["from_at_name"]

            follow_iframe = etree.SubElement(p, XHTML + "iframe", nsmap=NSMAP)
            follow_iframe.set("allowtransparency", "true")
            follow_iframe.set("frameborder", "0")
            follow_iframe.set("scrolling", "no")
            follow_iframe.set("src", "//platform.twitter.com/widgets/follow_button.html?screen_name=%s&show_count=false&show_screen_name=false" % tweet["from_at_name"].lstrip("@"))
            follow_iframe.set("style", "width: 300px; height:20px;")
            follow_iframe.text = " "
    

            txt = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            txt.text = tweet['text']
            txt.set("class", "tweet-text")
            when = etree.SubElement(p, XHTML + "span", nsmap=NSMAP)
            when.set("class", "tweet-when")
            when_a = etree.SubElement(when, XHTML + "a", nsmap=NSMAP)
            when_a.set("href", tweet['permalink'])
            when_a.text = tweet['when']


        body.append(section)



    # Collect all the relevant tweets and try to line them up
    return html

def _git_publish(fn):
    log.info("\nPublishing to GitHub Pages now...\n")
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
    return matches




if __name__ == "__main__":
    args = sys.argv[1:]

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.add_option("-c", "--continuous", action="store_true", dest="continuous", help="Run the code generation and commiting continuously")
    parser.add_option("-g", "--get-api-code", action="store_true", dest="get_api_code", help="Generate a new API code")

    (options, args) = parser.parse_args(args)    

    if options.get_api_code:
        authorize_url = docs.generate_authorization_url()
        print "Open a browser to %s" % authorize_url
        code = raw_input('Enter verification code: ').strip()
        docs.save_credentials(code)

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

