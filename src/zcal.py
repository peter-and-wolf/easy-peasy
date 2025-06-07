from datetime import (
  datetime, 
  timezone, 
)

from caldav import DAVClient
from caldav.objects import Calendar
from icalendar import Calendar as ICalendar
from dateutil.rrule import rrulestr

from models import CalendarEvent
from config import zimbra_config


def get_calendar(client: DAVClient, calendar_name: str) -> Calendar:
  principal = client.principal()
  for calendar in principal.calendars():
    if calendar.name == calendar_name:
      return calendar

  raise ValueError(f'Calendar named {calendar_name} not found')


def fetch_events(calendar: Calendar, from_date: datetime) -> dict[str, CalendarEvent]:
  events = {}
  for event in calendar.events():
    cal = ICalendar.from_ical(event.data)
    for e in cal.walk():
      if e.name == 'VEVENT':
        dtstart = e.decoded('DTSTART').astimezone(timezone.utc)

        rrule_txt = ''
        filter_dt = dtstart
        
        if e.get('RRULE', None):
          rrule_txt = event.vobject_instance.vevent.rrule.value
          rrule = rrulestr(rrule_txt, dtstart=dtstart)
          if (next_dt := rrule.after(from_date, inc=True)):
            filter_dt = next_dt   
        
        if filter_dt >= from_date:
          uid = str(e.get('UID'))
          dtend = e.decoded('DTEND').astimezone(timezone.utc)
          last_modified = e.decoded(
            'LAST-MODIFIED', 
            default=datetime.now(timezone.utc)
          )
          summary = str(e.get('SUMMARY', ''))
          description = str(e.get('DESCRIPTION', ''))
          location = str(e.get('LOCATION', ''))
          external_id = str(e.get('X-EXTERNAL-ID', None))

          if isinstance(dtstart, datetime) is False:
            dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=timezone.utc)
          if isinstance(dtend, datetime) is False:
            dtend = datetime.combine(dtend, datetime.min.time()).replace(tzinfo=timezone.utc)

          events[uid] = CalendarEvent(
            uid=uid,
            external_id=external_id,
            summary=summary,
            dtstart=dtstart,
            dtend=dtend,
            last_modified=last_modified,
            description=description,
            location=location,
            rrule=rrule_txt
          )

  return events


def main():
  client = DAVClient(
    url=str(zimbra_config.url),
    username=zimbra_config.user,
    password=zimbra_config.password
  )

  calendar = get_calendar(client, 'Calendar')
  events = fetch_events(calendar, datetime.now(timezone.utc))
  for key, event in sorted(events.items(), key=lambda e: e[1].dtstart):
    print(f"{key}: {event}")
    print()


if __name__ == '__main__':
  main()