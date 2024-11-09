from hashlib import sha256
import json
import os
import io
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import Resource

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"]


def is_upload(state: str, changed: str):
    return state == "update" and changed == "children"


def get_credentials(service_account_file):
    return service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )


def build_drive_service(credentials) -> Resource:
    return build("drive", "v3", credentials=credentials)


def get_start_page_token(drive_service: Resource) -> str:
    """
    Retrieves the start page token for the given drive service.

    Args:
        drive_service (googleapiclient.discovery.Resource): The drive service used to retrieve the start page token.

    Returns:
        str: The start page token.

    Raises:
        googleapiclient.errors.HttpError: If an HTTP error occurs while retrieving the start page token.
    """
    start_page_token_response = drive_service.changes().getStartPageToken().execute()
    return start_page_token_response.get("startPageToken")


def setup_watch(drive_service: Resource, start_page_token: str, webhook_url: str, folder_id: str):
    """
    Sets up a watch on Google Drive changes.

    Args:
        drive_service (googleapiclient.discovery.Resource): An instance of the Google Drive API service.
        start_page_token (str): The start page token to retrieve changes.
        webhook_url (str): The URL of the webhook to receive notifications.
        folder_id (str): The ID of the folder to observe.

    Returns:
        dict: The response from the Google Drive API indicating the status of the watch.
    """
    request_body = {
        "id": f"{folder_id}-test-{sha256(webhook_url.encode()).hexdigest()[:10]}",  # prevent creating duplicate watches
        "type": "web_hook",
        "address": webhook_url,
    }
    watch_response = (
        drive_service.changes()
        .watch(pageToken=start_page_token, body=request_body)
        .execute()
    )

    # Add folder-specific watch
    drive_service.files().watch(fileId=folder_id, body=request_body).execute()

    return watch_response


def stop_watch(drive_service: Resource, resource_id: str, channel_id: str):
    """
    Stops a watch on Google Drive changes.

    Args:
        drive_service (googleapiclient.discovery.Resource): An instance of the Google Drive API service.
        resource_id (str): The ID of the resource being watched.
        channel_id (str): The ID of the channel to stop the watch on.

    Returns:
        dict: The response from the Google Drive API indicating the status of the stop operation.
    """
    request_body = {
        "id": channel_id,
        "resourceId": resource_id,
    }
    response = drive_service.channels().stop(body=request_body).execute()
    return response


def folder_info(drive_service: Resource, folder_id: str):
    """
    Retrieves information about a folder in Google Drive.

    Args:
        drive_service (googleapiclient.discovery.Resource): An instance of the Google Drive API service.
        folder_id (str): The ID of the folder to retrieve information for.

    Returns:
        dict or None: A dictionary containing the folder's information, or None if an error occurred.
    """
    try:
        folder = (
            drive_service.files()
            .get(fileId=folder_id, fields="id, name, mimeType, parents, modifiedTime")
            .execute()
        )
        return folder
    except HttpError as error:
        print(f"An error occurred: {error}")
        if error.resp.status == 404:
            print(f"Folder not found: {folder_id}")
        else:
            print(error.content)
        return None


def fetch_changes(drive_service, saved_start_page_token):
    """Retrieve the list of changes for the currently authenticated user.
        prints changed file's ID
    Args:
        drive_service: Drive service
        saved_start_page_token : StartPageToken for the current state of the
        account.
    Returns: saved start page token.
    """

    try:

        # Begin with our last saved start token for this user or the
        # current token from getStartPageToken()
        page_token = saved_start_page_token
        # pylint: disable=maybe-no-member

        while page_token is not None:
            response = (
                drive_service.changes()
                .list(pageToken=page_token, spaces="drive")
                .execute()
            )
            print(json.dumps(response))
            for change in response.get("changes"):
                # Process change
                print(f'Change found" {json.dumps(change)}')
            if "newStartPageToken" in response:
                # Last page, save this token for the next polling interval
                saved_start_page_token = response.get("newStartPageToken")
            page_token = response.get("nextPageToken")

    except HttpError as error:
        print(f"An error occurred: {error}")
        saved_start_page_token = None

    return saved_start_page_token


def get_file(drive_service, file_id):
    try:
        # Get file metadata
        file = drive_service.files().get(fileId=file_id).execute()

        # Get file media
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        # Save the file
        file_name = file.get("name")
        if not file_name:
            raise ValueError("File name is not available in file metadata.")

        with open(file_name, "wb") as f:
            f.write(fh.getvalue())
        print(f"File downloaded successfully as {file_name}.")

    except HttpError as error:
        print(f"An error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
