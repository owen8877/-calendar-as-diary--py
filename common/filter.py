import logging
from datetime import timedelta, datetime
from typing import List

from common.event import EventWithId


def is_ended(event: EventWithId) -> bool:
    if 'ut_oden_seminar' in event.id:
        return True
    if event.duration.is_start_end():
        ended = (end := event.duration.end) <= datetime.now().replace(tzinfo=end.tzinfo) - timedelta(hours=1)
    else:
        ended = event.duration.start <= datetime.today() - timedelta(days=1)
    if not ended:
        logging.info(f'Event {event.summary} is filtered since it seems to be ongoing.')
    return ended


def long_enough(event: EventWithId) -> bool:
    if 'bilibili' in event.id:
        return True
    if event.duration.is_start_end():
        ended = event.duration.end - event.duration.start > timedelta(minutes=5)
    else:
        ended = True
    if not ended:
        logging.info(f'Event {event.summary} doesn\'t last long enough so it is ignored.')
    return ended


class FilterCollection:
    def __init__(self, *args):
        self.filters = args

    def apply(self, events: List[EventWithId]) -> List[EventWithId]:
        return [event for event in events if all(f(event) for f in self.filters)]
