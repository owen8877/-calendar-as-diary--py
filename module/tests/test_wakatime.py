from datetime import datetime

from pytz import timezone

from common.event import EventWithId, Duration
from module.wakatime import Wakatime


def test_process():
    sample_response = ['''{"data": [{"time": 1683387268.787917, "project": "ut-page-src", "duration": 20.586596, "color": null},
{"time": 1683389664.104264, "project": "blog-src", "duration": 949.579736, "color": null},
{"time": 1683390613.684, "project": "calendar-as-diary-py", "duration": 756.487, "color": null}
],"branches": ["master"], "start": "2023-05-06T05:00:00Z", "end": "2023-05-07T04:59:59Z",
"timezone": "America/Chicago"}''']

    tz = timezone('America/Chicago')
    expected_events = [
        EventWithId(
            summary='[Wakatime] ut-page-src',
            description='[link] https://wakatime.com/projects/ut-page-src',
            duration=Duration(
                start=tz.localize(datetime(2023, 5, 6, 15, 34, 28, 787917)),
                end=tz.localize(datetime(2023, 5, 6, 15, 34, 49, 374513)),
            ),
            id='wakatime|1683387268.787917',
        ),
        EventWithId(
            summary='[Wakatime] blog-src',
            description='[link] https://wakatime.com/projects/blog-src',
            duration=Duration(
                start=tz.localize(datetime(2023, 5, 6, 16, 14, 24, 104264)),
                end=tz.localize(datetime(2023, 5, 6, 16, 30, 13, 684000)),
            ),
            id='wakatime|1683389664.104264',
        ),
        EventWithId(
            summary='[Wakatime] calendar-as-diary-py',
            description='[link] https://wakatime.com/projects/calendar-as-diary-py',
            duration=Duration(
                start=tz.localize(datetime(2023, 5, 6, 16, 30, 13, 684000)),
                end=tz.localize(datetime(2023, 5, 6, 16, 42, 50, 171000))),
            id='wakatime|1683390613.684',
        ),
    ]

    events = Wakatime().process_response_into_event_with_id(sample_response)
    assert events == expected_events
