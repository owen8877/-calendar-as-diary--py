import logging

import pytest
from gcsa.calendar import Calendar

from common import init_calendar, load_global_config
from main import main, fetch_data, make_detail, filter_events_to_be_posted
from module.league_of_graphs import LeagueOfGraphs
from module.wakatime import Wakatime


def test_main():
    main(countdown=3, interval=0.5)  # Expecting four loops


@pytest.mark.local
def test_refresh_token():
    init_calendar()


@pytest.mark.local
def test_integration():
    global_config = load_global_config()
    gc = init_calendar(test=True)
    test_calendar_name = 'Test purpose only'

    # First clear any calendar of the same name
    calendars = list(gc.get_calendar_list())
    if len(calendars) == 0:
        logging.debug('No calendars!')
    for calendar in calendars:
        if calendar.summary == test_calendar_name:
            gc.delete_calendar(calendar.calendar_id)
    logging.debug('Test calendar(s) has been deleted!')

    # Then add our new test calendar
    test_calendar = gc.add_calendar(Calendar(test_calendar_name))
    test_calendar_id = test_calendar.calendar_id
    print(f'The test calendar is {test_calendar_id}. Please visit https://calendar.google.com/calendar/r.')

    module = LeagueOfGraphs()
    # module = Wakatime()
    module.calendar_id = test_calendar_id

    response = fetch_data(module)
    # print(response)

    detail_response = make_detail(module, response)
    # print(detail_response)

    events = filter_events_to_be_posted(module, detail_response, global_config)
    # print(events)

    for event in events:
        gc.add_event(event.to_event(), calendar_id=test_calendar_id)
