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

def main():
    """Main function to parse arguments and start the download process."""
    parser = argparse.ArgumentParser(description='Download a folder from Google Drive.')
    parser.add_argument('--credentials_json_path', default='credentials.json', help='The credentials json path for authentication for download from Google Drive')
    parser.add_argument('--file_id', required=True, help='The ID of the Google Drive file to download.')
    parser.add_argument('--save_dir', required=True, help='The local directory to save the downloaded files.')
    args = parser.parse_args()

    # set up
    service = setup(args.credentials_json_path)

    file = service.files().get(fileId=args.file_id).execute()
    file_name = file.get('name')
    file_path = os.path.join(args.save_dir, file_name)

    # Start downloading the folder
    download_file(service, args.file_id, file_path)

if __name__ == '__main__':
    main()