from common.module import read_dumped_event_id, load_request_config


def test_read_dumped_event_id():
    ids = read_dumped_event_id('template')

    assert len(ids) == 2
    assert ids == {1356, 'a5t1'}


def test_load_config():
    url, calendar_id, headers = load_request_config('template')

    assert url == 'https://wakatime.com/api/v1/users/current/durations?date={date}'
    assert calendar_id == '@group.calendar.google.com'
    assert headers, {'authorization': 'Basic [base64]'}
