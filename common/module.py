import logging
from typing import Set, Tuple, Dict, Optional, List

import yaml
from xsdata.formats.dataclass.parsers import JsonParser
from yaml import Loader

from common import get_json_parser, GlobalConfig, ensure_dir
from common.event import EventWithId


def read_dumped_event_id(id: str) -> Set[str]:
    try:
        with open(f'dump/{id}.yml', 'r') as f:
            content = yaml.load(f, Loader)
        logging.debug(f'Dumped id found! ({len(content)} entries)')
        return set(content)
    except FileNotFoundError:
        logging.debug('Dumped id not found, return an empty set instead.')
        return set()


def load_request_config(id: str) -> Tuple[str, str, Dict[str, str]]:
    with open(f'config/{id}.yml', 'r') as f:
        yconfig = yaml.load(f, Loader)
    return yconfig['url'], yconfig['calendar_id'], yconfig['headers']


class Module:
    def __init__(self, id: str, json_parser: Optional[JsonParser] = None):
        self.id = id
        self.url, self.calendar_id, self.headers = load_request_config(self.id)
        self.event_ids = read_dumped_event_id(self.id)
        self.json_parser = get_json_parser() if json_parser is None else json_parser

    def get_request_url(self) -> str:
        return self.url

    def need_for_detail(self, response: str) -> Optional[List[str]]:
        raise NotImplemented

    def process_response_into_event_with_id(self, responses: List[str], global_config: GlobalConfig) -> List[
        EventWithId]:
        raise NotImplemented

    def dump(self):
        ensure_dir('dump')
        with open(f'dump/{self.id}.yml', 'w') as f:
            f.write(yaml.dump(self.event_ids))
