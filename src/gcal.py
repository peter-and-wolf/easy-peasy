from typing import Any
from os import path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow # type: ignore
from googleapiclient.discovery import build # type: ignore
from google.auth.transport.requests import Request # type: ignore
from datetime import datetime, timezone

from models import CalendarEvent
from config import google_config  


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_service() -> Any:
  creds = None
  if path.exists(google_config.token_file):
    creds = Credentials.from_authorized_user_file(google_config.token_file, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
      with open(google_config.token_file, "w") as token:
        token.write(creds.to_json())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        google_config.credentials_file, 
        SCOPES
      )

      creds = flow.run_local_server(
        port=8080,
        access_type="offline",
        prompt="consent",
        open_browser=False  
      )

      with open(google_config.token_file, "w") as token:
       token.write(creds.to_json())
    
  return build("calendar", "v3", credentials=creds)


def get_calendar_id(service: Any, calendar_name: str) -> str:
  page_token = None
  while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_entry in calendar_list.get("items", []):
      summary = calendar_entry.get("summary")
      calendar_id = calendar_entry.get("id")
      if summary == calendar_name:
        return calendar_id
    page_token = calendar_list.get("nextPageToken")
    if not page_token:
      break

  raise ValueError(f"Календарь с названием {calendar_name} не найден")


def fetch_events(service: Any, calendar_name: str, from_date: datetime) -> list[CalendarEvent]:
  calendar_id = get_calendar_id(service, calendar_name)
  events_result = service.events().list(
    calendarId=calendar_id,
    timeMin=from_date.isoformat().replace("+00:00", "Z"),
    showDeleted=False,
    singleEvents=False,  
    maxResults =2500,
    orderBy='updated'
  ).execute()

  events = []
  for event in events_result.get("items", []):
    if 'start' not in event or 'end' not in event:
      continue
    start = event['start'].get('dateTime') or event['start'].get('date')
    end = event['end'].get('dateTime') or event['end'].get('date')
    last_modified = event.get('updated')
    recurrence = event.get('recurrence', [])
    rrule = recurrence[0] if recurrence else ""

    events.append(
      CalendarEvent(
        uid=event['id'],
        external_id=event.get('extendedProperties', {}).get('private', {}).get('external_event_id', None),
        summary=event.get('summary', ''),
        dtstart=datetime.fromisoformat(start).astimezone(timezone.utc),
        dtend=datetime.fromisoformat(end).astimezone(timezone.utc),
        last_modified=datetime.fromisoformat(last_modified).astimezone(timezone.utc),
        description=event.get('description', ''),
        location=event.get('location', ''),
        rrule=rrule
      )
    )

  return events


def create_event(service, event: CalendarEvent, calendar_name: str) -> str:
  calendar_id = get_calendar_id(service, calendar_name)

  body = {
    'summary': event.summary,
    'description': event.description,
    'location': event.location,
    'start': {'dateTime': event.dtstart.isoformat(), 'timeZone': 'UTC'},
    'end': {'dateTime': event.dtend.isoformat(), 'timeZone': 'UTC'},
    'extendedProperties': {
      'private': {
        'external_event_id': event.uid
      }
    }
  }

  if event.is_recurring:
    body['recurrence'] = [event.rrule_str]

  created = service.events().insert(calendarId=calendar_id, body=body).execute()
  return created['id']


def main():
  service = get_service()
  events = fetch_events(service, "Bloom", datetime.now(timezone.utc))
  for event in events:  
    print(event)


if __name__ == "__main__":
  main()