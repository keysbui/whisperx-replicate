from __future__ import unicode_literals
import re
import io
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')


def extract_file_id(drive_url):
    """
    Extracts the file ID from a Google Drive URL.

    Args:
        drive_url (str): The Google Drive URL.

    Returns:
        str: The extracted file ID.
    """
    # Regular expression to match the file ID in the URL
    match = re.search(r'(?:/d/|id=)([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive URL")


def fetch_audio(url):
    file_id = extract_file_id(url)

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    file_metadata = service.files().get(fileId=file_id, fields='name,webContentLink').execute()
    file_name = file_metadata.get('name')
    print(f"Downloading file: {file_name}")
    print(file_metadata)

    request = service.files().get_media(fileId=file_id)
    drive_file = io.BytesIO()
    downloader = MediaIoBaseDownload(drive_file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}.")
    
    file_path = 'tmp/'+file_name
    with open(file_path, 'wb') as file:
        file.write(drive_file.getvalue())
    
    return file_path, file_name