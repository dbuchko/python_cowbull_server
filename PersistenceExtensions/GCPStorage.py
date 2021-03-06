from flask_helpers.ErrorHandler import ErrorHandler
from google.oauth2 import service_account
from io import StringIO
from io import BytesIO
from Persistence.AbstractPersister import AbstractPersister
from six import text_type

import googleapiclient.discovery
import googleapiclient.http
import os


class Persister(AbstractPersister):

    #TODO : Refine error checking and logging

    def __init__(self, bucket=None):
        if not bucket:
            raise ValueError('A bucket name must be provided!')

        super(Persister, self).__init__()

        self.handler.module="GCPStoragePersist"
        self.handler.log(message="Validating if credentials are defined or if defaults should be used")
        secret_name = "/cowbull/secrets/k8storageservice.json"
        if not os.path.isfile(secret_name):
            self.handler.log(message="Requesting storage client with default credentials.", status=0)
            self.storage_client = googleapiclient.discovery.build('storage', 'v1', cache_discovery=False)
        else:
            self.handler.log(message="Requesting storage client with secret credentials.", status=0)
            credentials = service_account.Credentials.from_service_account_file(secret_name)
            self.handler.log(message="Credentials received: {}".format(credentials))

            self.handler.log(message="Requesting discovery of storage client.")
            self.storage_client = googleapiclient.discovery.build(
                'storage',
                'v1',
                credentials=credentials,
                cache_discovery=False
            )
            self.handler.log(message="Storage client retrieved.")


        self.handler.log(message="Storage client received. Setting bucket to {}".format(bucket), status=0)
        self.bucket = bucket

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)

        self.handler.log(message="Saving key {} with json {}".format(key, jsonstr))

        self.handler.log(message="Creating StreamIO object")
        contents = StringIO(initial_value=text_type(jsonstr))

        self.handler.log(message="Forming GCP Storage request")
        body = {
            'name': key,
            'contentType': 'application/json',
            'mimeType': 'application/json'
        }

        self.handler.log(message="Creating insert request")
        req = self.storage_client.objects().insert(
            bucket=self.bucket,
            body=body,
            media_mime_type='application/json',
            media_body=googleapiclient.http.MediaIoBaseUpload(contents, 'application/json')
        )
        self.handler.log(message="Insert request returned {}".format(req))

        self.handler.log(message="Executing GCP Storage request")
        try:
            resp = req.execute()
            self.handler.log(message="Response from execute: {}".format(resp))
        except Exception as e:
            self.handler.log(message="Exception: {}".format(repr(e)))
            raise

        self.handler.log(message="Closed temp file/stream with game data")

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Creating temporary file to hold results")

        return_result = None
        try:
            self.handler.log(message="Opening file in write mode")
            tmpfile = BytesIO()
            self.handler.log(message="File opened")

            self.handler.log(message="Issuing get_media request on {}".format(key))
            req = self.storage_client.objects().get_media(
                bucket=self.bucket,
                object=key
            )
            self.handler.log(message="Request on {} formed".format(key))

            self.handler.log(message="Creating downloader")
            downloader = googleapiclient.http.MediaIoBaseDownload(
                tmpfile,
                req
            )
            self.handler.log(message="Downloader created")

            self.handler.log(message="Downloading from downloader")
            done = False
            while not done:
                self.handler.log(message="Fetching chunk")
                status, done = downloader.next_chunk()
                self.handler.log(message="Fetch status: {}%".format(status.progress()*100))
            self.handler.log(message="Download complete")

            self.handler.log(message="Getting JSON")
            return_result = tmpfile.getvalue()
            self.handler.log(message="JSON is {} (type {})".format(
                return_result, type(return_result)
            ))

            self.handler.log(message="Converting bytes result to unicode (if reqd)")
            if return_result is not None:
                if isinstance(return_result, bytes):
                    return_result = str(return_result.decode('utf-8'))

            self.handler.log(message="Returning result: {}".format(return_result))
        except Exception as e:
            self.handler.log(message="Exception: {}".format(repr(e)))

        return return_result
