from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

import pytz
import yaml
from gcsa.google_calendar import GoogleCalendar
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import JsonParser
from yaml import Loader


def get_json_parser() -> JsonParser:
    context = XmlContext()
    parser = JsonParser(context=context)
    return parser


def init_calendar(test: bool = False) -> GoogleCalendar:
    return GoogleCalendar(credentials_path='config/client_secret.json',
                          token_path='config/' + ('test' if test else '') + 'token.pickle',
                          authentication_flow_port=14789)


@dataclass
class GlobalConfig:
    update_interval = 3600
    timezone = pytz.timezone('UTC')


def load_global_config() -> GlobalConfig:
    with open(f'global_config.yml', 'r') as f:
        econfig = yaml.load(f, Loader)
    gconfig = GlobalConfig()
    for k, v in econfig.items():
        if k == 'timezone':
            v = ZoneInfo(v)
        gconfig.__setattr__(k, v)
    return gconfig


def ensure_dir(dir: str):
    Path(dir).mkdir(exist_ok=True)
