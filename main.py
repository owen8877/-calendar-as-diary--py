import logging
import sched
import time
from datetime import datetime
from typing import List, Iterable, Optional

import requests
from gcsa.google_calendar import GoogleCalendar

from common import init_calendar, load_global_config, GlobalConfig
from common.event import EventWithId
from common.filter import FilterCollection, is_ended, long_enough
from common.module import Module
from module.league_of_graphs import LeagueOfGraphs
from module.wakatime import Wakatime


def fetch_data(module: Module) -> str:
    response = requests.get(module.get_request_url(), headers=module.headers)
    logging.debug(f'Fetched {response.status_code} for module {module.id}')
    return response.text


def make_detail(module: Module, response: str) -> List[str]:
    if further_request_urls := module.need_for_detail(response) is not None:
        responses = []
        for url in further_request_urls:
            r = requests.get(url, headers=module.headers)
            logging.debug(f'Fetched further {r.status_code} for module {module.id}')
            responses.append(r.text)
        return responses
    else:
        return [response]


def deduplicate(module: Module, events: List[EventWithId]) -> List[EventWithId]:
    events_filtered = []
    for event in events:
        if (id := event.id) in (events_ids := module.event_ids):
            logging.info(f'Event with id {id} already exists; skipped.')
        else:
            events_ids.add(id)
            logging.info(f'Event with id {id} shows for the first time; inserted.')
            events_filtered.append(event)
    return events_filtered


def heavy_lifting(modules: Iterable[Module], gc: GoogleCalendar, filters: FilterCollection,
                  global_config: GlobalConfig):
    logging.debug(f'Doing heavy lifting jobs at {datetime.now()}...')

    for module in modules:
        response = fetch_data(module)
        detail_response = make_detail(module, response)
        events = module.process_response_into_event_with_id(detail_response, global_config)
        new_events = deduplicate(module, filters.apply(events))
        for event in new_events:
            gc.add_event(event.to_event(), calendar_id=module.calendar_id)
        module.dump()

    logging.debug(f'Work done at {datetime.now()}, waiting to be picked up...')


def main(countdown: int = -1, interval: Optional[float] = None):
    """
    The main entrance of the entire program.

    :param countdown: used for testing purpose, set to -1 by default
    :param interval: in the unit of seconds
    """

    # Set-up logger
    logging.basicConfig(level=logging.DEBUG)

    # Loading modules and calendar(s)
    modules = [
        Wakatime(),
        LeagueOfGraphs(),
    ]
    gc = init_calendar()
    global_config = load_global_config()
    filters = FilterCollection(is_ended, long_enough)

    # Set-up scheduler
    s = sched.scheduler(time.monotonic, time.sleep)

    def loop(countdown: int):
        if countdown < 0:  # make way for unittest
            heavy_lifting(modules, gc, filters, global_config)
        if countdown == 0:  # No more loops!
            return
        else:
            s.enter(global_config.update_interval if interval is None else interval, 0, loop,
                    argument=(countdown if countdown < 0 else countdown - 1,))

    loop(countdown)
    s.run()


if __name__ == '__main__':
    main()
