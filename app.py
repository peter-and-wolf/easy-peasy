from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import calendar
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# Get environment variables with default values
ZIMBRA_USER = os.getenv('ZIMBRA_USER', '')
ZIMBRA_PASSWORD = os.getenv('ZIMBRA_PASSWORD', '')
ZIMBRA_URL = os.getenv('ZIMBRA_URL', '')
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 8999))

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello from easy-peasy!", "env_loaded": True}

@app.get("/v1/api/calendar")
async def get_calendar():
  if not ZIMBRA_USER or not ZIMBRA_PASSWORD or not ZIMBRA_URL:
    raise HTTPException(status_code=400, detail="Zimbra credentials or URL not configured")
    
  try:
    # Make request with basic auth
    response = requests.get(
      ZIMBRA_URL,
      auth=(ZIMBRA_USER, ZIMBRA_PASSWORD),
      verify=False  # Disable SSL verification for self-signed certificate
    )

    response.raise_for_status()  # Raise exception for bad status codes
    
    import email.utils
    return Response(
      content=response.text,
      media_type="text/calendar;charset=utf-8",
      headers={
        "Date": email.utils.formatdate(timeval=None, localtime=False, usegmt=True),
        "Cache-Control": "public, max-age=3600",
        "Content-Type": "text/calendar;charset=utf-8",
        "Content-Disposition": "attachment; filename=calendar.ics",
        "Vary": "Accept-Encoding, User-Agent",
        "Transfer-Encoding": "chunked"
      }
    )
  
  except requests.exceptions.RequestException as e:
    raise HTTPException(
      status_code=500,
      detail=f"Failed to fetch calendar data: {str(e)}"
    )

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
