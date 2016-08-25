import httplib2
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def initialize_upload(youtube, options={}):
    tags = None
    if options.get('keywords'):
        tags = options.get('keywords').split(",")

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
        media_body=MediaFileUpload(options.get('filepath'), chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)


def resumable_upload(insert_request):
    response = None
    error = None
    rtn = None
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if 'id' in response:
                rtn = response
            else:
                error = "The upload failed with an unexpected response: %s" % response
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
    if rtn:
        return dict(status='200', response=rtn)
    else:
        return dict(status='500', response=error)
