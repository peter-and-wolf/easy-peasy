from hashlib import md5
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalendarEvent:
  uid: str
  external_id: str | None
  summary: str
  dtstart: datetime
  dtend: datetime
  last_modified: datetime
  description: str = ""
  location: str = ""          
  rrule: str = ""

  @property
  def hash(self) -> str:
    raw = f"{self.summary}|{self.dtstart.isoformat()}|{self.dtend.isoformat()}|{self.description}|{self.location}|{self.rrule}"
    return md5(raw.encode('utf-8')).hexdigest()

  @property
  def is_recurring(self) -> bool:
    return self.rrule is not None and self.rrule != ""

  @property
  def rrule_str(self) -> str:
    if not self.rrule.startswith("RRULE:"):
      return "RRULE:" + self.rrule
    return self.rrule
    
  