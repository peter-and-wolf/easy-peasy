import os
import json
from typing import Any

import typer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timezone


app = typer.Typer()


SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "google-calendar-creds.json"  
CALENDAR_NAME = "Bloom"


def get_service() -> Any:
  creds = None
  if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      print("Refreshing token...")
      creds.refresh(Request())
      with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, 
        SCOPES
      )

      creds = flow.run_local_server(
        port=8080,
        access_type="offline",
        prompt="consent",
        open_browser=False  
      )

      with open(TOKEN_FILE, "w") as token:
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


@app.command()
def list_calendars():
  """Показать все доступные календари с их ID."""
  service = get_service()
  page_token = None

  while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_entry in calendar_list.get("items", []):
      summary = calendar_entry.get("summary")
      calendar_id = calendar_entry.get("id")
      typer.echo(f"{summary} — {calendar_id}")
    page_token = calendar_list.get("nextPageToken")
    if not page_token:
      break  


@app.command()
def list_events():
  """Показать ближайшие 10 событий."""
  service = get_service()
  calendar_id = get_calendar_id(service, CALENDAR_NAME)
  now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
  events_result = service.events().list(
    calendarId=calendar_id,
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy="startTime",
  ).execute()
  events = events_result.get("items", [])
  if not events:
    typer.echo("Событий не найдено.")
    return
  for event in events:
    start = event["start"].get("dateTime", event["start"].get("date"))
    typer.echo(f"{start} — {event['summary']} (ID: {event['id']})")


@app.command()
def create_event(summary: str, start: str, end: str):
  """
  Создать событие.
  Пример:
  calendar-cli create-event "Встреча" "2025-06-01T10:00:00" "2025-06-01T11:00:00"
  """
  service = get_service()
  calendar_id = get_calendar_id(service, CALENDAR_NAME)
  event = {
    "summary": summary,
    "start": {"dateTime": start, "timeZone": "Europe/Moscow"},
    "end": {"dateTime": end, "timeZone": "Europe/Moscow"},
  }
  created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
  typer.echo(f"Создано: {created_event.get('htmlLink')}")


@app.command()
def delete_event(event_id: str):
  """Удалить событие по ID."""
  service = get_service()
  try:
    calendar_id = get_calendar_id(service, CALENDAR_NAME)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    typer.echo("Событие удалено.")
  except Exception as e:
    typer.echo(f"Ошибка удаления: {e}")


if __name__ == "__main__":
  app()