Oration
=======

Oration transforms a series of Google Docs inside a folder into a presentation with static HTML in
the center, Google Doc comments on the left, and Tweets matching a hashtag on the right..

For the background, see http://techblog.safaribooksonline.com/2012/11/16/capturing-more-authoring/
For an example of (styled) output: http://public.safarilab.com/talks/bib-2012-self-publishing-book/

Developer Setup
~~~~~~~~~~~~~~~

1. `git clone ...`
2. `cd oration`
3. `virtualenv --python=python2.7 --prompt="(oration)" ve`
4. `. ve/bin/activate`
5. `python setup.py develop --always-unzip`
6. `cp local.py.example local.py`
7. Register/retrieve Twitter app key/secrets and add to local.py
8. Register/retrieve Google app key/secrets and add to local.py
9. Find Google Docs folder ID and add to local.py
10. Pick a #hashtag and add to local.py
11. `./generate_html.py -h`
12. Download foundation.min.css from and put it in this dir (if you want it to look pretty)

Comments
~~~~~~~~

It probably will not work for you. If it does, it is likely that it worked because you made the
Google Docs relatively recently and did not get banned by the Twitter API. 

