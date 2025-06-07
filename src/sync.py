from datetime import (
  datetime, 
  timezone 
)

import db
import zcal
import gcal
from models import CalendarEvent, SyncEvent, EventStatus
from config import (
  google_config, 
  zimbra_config
)


def make_index(events: list[CalendarEvent]) -> dict[str, CalendarEvent]:
  return {e.external_id: e for e in events if e.external_id is not None}


def main():
  conn = db.connect()

  zimbra = zcal.get_calendar(
    zcal.DAVClient(
      url=str(zimbra_config.url),
      username=zimbra_config.user,
      password=zimbra_config.password
    ), 
    zimbra_config.calendar_name
  )

  google = gcal.get_service()

  zevents = zcal.fetch_events(
    zimbra,
    from_date=datetime.now(timezone.utc)
  )

  gevents = gcal.fetch_events(
    google,
    google_config.calendar_name,
    from_date=datetime.now(timezone.utc)
  )

  for uid, event in sorted(zevents.items(), key=lambda e: e[1].dtstart):  
    if db.get_sync_zevent(conn, uid):
      print('Event already exists in sync db')
    else:
      guid = gcal.create_event(google, event, google_config.calendar_name)
      db.save_sync_event(conn, 
        SyncEvent(
          uid=uid,
          zimbra_uid=uid,
          google_uid=guid,
          last_modified=datetime.now(timezone.utc),
          status=int(EventStatus.ACTIVE),
          hash=event.hash
        )
      )
    print(f'{uid}: {event}')
    print()
    

  #zindex = make_index(zevents)
  #gindex = make_index(gevents)

  #for event in zevents:
  #  if event.uid in gindex:
  #    print(f"Event {event.uid} already exists in Google Calendar")
  #  else:
  #    print(f"Creating event {event.uid} in Google Calendar")
      #gcal.create_event(
      #  gcal.get_service(),
      #  event,
      #  "Bloom"
      #)


if __name__ == "__main__":
  main()
  