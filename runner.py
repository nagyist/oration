import datetime

import tweets

start = datetime.datetime.strptime("2012-10-21T17:18:45.610Z", tweets.UNIX_TIMESTAMP).isoformat('T')
end = datetime.datetime.strptime("2012-10-21T18:18:45.610Z", tweets.UNIX_TIMESTAMP).isoformat('T')


tweets.hashtag_search_in_daterange(start, end)


