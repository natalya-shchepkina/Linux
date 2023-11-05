import subprocess
from datetime import datetime


def ps_aux():
    stdout = subprocess.run("ps aux", shell=True, capture_output=True).stdout.decode().splitlines()
    stdout_headers = stdout[0].split()
    stdout_data = [stdout_row.split(None, len(stdout_headers) - 1) for stdout_row in stdout[1:]]
    return [dict(zip(stdout_headers, stdout_row)) for stdout_row in stdout_data]


def get_users(process_result: list):
    users = [row["USER"] for row in process_result]
    return users


def get_user_process(process_result: list):
    user_process = []
    users = get_users(process_result)
    for user in set(users):
        user_process.append(f"{user}:{users.count(user)}")
    return user_process


def get_sum(process_result: list, value: str):
    sum = 0
    match value:
        case "%CPU":
            for row in process_result:
                cpu = float(row["%CPU"])
                sum += cpu
            return round(sum, 1)
        case "RSS":
            for row in process_result:
                rss = int(row["RSS"])
                sum += rss
            return round(sum / 1024, 1)


def get_max_process(process_result: list, value: str):
    count = 0
    name_process = ""
    for row in process_result:
        current_value = float(row[value])
        if current_value > count:
            count = current_value
            name_process = row["COMMAND"]
    return name_process


stdout = ps_aux()
max_rss = get_max_process(stdout, 'RSS')
max_cpu = get_max_process(stdout, '%CPU')
data = [
    "Отчёт о состоянии системы: "
    f"Пользователи системы: {set(get_users(stdout))} ",
    f"Процессов запущено: {len(stdout)}",
    f"Пользовательских процессов: {get_user_process(stdout)}",
    f"Всего памяти используется: {get_sum(stdout, 'RSS')} mb",
    f"Всего CPU используется:{get_sum(stdout, '%CPU')} %",
    f"Больше всего памяти использует:{max_rss[:20]}",
    f"Больше всего CPU использует:{max_cpu[:20]}"
]

with open(f'{datetime.today().isoformat("-", "minutes")}-report.txt', 'w') as f:
    for row in data:
        f.write(row + "\n")




