from datetime import datetime
from zoneinfo import ZoneInfo

from pytz import timezone

from common import load_global_config
from common.event import EventWithId, Duration
from main import fetch_data, make_detail
from module.wakatime import Wakatime


def test_process():
    global_config = load_global_config()
    sample_response = ['''{"data": [{"time": 1683387268.787917, "project": "ut-page-src", "duration": 20.586596, "color": null},
{"time": 1683389664.104264, "project": "blog-src", "duration": 949.579736, "color": null},
{"time": 1683390613.684, "project": "calendar-as-diary-py", "duration": 756.487, "color": null}
],"branches": ["master"], "start": "2023-05-06T05:00:00Z", "end": "2023-05-07T04:59:59Z",
"timezone": "America/Chicago"}''']

    tz = ZoneInfo('America/Chicago')
    expected_events = [
        EventWithId(
            summary='[Wakatime] ut-page-src',
            description='[link] https://wakatime.com/projects/ut-page-src',
            duration=Duration(
                start=datetime(2023, 5, 6, 10, 34, 28, 787917).replace(tzinfo=tz),
                end=datetime(2023, 5, 6, 10, 34, 49, 374513).replace(tzinfo=tz),
            ),
            id='wakatime|1683387268.787917',
        ),
        EventWithId(
            summary='[Wakatime] blog-src',
            description='[link] https://wakatime.com/projects/blog-src',
            duration=Duration(
                start=datetime(2023, 5, 6, 11, 14, 24, 104264).replace(tzinfo=tz),
                end=datetime(2023, 5, 6, 11, 30, 13, 684000).replace(tzinfo=tz),
            ),
            id='wakatime|1683389664.104264',
        ),
        EventWithId(
            summary='[Wakatime] calendar-as-diary-py',
            description='[link] https://wakatime.com/projects/calendar-as-diary-py',
            duration=Duration(
                start=datetime(2023, 5, 6, 11, 30, 13, 684000).replace(tzinfo=tz),
                end=datetime(2023, 5, 6, 11, 42, 50, 171000).replace(tzinfo=tz),
            ),
            id='wakatime|1683390613.684',
        ),
    ]

    events = Wakatime().process_response_into_event_with_id(sample_response, global_config)
    assert events == expected_events


def test_fetch():
    module = Wakatime()
    response = fetch_data(module)
    print('\n')
    print(response)


def test_fetch_and_process():
    global_config = load_global_config()
    module = Wakatime()
    response = fetch_data(module)
    detail_response = make_detail(module, response)
    events = module.process_response_into_event_with_id(detail_response, global_config)
    print('\n')
    print(events)
