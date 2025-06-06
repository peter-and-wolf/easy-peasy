from datetime import (
  datetime, 
  timezone 
)

import zcal
import gcal
from models import CalendarEvent
from config import (
  google_config, 
  zimbra_config
)


def make_index(events: list[CalendarEvent]) -> dict[str, CalendarEvent]:
  return {e.external_id: e for e in events if e.external_id is not None}


def main():
  zevents = zcal.fetch_events(
    zcal.get_calendar(
      zcal.DAVClient(
        url=str(zimbra_config.url),
        username=zimbra_config.user,
        password=zimbra_config.password
      ), 
      "Calendar"
    ), 
    from_date=datetime.now(timezone.utc)
  )

  gevents = gcal.fetch_events(
    gcal.get_service(),
    "Bloom",
    from_date=datetime.now(timezone.utc)
  )

  zindex = make_index(zevents)
  gindex = make_index(gevents)

  print(gindex)

  for event in zevents:
    if event.uid in gindex:
      print(f"Event {event.uid} already exists in Google Calendar")
    else:
      print(f"Creating event {event.uid} in Google Calendar")
      #gcal.create_event(
      #  gcal.get_service(),
      #  event,
      #  "Bloom"
      #)


if __name__ == "__main__":
  main()
  