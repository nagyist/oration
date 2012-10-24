EXPORT_FILENAME = "index.html"

TWITTER_OAUTH_TOKEN = "15108695-Dr8urmlyAPQ6fd7QTYd3hYRtn8nI6nNXNeQe4Rg2M"
TWITTER_OAUTH_SECRET = "a7Ve4DTX8kwpMA3pXPPndMNvD6bOeLgfSaUuR7jCoXA"
TWITTER_CONSUMER_KEY = "zH4rnDfJtqxDt7qimIA" # Keith's
TWITTER_CONSUMER_SECRET = "odWIqyuOuGNTpBq8HJBPdSp5Ga4OcLrGKQeF1gfcc"
TWITTER_SEARCH_DOMAIN = "search.twitter.com"

TWITTER_HASHTAG = "#bib12"

GOOGLE_CLIENT_ID = "279382989528-gp2s1cctku0239l12u7qm7qs1sjbvihl.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "7M6cRxumgDJlpjlNUybVJE2d"

GOOGLE_FOLDER_ID = '0B5YOxLevHBt1OEVCWEVleDZGcWs'

# Last resort (good for dev machines): import settings that aren't in the repo.
try:
    from local import *
except ImportError, e:
    pass
