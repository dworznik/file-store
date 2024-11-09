import argparse
import os
import json
from file_store.gcp.drive import (
    fetch_changes,
    get_credentials,
    build_drive_service,
    get_file,
    get_start_page_token,
    setup_watch,
    stop_watch,
    folder_info,
)

DATABASE_FILE = "watch_channels.jsonl"


def save_watch_response(response):
    with open(DATABASE_FILE, "a") as f:
        f.write(json.dumps(response) + "\n")


def load_watch_responses():
    responses = []
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            for line in f:
                responses.append(json.loads(line.strip()))
    return responses


def main():
    parser = argparse.ArgumentParser(description="Google Drive API CLI Tool")
    parser.add_argument(
        "--service-account-file",
        required=True,
        help="Path to the service account key file",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command to set up a watch
    parser_watch = subparsers.add_parser(
        "watch", help="Set up a watch on Google Drive changes"
    )
    parser_watch.add_argument(
        "--webhook-url", required=True, help="The webhook URL to receive notifications"
    )
    parser_watch.add_argument(
        "--folder-id", required=True, help="The ID of the folder to observe"
    )

    # Sub-command to stop a watch
    parser_stop = subparsers.add_parser(
        "stop", help="Stop a watch on Google Drive changes"
    )
    parser_stop.add_argument(
        "--channel-id", required=True, help="The channel ID of the watch"
    )

    # Sub-command to get folder info
    parser_info = subparsers.add_parser(
        "info", help="Get information about a Google Drive folder"
    )
    parser_info.add_argument(
        "--folder-id", required=True, help="The ID of the folder to get information for"
    )

    # Sub-command to get changes
    parser_changes = subparsers.add_parser(
        "changes", help="Get information about changes"
    )
    parser_changes.add_argument(
        "--token", required=False, help="Last token from getStartPageToken()"
    )

    # Sub-command to download files
    parser_download = subparsers.add_parser("download", help="Download file")
    parser_download.add_argument("--file-id", required=True, help="File id to download")

    args = parser.parse_args()

    credentials = get_credentials(args.service_account_file)
    drive_service = build_drive_service(credentials)

    if args.command == "watch":
        start_page_token = get_start_page_token(drive_service)
        watch_response = setup_watch(
            drive_service, start_page_token, args.webhook_url, args.folder_id
        )
        save_watch_response(watch_response)
        print("Watch response:", watch_response)
    elif args.command == "stop":
        responses = load_watch_responses()
        for response in responses:
            if response["id"] == args.channel_id:
                stop_response = stop_watch(
                    drive_service, response["resourceId"], response["id"]
                )
                print("Stop watch response:", stop_response)
                break
        else:
            print(f"Channel ID {args.channel_id} not found in database.")
    elif args.command == "info":
        folder_details = folder_info(drive_service, args.folder_id)
        if folder_details:
            print("Folder details:", json.dumps(folder_details, indent=2))
        else:
            print(
                "Failed to retrieve folder information. Please check the error messages above."
            )
    elif args.command == "changes":
        if args.token:
            start_page_token = args.token
        else:
            start_page_token = get_start_page_token(drive_service)

        saved_token = fetch_changes(drive_service, start_page_token)
        print("Token:", saved_token)
    elif args.command == "download":
        get_file(drive_service, args.file_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
