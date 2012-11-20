from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='oration',
      version=version,
      description="Oration captures a set of Google Docs and tweets as interesting HTML",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Keith Fahlgren',
      author_email='keith@safaribooksonline.com',
      url='http://techblog.safaribooksonline.com/2012/11/22/oration-tool-for-html-from-goodocs-and-tweets/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "html5lib",
          "lxml",
          "twitter >= 1.9",
          "google-api-python-client",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
