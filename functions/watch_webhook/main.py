import json
import logging

import functions_framework
import google.cloud.logging
from flask import request

from file_store.gcp.drive import is_upload

# Initialize the Google Cloud logging client and set up logging
client = google.cloud.logging.Client()
client.setup_logging()


@functions_framework.http
def handler(request):
    if request.method == "POST":
        id = request.headers.get("X-Goog-Resource-ID")
        uri = request.headers.get("X-Goog-Resource-URI")
        channel = request.headers.get("X-Goog-Channel-ID")
        state = request.headers.get("X-Goog-Resource-State")
        changes = request.headers.get("X-Goog-Changed")

        logging.info(
            json.dumps(
                {
                    "channel": channel,
                    "id": id,
                    "uri": uri,
                    "state": state,
                    "changes": changes
                }
            )
        )

        if is_upload(state, changes):
            logging.info(f"File(s) uploaded to {id}")

        return "", 200

    else:
        return "Method not allowed", 405
