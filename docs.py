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

def generate_authorization_url():
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    return authorize_url

def setup_api_service(code):
    flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    log.debug(code)
    flow.step1_get_authorize_url()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)
    return drive_service

def export_file(service, g_file):
    download_url = g_file['exportLinks']['text/html']
    resp, content = service._http.request(download_url)
    log.debug(content)
    return content

def folder_contents(service, folder_id=GOOGLE_FOLDER_ID):
    results = []
    params = {"q": "trashed=False"}
    page_token = None

    while True:
        if page_token:
            params['pageToken'] = page_token
        children = service.children().list(folderId=folder_id, **params).execute()

        for child in children.get('items', []):
            child_file = service.files().get(fileId=child['id']).execute()
            results.append(child_file)

        page_token = children.get('nextPageToken')
        if not page_token:
            break
    return results
