import re
from dataclasses import field, dataclass
from datetime import datetime, timedelta
from re import Pattern
from typing import List, Optional

from bs4 import BeautifulSoup, Tag, PageElement
from pytz import timezone

from common import GlobalConfig
from common.event import EventWithId, Duration
from common.module import Module

ID = 'league_of_graphs'


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


def parse_single_game(t: PageElement, timestamp_re: Pattern, match_re: Pattern, duration_re: Pattern,
                      tz: timezone) -> EventWithId:
    script_node = t.find_next('td').find_next('td').find_next('script')
    comp_node = script_node.find_next('td')
    mode_node = comp_node.find('div').find_next('div')
    duration_node = mode_node.find_next('div').find_next('div')

    script_content = script_node.text
    mode_content = mode_node.text.strip()
    duration_content = duration_node.text

    start_timestamp, = re.search(timestamp_re, script_content).groups()
    match_id, = re.search(match_re, script_content).groups()
    minute, second = re.search(duration_re, duration_content).groups()

    return EventWithId(
        summary=f'[League of Legends] {mode_content}',
        id=(id := f'{ID}|{match_id}'),
        description=f'[link] https://www.leagueofgraphs.com/match/na/{match_id}\n[mode] {mode_content}\n[hash] {id}',
        duration=Duration(
            start=(start := datetime.fromtimestamp(int(start_timestamp) // 1000, tz)),
            end=start + timedelta(minutes=int(minute), seconds=int(second)),
        ),
    )


class LeagueOfGraphs(Module):
    def __init__(self):
        super().__init__(ID)

        self.timestamp_re = re.compile(r'new Date\((\d+)')
        self.match_re = re.compile(r'match-(\d+)')
        self.duration_re = re.compile(r'(\d+)min (\d+)s')

    def need_for_detail(self, response: str) -> Optional[List[str]]:
        return None

    def process_response_into_event_with_id(self, responses: List[str], global_config: GlobalConfig) -> List[
        EventWithId]:
        soup = BeautifulSoup(responses[0], 'lxml')

        return [parse_single_game(t, self.timestamp_re, self.match_re, self.duration_re, global_config.timezone) for t
                in
                filter(lambda x: isinstance(x, Tag) and len(x['class']) == 0, soup.find('table').children)]
