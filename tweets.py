#!/usr/bin/env python
# encoding: utf-8
# Created by Keith Fahlgren <keith@safaribooksonline.com> on Wed Oct 17 11:17:21 PDT 2012
# Copyright (c) 2012 Safari Books Online, LLC. All rights reserved.

import datetime
import logging

from twitter import *

from settings import *

TWITTER_WTF_DATE_FMT = "%a, %d %b %Y %H:%M:%S +0000"

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

t = Twitter(domain=TWITTER_SEARCH_DOMAIN,
            auth=OAuth(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET))

def hashtag_search_in_daterange(start, end):
    search_resp = t.search(q=TWITTER_HASHTAG)
    tweets = []
    for tweet in search_resp['results']:
        when = datetime.datetime.strptime(tweet['created_at'], TWITTER_WTF_DATE_FMT).isoformat('T')
        avatar = tweet['profile_image_url_https']

        # INFO:tweets:@naypinya Looking forward to the Books in Browsers conference. @RedBridgePress #bib12 at 2012-10-17T16:39:51
        # INFO:tweets:RT @gunzalis: @raffers @dinoboy89 @samatlounge I am not. I'm sweating my #bib12 talk instead in NorCal. at 2012-10-17T16:17:48
        log.debug("%s v %s v %s" % (start, when, end))
        if when > start and when < end:
            tweet = {'text': tweet['text'],
                    'avatar': avatar,
                    'when': when}
            tweets.append(tweet)
    return tweets


