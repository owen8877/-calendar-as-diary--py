from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from gcsa.event import Event


@dataclass
class Duration:
    start: datetime
    end: Optional[datetime]

    def is_start_end(self):
        return self.end is not None

    def is_whole_day(self):
        return self.end is None


@dataclass
class EventWithId:
    summary: str
    description: str
    duration: Duration
    id: str

    def to_event(self):
        return Event(
            summary=self.summary,
            start=self.duration.start,
            end=self.duration.end,
            description=self.description,
        )
