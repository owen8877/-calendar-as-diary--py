from dataclasses import field, dataclass
from datetime import datetime, timedelta, tzinfo
from typing import List, Optional

from pytz import timezone

from common.event import EventWithId, Duration
from common.module import Module

ID = 'wakatime'


@dataclass
class Item:
    project: str = field()
    time: float = field()
    duration: float = field()
    color: str = field()

    def id(self):
        return f'{ID}|{self.time}'


@dataclass
class JsonResponse:
    start: datetime = field()
    end: datetime = field()
    timezone: str = field()
    data: List[Item] = field(default_factory=list)
    branches: List[str] = field(default_factory=list)


class Wakatime(Module):
    def __init__(self):
        super().__init__(ID)

    def get_request_url(self) -> str:
        return self.url.replace('{date}', datetime.strftime(datetime.now(), '%Y-%m-%d'))

    def need_for_detail(self, response: str) -> Optional[List[str]]:
        return None

    def process_response_into_event_with_id(self, responses: List[str], _) -> List[EventWithId]:
        json_response = self.json_parser.from_string(responses[0], JsonResponse)
        tz = timezone(json_response.timezone)

        return [EventWithId(
            summary=f'[Wakatime] {item.project}',
            description=f'[link] https://wakatime.com/projects/{item.project}',
            duration=Duration(
                start=(created_at := tz.localize(datetime.utcfromtimestamp(item.time))),
                end=created_at + timedelta(seconds=item.duration),
            ),
            id=item.id(),
        ) for item in json_response.data]
