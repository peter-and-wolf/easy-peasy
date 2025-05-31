# Calendar CLI with Google OAuth (Server-Compatible)

This is a Python command-line utility using `Typer` and Google Calendar API. It supports full OAuth 2.0 authorization via a **headless-safe local server redirect**, and allows you to:

* List calendars and their IDs
* List upcoming events
* Create a new event
* Delete an event by ID

---

## ✅ Features

* Fully functional with `InstalledAppFlow` OAuth
* Works on **remote headless servers** using `ssh -L` tunnel
* Authorization is performed via browser on your local machine

---

## 🔧 Requirements

```bash
pip install typer[all] google-auth google-auth-oauthlib google-api-python-client
```

Also make sure you have:

* `calendar_cli.py` (see `calendar_cli.py` in this repo)
* A valid `credentials.json` for a **Desktop OAuth client** from Google Cloud Console

---

## 🧭 Getting OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials:

   * Application type: **Desktop**
3. Enable **Google Calendar API**
4. Add this redirect URI:

```
http://localhost:8080
```

5. Download `credentials.json`

---

## 🚀 Running on a Remote Server

Because `run_local_server()` binds to `localhost:8080`, you need to **create a local tunnel** from your machine to the server:

### Step-by-step:

1. Connect to your server with SSH port forwarding:

```bash
ssh -L 8080:localhost:8080 user@your.server.ip
```

2. On the server, run:

```bash
python calendar_cli.py list-calendars
```

3. CLI will print an auth URL:

```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?...
```

4. Open the link in your browser on your local machine.
5. After login, Google will redirect to `http://localhost:8080/?code=...` → the server will catch the code via the tunnel.
6. You're authenticated 🎉

Token will be saved to `token.json` for reuse.

---

## 📦 CLI Usage

```bash
# List all available calendars
python calendar_cli.py list-calendars

# List upcoming events
python calendar_cli.py list-events

# Create an event
python calendar_cli.py create-event "Meeting" "2025-06-01T10:00:00" "2025-06-01T11:00:00"

# Delete an event by ID
python calendar_cli.py delete-event EVENT_ID
```

---

## 🛠 Notes

* Make sure your server allows binding to `localhost:8080`
* Always open the auth link in your **local browser** (not on the server)
* Never share your `token.json` or `credentials.json`

---

Made for remote environments. Secure and simple. ☁️
