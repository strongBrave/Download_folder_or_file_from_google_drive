import os
import argparse

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError


def setup(credentials_json_path: str):
    # Define the scope for Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']

    if os.path.exists(credentials_json_path):
        # Authenticate and create the Google Drive service
        flow = InstalledAppFlow.from_client_secrets_file(credentials_json_path, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        service = build('drive', 'v3', credentials=creds)
    else:
        raise FileNotFoundError(f"Credentials file not found: {credentials_json_path}")
    return service

def list_files_in_folder(folder_id, service):
    """List all files in a specific folder."""
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType, size)").execute()
    return results.get('files', [])

def download_file(service, file_id, file_path, file_size=None, max_retries=10):
    """Download a file with retry mechanism."""
    retries = 0
    while retries < max_retries:
        try:
            # If the file already exists, delete it
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted existing file: {file_path}")

            # Get the download request
            request = service.files().get_media(fileId=file_id)

            # Download the file
            with open(file_path, 'wb') as fh:  # Use 'wb' mode to overwrite the file
                downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024 * 50)  # 50MB per chunk
                done = False

                while not done:
                    try:
                        status, done = downloader.next_chunk()
                        if status:
                            downloaded = status.resumable_progress
                            total_size = status.total_size
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading {file_path}... {progress:.1f}%", end='', flush=True)
                    except Exception as e:
                        print(f"Error: {e}")
                        raise e  # Raise error to trigger retry logic

            print(f"Download complete: {file_path}")
            return  # Return after successful download

        except Exception as e:
            retries += 1
            print(f"Download error: {e}. Retrying ({retries}/{max_retries})...")
            # Wait for a while before retrying (optional)
            import time
            time.sleep(2)

    print(f"Failed to download file: {file_path}. Tried {max_retries} times.")

def download_folder(service, folder_id, save_dir):
    """Download all files and subfolders from a Google Drive folder."""
    os.makedirs(save_dir, exist_ok=True)
    files = list_files_in_folder(folder_id, service)
    for file in files:
        save_file_path = os.path.join(save_dir, file['name'])
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            download_folder(service, file['id'], save_file_path)
        else:
            file_size = int(file.get('size', 0)) if 'size' in file else None
            download_file(service, file['id'], save_file_path, file_size)

def main():
    """Main function to parse arguments and start the download process."""
    parser = argparse.ArgumentParser(description='Download a folder from Google Drive.')
    parser.add_argument('--credentials_json_path', default='credentials.json', help='The credentials json path for authentication for download from Google Drive')
    parser.add_argument('--folder_id', required=True, help='The ID of the Google Drive folder to download.')
    parser.add_argument('--save_dir', required=True, help='The local directory to save the downloaded files.')
    args = parser.parse_args()

    # set up
    service = setup(args.credentials_json_path)

    # Start downloading the folder
    download_folder(service, args.folder_id, args.save_dir)

if __name__ == '__main__':
    main()