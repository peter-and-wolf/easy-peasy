from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_service(creds_path: str, scopes: list[str]):
  creds = None
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', scopes)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
      creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
  return build('calendar', 'v3', credentials=creds)


def main() -> None:
  service = get_calendar_service('google-calendar-creds.json', SCOPES)
  print(service.events().list(calendarId='primary').execute())


if __name__ == '__main__':
  main()