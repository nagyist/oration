#!/usr/bin/env python
# encoding: utf-8

import datetime
import logging

import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


from settings import *


log = logging.getLogger(__name__)

OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def generate_authorization_code():
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    log.info("Visit %s", authorize_url)

def authorize_http(code):
    flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http

def file_export_url():
    drive_service = build('drive', 'v2', http=http)
    drive_service.files.get({'fileId': GOOGLE_FILE_ID})
