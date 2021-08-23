import os.path
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = "https://www.googleapis.com/auth/photoslibrary"
token_json = "token.json"
credentials_json = "credentials.json"


def download_photo(url: str, destination_folder: str, file_name: str):
    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading file {0}'.format(
            os.path.join(destination_folder, file_name)))
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()


def main():

    valid = False
    while not valid:
        print("指定輸出資料夾路徑")
        output = input(">> ")
        if os.path.exists(output):
            break
        print("請指定存在的路徑")

    creds = False
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_json):
        creds = Credentials.from_authorized_user_file(token_json, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_json, 'w') as token:
            token.write(creds.to_json())

    with build('photoslibrary', 'v1', credentials=creds, static_discovery=False) as gphoto_service:

        # gphoto_service = build('photoslibrary', 'v1',
        #    credentials=creds, static_discovery=False)

        # 取得所有的照片
        nextPageToken = None
        while True:

            try:  # 每次取 1 page 25張
                page_photos = gphoto_service.mediaItems().list(
                    pageSize=25, pageToken=nextPageToken).execute()
                nextPageToken = page_photos['nextPageToken']
                page_photos = page_photos['mediaItems']

                for photo in page_photos:
                    filename = photo['filename']
                    download_url = photo['baseUrl'] + '=d'
                    download_photo(download_url, output, filename)

            except:   # I don't know what type of error may occur
                # gphoto_service.close()
                break


if __name__ == '__main__':
    main()
