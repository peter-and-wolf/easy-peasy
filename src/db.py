import sqlite3

from config import sync_config
from models import (
  SyncEvent,
  EventStatus
)


def connect() -> sqlite3.Connection:
  conn = sqlite3.connect(sync_config.db_file)
  c = conn.cursor()
  c.execute("""
    CREATE TABLE IF NOT EXISTS event_map (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      zimbra_uid TEXT NOT NULL,
      google_uid TEXT NOT NULL,
      last_modified TEXT NOT NULL,
      status INTEGER NOT NULL,
      hash TEXT NOT NULL
    )
  """)
  c.execute("""
    CREATE INDEX IF NOT EXISTS idx_event_map_zimbra_uid ON event_map (zimbra_uid);
  """)
  c.execute("""
    CREATE INDEX IF NOT EXISTS idx_event_map_google_uid ON event_map (google_uid);
  """)
  conn.commit()
  return conn


def disconnect(conn: sqlite3.Connection):
  conn.close()


def _get_sync_event(conn: sqlite3.Connection, target: str, value: str) -> SyncEvent | None:
  c = conn.cursor()
  c.execute(f"SELECT * FROM event_map WHERE {target} = ?", (value,))
  row = c.fetchone()
  if row:
    return SyncEvent(
      uid=row[0],
      zimbra_uid=row[1],
      google_uid=row[2],
      last_modified=row[3],
      status=EventStatus(row[4]),
      hash=row[5]
    )
  return None


def get_sync_zevent(conn: sqlite3.Connection, zimbra_uid: str) -> SyncEvent | None:
  return _get_sync_event(conn, "zimbra_uid", zimbra_uid)


def get_sync_gevent(conn: sqlite3.Connection, google_uid: str) -> SyncEvent | None:
  return _get_sync_event(conn, "google_uid", google_uid)
  

def save_sync_event(conn: sqlite3.Connection, event: SyncEvent):
  c = conn.cursor()
  c.execute("""
    INSERT INTO event_map (zimbra_uid, google_uid, last_modified, status, hash)
    VALUES (?, ?, ?, ?, ?)
  """, (event.zimbra_uid, event.google_uid, event.last_modified, event.status, event.hash))
  conn.commit()