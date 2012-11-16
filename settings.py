EXPORT_FILENAME = "index.html"

CONTINUOUS_WAIT_SECONDS = 15

TWITTER_OAUTH_TOKEN = None # in local.py
TWITTER_OAUTH_SECRET = None # in local.py
TWITTER_CONSUMER_KEY = None # in local.py
TWITTER_CONSUMER_SECRET = None # in local.py

TWITTER_SEARCH_DOMAIN = "search.twitter.com"
TWITTER_HASHTAG = "#twitter" # probably in local.py

GOOGLE_CLIENT_ID = None # in local.py
GOOGLE_CLIENT_SECRET = None # in local.py

GOOGLE_FOLDER_ID = None # in local.py

# Last resort (good for dev machines): import settings that aren't in the repo.
try:
    from local import *
except ImportError, e:
    pass
