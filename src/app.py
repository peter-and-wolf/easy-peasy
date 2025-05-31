from datetime import datetime

from fastapi import FastAPI, HTTPException, Response
import aiohttp # type: ignore
from config import settings
#from authlib.integrations.starlette_client import AsyncOAuthClient

app = FastAPI()


@app.get("/")
async def root() -> dict:
  return {"message": "Hello from easy-peasy!", "env_loaded": True}


@app.get("/v1/api/calendar")
async def get_calendar() -> Response:
  if not settings.zimbra_user or not settings.zimbra_password or not settings.zimbra_url:
    raise HTTPException(status_code=400, detail="Zimbra credentials or URL not configured")
    
  try:
    # Make async request with basic auth
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(settings.zimbra_user, settings.zimbra_password)) as session:
        async with session.get(str(settings.zimbra_url)) as response:
            response.raise_for_status()  # Raise exception for bad status codes
            content = await response.text()
            
    return Response(
      content=content,
      media_type="text/calendar;charset=utf-8",
      headers={
        "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Cache-Control": "public, max-age=3600",
        "Content-Type": "text/calendar;charset=utf-8",
        "Content-Disposition": "attachment; filename=calendar.ics",
        "Vary": "Accept-Encoding, User-Agent",
        "Transfer-Encoding": "chunked"
      }
    )
  
  except aiohttp.ClientError as e:
    raise HTTPException(
      status_code=500,
      detail=f"Failed to fetch calendar data: {str(e)}"
    )


if __name__ == "__main__":
  #import uvicorn
  #uvicorn.run(
  #  app, 
  #  host=settings.server_host, 
  #  port=settings.server_port
  #)
  print("Hello from easy-peasy!")
