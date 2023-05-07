import logging
import sched
import time
from datetime import datetime, timedelta
from typing import List, Iterable, Optional

import requests
from gcsa.google_calendar import GoogleCalendar

from common import init_calendar, load_global_config, GlobalConfig
from common.event import EventWithId
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


def filter_events_to_be_posted(module: Module, detail_response: List[str], global_config: GlobalConfig) -> List[
    EventWithId]:
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

    def not_duplicated(event: EventWithId) -> bool:
        if (id := event.id) in (events_ids := module.event_ids):
            logging.info(f'Event with id {id} already exists; skipped.')
            return False
        events_ids.add(id)
        logging.info(f'Event with id {id} shows for the first time; inserted.')
        return True

    return [event for event in module.process_response_into_event_with_id(detail_response, global_config)
            if is_ended(event) and long_enough(event) and not_duplicated(event)]


def heavy_lifting(modules: Iterable[Module], gc: GoogleCalendar, global_config: GlobalConfig):
    logging.debug(f'Doing heavy lifting jobs at {datetime.now()}...')

    for module in modules:
        response = fetch_data(module)
        detail_response = make_detail(module, response)
        events = filter_events_to_be_posted(module, detail_response, global_config)
        for event in events:
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

    # Set-up scheduler
    s = sched.scheduler(time.monotonic, time.sleep)

    def loop(countdown: int):
        if countdown < 0:  # make way for unittest
            heavy_lifting(modules, gc, global_config)
        if countdown == 0:  # No more loops!
            return
        else:
            s.enter(global_config.update_interval if interval is None else interval, 0, loop,
                    argument=(countdown if countdown < 0 else countdown - 1,))

    loop(countdown)
    s.run()


if __name__ == '__main__':
    main()
