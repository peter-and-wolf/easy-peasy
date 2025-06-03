import sqlite3
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from caldav import DAVClient
from uritemplate import expand

from config import (
  calwatch_config, 
  zimbra_config, 
  google_config
)


@dataclass
class CalendarEvent:
    uid: str
    summary: str
    dtstart: str
    dtend: str
    hash: str


def init_db() -> sqlite3.Connection:
  conn = sqlite3.connect(calwatch_config.db_file)
  c = conn.cursor()
  c.execute("""
      CREATE TABLE IF NOT EXISTS events (
        uid TEXT PRIMARY KEY,
        summary TEXT,
        dtstart TEXT,
        dtend TEXT,
        hash TEXT
      )
  """)
  c.execute("""
    CREATE TABLE IF NOT EXISTS changes (
      timestamp TEXT,
      change_type TEXT,
      uid TEXT,
      summary TEXT,
      dtstart TEXT,
      dtend TEXT
    )
  """)
  conn.commit()
  return conn


def hash_event(summary, dtstart, dtend):
  combined = f'{summary}|{dtstart}|{dtend}'
  return hashlib.md5(combined.encode('utf-8')).hexdigest()


def fetch_calendar_events(client):
  now = datetime.now(timezone.utc)
  principal = client.principal()
  events = []
  for calendar in principal.calendars():
    for event in calendar.events():
      try:
        vevent = event.vobject_instance.vevent
        uid = vevent.uid.value
        summary = vevent.summary.value
        dtstart = vevent.dtstart.value
        dtend = vevent.dtend.value
        rrule_field = vevent.rrule.value
        
        if rrule_field:
          print(dtstart)
          print(type(rrule_field))

        hash_value = hash_event(summary, dtstart, dtend)
        
        events.append(
          CalendarEvent(
            uid=uid, 
            summary=summary, 
            dtstart=dtstart, 
            dtend=dtend, 
            hash=hash_value
          )
        )
      except Exception:
        continue
  return events


def load_previous_events(conn: sqlite3.Connection) -> dict[str, CalendarEvent]:
  c = conn.cursor()
  c.execute("SELECT uid, summary, dtstart, dtend, hash FROM events")
  rows = c.fetchall()
  return {
    row[0]: CalendarEvent(row[0], row[1], row[2], row[3], row[4]) for row in rows
  }


def save_current_events(conn: sqlite3.Connection, events: list[CalendarEvent]):
  c = conn.cursor()
  c.execute("DELETE FROM events")
  for e in events:
    c.execute(
      "INSERT INTO events (uid, summary, dtstart, dtend, hash) VALUES (?, ?, ?, ?, ?)",
      (e.uid, e.summary, e.dtstart, e.dtend, e.hash)
    )
  conn.commit()


def diff_events(
  previous_events: dict[str, CalendarEvent],
  current_events: list[CalendarEvent]
)  -> None:

  previous_uids = set(previous_events.keys())
  current_uids = set(e.uid for e in current_events)
  current_map = {e.uid: e for e in current_events}

  added = current_uids - previous_uids
  removed = previous_uids - current_uids
  potentially_modified = previous_uids & current_uids

  for uid in added:
    #record_change('added', current_map[uid])
    print(f"🟢 Добавлено: {current_map[uid].dtstart} — {current_map[uid].summary}")

  for uid in removed:
    #record_change('removed', old_events[uid])
    print(f"🔴 Удалено: {previous_events[uid].dtstart} — {previous_events[uid].summary}")

  for uid in potentially_modified:
    if previous_events[uid].hash != current_map[uid].hash:
      #record_change('modified', new_map[uid])
      print(f"🟡 Изменено: {current_map[uid].dtstart} — {current_map[uid].summary}")



def main():
  conn = init_db()

  client = DAVClient(
    url=str(zimbra_config.url),
    username=zimbra_config.user,
    password=zimbra_config.password
  )

  print("fetching calendar events...")
  events = fetch_calendar_events(client)

  #for e in sorted(events, key=lambda e: e.dtstart):
  #  print(f"{e.dtstart} — {e.summary}")

  #print("loading previous events...") 
  #previous_events = load_previous_events(conn)
  #print("saving current events...")
  #save_current_events(conn, events)
  #print("diffing events...")
  #diff_events(previous_events, events)


if __name__ == "__main__":
  main()