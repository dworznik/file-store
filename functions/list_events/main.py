import functions_framework
from file_store.db import Database
from flask import jsonify


@functions_framework.http
def handler(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    with Database() as db:
        events = db.fetch_file_events()
        return jsonify(
            [
                {
                    "id": row.id,
                    "file_name": row.file_name,
                    "uploaded_at": row.uploaded_at,
                }
                for row in events
            ]
        )
