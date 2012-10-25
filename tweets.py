#!/usr/bin/env python
# encoding: utf-8
# Created by Keith Fahlgren <keith@safaribooksonline.com> on Wed Oct 17 11:17:21 PDT 2012
# Copyright (c) 2012 Safari Books Online, LLC. All rights reserved.

import json
import datetime
import logging
import urllib2

from twitter import *

from settings import *

TWITTER_WTF_DATE_FMT = "%a, %d %b %Y %H:%M:%S +0000"
UNIX_TIMESTAMP = "%Y-%m-%dT%H:%M:%S.%fZ"

class AllTweetsFoundError(Exception): pass # dirty hack

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

t = Twitter(domain=TWITTER_SEARCH_DOMAIN,
            auth=OAuth(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET))

MIN_TIME = datetime.datetime(2012, 10, 22, 12, 10, 10, 550).isoformat('T')
MAX_TIME = datetime.datetime(2012, 10, 23, 4, 10, 10, 550).isoformat('T')

search_url = "http://{}/search.json".format(TWITTER_SEARCH_DOMAIN)

def hackhackhack(next_page):
    response = urllib2.urlopen("{}{}&rpp=100".format(search_url, next_page))
    data = response.read()
    return json.loads(data)

def iterate_search_pages(query, num_pages=20):
    '''iterate over all pages of a tweet query 
    be careful though! The potential for lots of API calls
    '''
    search_response = t.search(q=query)
    pages = 0
    while search_response.get('next_page') and pages <= num_pages:
        log.debug("Page: {}".format(pages))
        yield search_response.get('results')
        pages += 1
        log.debug("next page: {}".format(search_response['next_page']))
        search_response = hackhackhack(search_response['next_page'])

def iterate_valid_tweets(tweets, min_time=MIN_TIME, max_time=MAX_TIME):
    for tweet in tweets:
        when = datetime.datetime.strptime(tweet['created_at'], TWITTER_WTF_DATE_FMT).isoformat('T')
        if when < min_time:
            log.debug("STOPPING for %s v %s" % (when, max_time))
            raise AllTweetsFoundError
        if when >= min_time and when <= max_time:
            log.debug("%s v %s v %s" % (min_time, when, max_time))
            yield tweet

def hashtag_search_in_daterange(start, end):
    tweets = []
    for tweet_page in iterate_search_pages(TWITTER_HASHTAG):
        try:
            for valid_tweet in iterate_valid_tweets(tweet_page, min_time=start, max_time=end):
                avatar = valid_tweet['profile_image_url_https']
                when = datetime.datetime.strptime(valid_tweet['created_at'],
                        TWITTER_WTF_DATE_FMT).isoformat('T')
                from_name = valid_tweet['from_user_name']
                from_at_name = u"@%s" % valid_tweet['from_user']
                from_url = u"https://twitter.com/%s" % valid_tweet['from_user']
                permalink = u"https://twitter.com/%s/statuses/%s" % (valid_tweet['from_user'], valid_tweet['id_str'])

                # INFO:tweets:@naypinya Looking forward to the Books in Browsers conference. @RedBridgePress #bib12 at 2012-10-17T16:39:51
                # INFO:tweets:RT @gunzalis: @raffers @dinoboy89 @samatlounge I am not. I'm sweating my #bib12 talk instead in NorCal. at 2012-10-17T16:17:48
                tweet = {'text': valid_tweet['text'],
                         'avatar': avatar,
                         'from_name': from_name,
                         'from_at_name': from_at_name,
                         'from_url': from_url,
                         'permalink': permalink,
                         'when': when}
                tweets.append(tweet)
        except AllTweetsFoundError:
            break
    return tweets
