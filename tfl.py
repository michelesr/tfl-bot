from dateutil.parser import parse
import requests

BASE_URL = 'https://api.tfl.gov.uk'


def get_data(path):
    res = requests.get(BASE_URL + '/' + path)
    return res.json()


def get_modes():
    return get_data('Line/Meta/Modes')


def get_mode_names():
    return map(lambda m: m['modeName'], get_modes())


def get_lines(mode):
    return get_data('Line/Mode/{}/Route'.format(mode))


def get_all_lines():
    return map(get_lines, get_mode_names())


def get_line_status(line_id):
    return get_data('Line/{}/Status'.format(line_id))


def get_lines_status(mode):
    return map(lambda l: get_line_status(l['id']), get_lines(mode))


def format_status(status):
    status = status[0]
    messages = []
    messages.append('Status for {} ({}) last modified on {}'.format(
        status['name'], status['modeName'], format_date(status['modified'])))
    for s in status['lineStatuses']:
        messages.append(s['statusSeverityDescription'])
        if 'disruption' in s.keys():
            d = s['disruption']
            messages.append(d['description'])
            if 'additionalInfo' in d.keys():
                messages.append(d['additionalInfo'])
    return messages


def format_date(date_string):
    d = parse(date_string)
    return '{}/{}/{} at {}:{}:{}'.format(d.day, d.month, d.year, d.hour,
                                         d.minute, d.second)
