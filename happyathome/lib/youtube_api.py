import os

import httplib2
from flask import current_app
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from happyathome.models import File
from oauth2client import service_account

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def auth_account():
    credentials = service_account.ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(current_app.root_path, 'HappyAtHome-YouTube-b682b3e6d89a.json'),
        scopes=current_app.config['YOUTUBE_API_SCOPES']
    )
    delegated_credentials = credentials.create_delegated('dev@inotone.co.kr')
    youtube = discovery.build(current_app.config['YOUTUBE_API_SERVICE_NAME'],
                              current_app.config['YOUTUBE_API_VERSION'],
                              http=delegated_credentials.authorize(httplib2.Http()))

    return youtube


def initialize_upload(youtube, options={}):
    tags = options.get('keywords').split(',') if options.get('keywords') else None

    body = dict(
        snippet=dict(
            title=options.get('title'),
            description=options.get('description'),
            tags=tags,
        ),
        status=dict(
            privacyStatus='public'
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.get('file_path'), chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request, options.get('file'))


def resumable_upload(insert_request, file):
    response = None
    error = None
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if 'id' in response:
                file.cid = response['id']
            else:
                error = "The upload failed with an unexpected response: %s" % response
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
