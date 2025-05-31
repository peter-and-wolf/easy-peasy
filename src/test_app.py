# requirements.txt
# Установи зависимости:
# pip install fastapi uvicorn google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-multipart

import os

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

# Разрешаем OAuth использовать HTTP (только для локальной разработки!)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "google-calendar-creds.json"
REDIRECT_URI = "http://localhost:8000/oauth2callback"
TOKEN_FILE = "token.json"


@app.get("/")
def root():
    return HTMLResponse("<a href='/authorize'>Авторизоваться через Google</a>")


@app.get("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return RedirectResponse(authorization_url)


@app.get("/oauth2callback")
def oauth2callback(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return HTMLResponse("<a href='/events'>Посмотреть события</a> | <a href='/create'>Создать событие</a>")


def get_service():
    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError("Нет авторизации. Перейдите по /authorize")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


@app.get("/events")
def list_events():
    service = get_service()
    events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    html = "<h2>События:</h2><ul>"
    for e in events:
        html += f"<li>{e['summary']} - {e['start'].get('dateTime', e['start'].get('date'))} <a href='/delete?id={e['id']}'>Удалить</a></li>"
    html += "</ul><a href='/'>На главную</a>"
    return HTMLResponse(html)


@app.get("/create")
def create_event():
    service = get_service()
    event = {
        'summary': 'FastAPI встреча',
        'start': {'dateTime': '2025-06-01T10:00:00+03:00', 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': '2025-06-01T11:00:00+03:00', 'timeZone': 'Europe/Moscow'},
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return RedirectResponse(url='/events')


@app.get("/delete")
def delete_event(id: str):
    service = get_service()
    service.events().delete(calendarId='primary', eventId=id).execute()
    return RedirectResponse(url='/events')


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=8000
  )