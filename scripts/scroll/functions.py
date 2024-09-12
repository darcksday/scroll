import random

from config.volume_config import USE_DEXES
from helpers.cli import get_int_in_range
from helpers.csv_helper import write_csv_volume
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import *
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.orbiter_bridge.functions import orbiter_eth_bridge
from modules.swaps.config import TOKENS
from modules.transfer.functions import map_recipients, transfer
from scripts.functions import *

total_txs = 0
total_volume = 0


def generate_route_data(length):
    length=get_int_in_range(length)



    # to even number
    if length % 2 != 0:
        length += 1


    random.shuffle(USE_DEXES)
    result_objects = []
    dexes = USE_DEXES * (length // len(USE_DEXES)) + USE_DEXES[:length % len(USE_DEXES)]

    for one in range(length):

        if one % 2 == 0:
            group = [TOKENS['USDC'], TOKENS['USDT']]
        else:
            group = [TOKENS['USDT'], TOKENS['USDC']]


        result_objects.append({
            'function': dexes[one],
            'function_name': dexes[one].__name__,
            'grouped_tokens': group,
        })


    return result_objects


def generate_path(web3, routes):
    path = ''
    for route in routes:
        token1 = route['grouped_tokens'][0]
        token2 = route['grouped_tokens'][1]
        token_contract1, decimals1, symbol1 = check_data_token(web3, token1)
        token_contract2, decimals2, symbol2 = check_data_token(web3, token2)
        path = path + f"({route['function_name']} {symbol1} -> {symbol2})->"

    return f"ETH->{path}->ETH->"


def get_eth_price(amount):
    eth_price = price_token(all_prices(), "ETH")
    return_max = float(eth_price) * amount
    return_min = round(return_max - return_max * 0.01, 6)
    return int(return_min)


def add_to_stat(tx_count, amount):
    global total_txs, total_volume
    total_txs += tx_count
    total_volume += amount
