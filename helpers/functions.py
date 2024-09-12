import os
import random
import time
import math
import requests
from termcolor import cprint
from tqdm import tqdm
from datetime import datetime
from loguru import logger

from config.settings import MAX_GWEI, MIN_BALANCE, USE_PROXY
from helpers.cli import get_amount_in_range
from helpers.settings_helper import get_random_proxy
MAX_RETRIES=1

def sleeping(from_sleep: object, to_sleep: object) -> object:
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)


# 2023-08-15 22:36 format
def wait_schedule(scheduled_time, interval_time=30):
    while True:
        scheduled_datetime = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
        current_datetime = datetime.now()
        logger.info(f'Current timestamp: {current_datetime} | Scheduled: {scheduled_datetime}')

        if current_datetime >= scheduled_datetime:
            break

        time.sleep(interval_time)


def round_to(num, digits=3):
    try:
        if num == 0:
            return 0

        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits:
            scale = digits
        return round(num, scale)
    except:
        return num


def int_to_wei(qty, decimal):
    # return int(Web3.to_wei(qty, CURRENCY_MAP[decimal]))
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def wei_to_int(qty, decimal):
    # return float(Web3.from_wei(qty, CURRENCY_MAP[decimal]))
    return qty / int("".join((["1"] + ["0"] * decimal)))


def func_chunks_generators(keys, n):
    return [keys[i:i + n] for i in range(0, len(keys), n)]


def get_min_balance(network):
    return get_amount_in_range(str(MIN_BALANCE[network]))


def api_call(url, params=None, headers=None,retry=0):
    proxies = []
    verify=True

    if USE_PROXY:
        proxies = get_random_proxy()
        ssl_path = 'config/ca.crt'
        if os.path.isfile(ssl_path):
            verify = ssl_path

    try:
        response = requests.get(url, params=params, headers=headers, proxies=proxies,verify=verify)

        if response.status_code == 200:
            api_data = response.json()
            return api_data
        else:
                error_text = response.json()
                if error_text:
                    if error_text.get('description'):
                        cprint(error_text['description'], 'red')
                    else:
                        cprint(error_text, 'red')

    except Exception as error:
        if retry < MAX_RETRIES:
            cprint(f'Request Error: {error}, retry...', 'red')
            time.sleep(3)
            return api_call(url, params, headers, retry + 1)



def post_call(url, params=None, headers=None):
    proxies = []
    verify = True

    if USE_PROXY:
        proxies = get_random_proxy()
        ssl_path = 'config/ca.crt'
        if os.path.isfile(ssl_path):
            verify = ssl_path



    try:
        response = requests.post(url, json=params, headers=headers, proxies=proxies,verify=verify)

        if response.status_code == 200:
            api_data = response.json()
            return api_data
        else:
            error_text = response.json()
            if error_text and error_text.get('description'):
                cprint(error_text['description'], 'red')
            if error_text and error_text.get('message'):
                cprint(error_text['message'], 'red')

            cprint(f'Error: status code {response.status_code}, retry...', 'red')
            time.sleep(3)
            return post_call(url, params, headers)

    except Exception as error:
        cprint(f'Error: {error}, retry...', 'red')
        time.sleep(3)
        return post_call(url, params, headers)
