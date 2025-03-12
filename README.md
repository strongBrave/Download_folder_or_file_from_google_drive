# Download Folder or File from Google Drive

This script allows you to download files or entire folders from Google Drive to your local machine. It uses the Google Drive API to authenticate, list, and download files with a retry mechanism to handle errors during the download process.

## Features:
- **Download Files**: Download individual files from Google Drive.
- **Download Folders**: Recursively download entire folders (including subfolders).
- **Retry Mechanism**: Handles download failures by retrying multiple times.

## Requirements:
- Python 3.x
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

## Installation:
1. Install required dependencies:
    ```bash
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```

2. Create a project in [Google Cloud Console](https://console.cloud.google.com/), enable the Google Drive API, and create OAuth 2.0 credentials.

3. Download the `credentials.json` file and place it in the root of this project.

## Usage:
Run the script from the command line with the following arguments:

```bash
python download_folder.py --credentials_json_path <path_to_credentials_json> --folder_id <google_drive_folder_id> --save_dir <local_directory>
```

* `--credentials_json_path`: Path to your credentials.json file (default: credentials.json).
* `--folder_id`: The ID of the folder on Google Drive to download.
* `--save_dir`: The local directory where files will be saved.

```bash
python download_file.py --credentials_json_path <path_to_credentials_json> --file_id <google_drive_folder_id> --save_dir <local_directory>
```

* `--file_id`: The ID of the file on Google Drive to download.

## Example
* Download folder
```bash
python download_folder.py --credentials_json_path credentials.json --folder_id 1a2B3cD4EfG5hIjKlMnOpQrStUvWxYz --save_dir ./downloads
```

* Download file
```bash
python download_file.py --credentials_json_path credentials.json --file_id 1a2B3cD4EfG5hIjKlMnOpQrStUvWxYz --save_dir ./downloads
```