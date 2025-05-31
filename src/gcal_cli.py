import os
import json

import typer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime

from test_app import REDIRECT_URI

app = typer.Typer()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "google-calendar-creds.json"  # скачай с Google Cloud Console
REDIRECT_URI="http://localhost:8000/oauth"

def get_service():
  creds = None
  if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, 
        SCOPES
    )
      creds = flow.run_local_server(
        port=8000,
        redirect_uri_trailing_slash=False,
        access_type="offline",
        prompt="consent"
      )
    with open(TOKEN_FILE, "w") as token:
      token.write(creds.to_json())
  return build("calendar", "v3", credentials=creds)

@app.command()
def list_events():
  """Показать ближайшие 10 событий."""
  service = get_service()
  now = datetime.utcnow().isoformat() + "Z"
  events_result = service.events().list(
    calendarId="primary",
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
  event = {
    "summary": summary,
    "start": {"dateTime": start, "timeZone": "Europe/Moscow"},
    "end": {"dateTime": end, "timeZone": "Europe/Moscow"},
  }
  created_event = service.events().insert(calendarId="primary", body=event).execute()
  typer.echo(f"Создано: {created_event.get('htmlLink')}")

@app.command()
def delete_event(event_id: str):
  """Удалить событие по ID."""
  service = get_service()
  try:
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    typer.echo("Событие удалено.")
  except Exception as e:
    typer.echo(f"Ошибка удаления: {e}")

if __name__ == "__main__":
  app()