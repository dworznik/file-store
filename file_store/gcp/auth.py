from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "veri-dao-4221a9621ac0.json"

# Define the required scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive",
]

# Create credentials using the service account key file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Drive API client
drive_service = build("drive", "v3", credentials=credentials)

# List files in Google Drive
results = (
    drive_service.files()
    .list(pageSize=10, fields="nextPageToken, files(id, name)")
    .execute()
)
items = results.get("files", [])

if not items:
    print("No files found.")
else:
    print("Files:")
    for item in items:
        print(f'{item["name"]} ({item["id"]})')
