import argparse
import json
import re
import subprocess
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--dir_name", default='/var/log')
parser.add_argument("--file_name", default='*.log')
args = parser.parse_args()


def get_log_files():
    dir_name = args.dir_name
    file_name = args.file_name
    return subprocess.run(f"find {dir_name} -name {file_name} ",
                                shell=True, capture_output=True).stdout.decode().split()


def parse_log_files(files):
    print(f'Start parsing files: {files}')
    result = []
    for file in files:
        with open(file, 'r') as f:
            regex = (r'^(?P<remote_host>[\d\.]*).*'
                     r'\[(?P<request_time>.*)\]\s'
                     r'\"(?P<request_method>\S*)\s'
                     r'(?P<request_url>\S*)\s'
                     r'(?P<request_version>.*)\"\s'
                     r'(?P<http_code>\d{,3})\s'
                     r'(?P<bytes>\S*)\s'
                     r'\"(?P<referer>.*)\"\s'
                     r'\"(?P<user_agent>.*)\"\s'
                     r'(?P<request_duration>\d*)$')
            for row in f:
                try:
                    pars_line = re.search(regex, row)
                    result.append({
                        'remote_host': pars_line.group('remote_host'),
                        'request_time': pars_line.group('request_time'),
                        'request_method': pars_line.group('request_method'),
                        'request_url': pars_line.group('request_url'),
                        'request_version': pars_line.group('request_version'),
                        'http_code': pars_line.group('http_code'),
                        'bytes': pars_line.group('bytes'),
                        'referer': pars_line.group('referer'),
                        'user_agent': pars_line.group('user_agent'),
                        'request_duration': pars_line.group('request_duration')
                    })
                except AttributeError:
                    print(f'Сould not parse this log:\n {row}')
    print(f'Finished parsing files')
    return result


def get_count(logs, value: str):
    list_value = [i[value] for i in logs]
    result = {}
    for i in list_value:
        if i not in result:
            result.update(({i: list_value.count(i)}))
    return sorted(result.items(), key=lambda item: item[1], reverse=True)


def get_longest_request(logs):
    result = sorted(logs, key=lambda x: int(x['request_duration']), reverse=True)
    return result[:3]


logs = parse_log_files(get_log_files())
data = {
    'Counts of completed requests': len(logs),
    'Counts by methods': get_count(logs, 'request_method'),
    'Top of IP': get_count(logs, 'request_url')[:3],
    'Top of longest request': [
        {
            'method': item["request_method"],
            'url': item["request_url"],
            'ip': item["remote_host"],
            'duration': item["request_duration"],
            'date and time': item["request_time"]
        } for item in get_longest_request(logs)
    ]
}
pprint(data)

with open('report.json', 'w') as f:
    json_data = json.dumps(data, indent=4)
    f.write(json_data)
