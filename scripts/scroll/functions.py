import random
from datetime import datetime

from helpers.cli import get_int_in_range
from helpers.csv_helper import write_csv_volume
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import *
from modules.across.functions import eth_bridge
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.orbiter_bridge.functions import orbiter_eth_bridge
from modules.run_zksync.config import ZKSYNC_TOKENS
from modules.run_zksync.functions import odos_swap, open_ocean
from modules.transfer.functions import map_recipients, transfer
from scripts.functions import *
from config.volume_route import VOLUME_ROUTES

total_txs = 0
total_volume = 0


def generate_route_data(lending=False,n=0):

    tx_count=0
    if MAX_SWAPS_PER_REPEAT:
        tx_count=get_int_in_range(MAX_SWAPS_PER_REPEAT)

    data = list(VOLUME_ROUTES.items())
    result_objects = []
    merged_tokens = []
    grouped_tokens = []
    for route_name, route_details in data:
        tokens = route_details['tokens']
        merged_tokens = merged_tokens + tokens

    random.shuffle(merged_tokens)
    for i in range(len(merged_tokens) - 1):
        grouped_tokens.append([merged_tokens[i], merged_tokens[i + 1]])



    # ONLY FOR LENDING route
    if lending:
        check_usdc=grouped_tokens[0][0]==ZKSYNC_TOKENS['USDC']
        if not check_usdc:
            return generate_route_data(lending,n+1)







    for group in grouped_tokens:
        if group[0] == group[1]:
            return generate_route_data(lending,n+1)



        dex = random.choice(data)
        route_name, route = dex
        while True:
            if group[0] in route['tokens'] and group[1] in route['tokens']:
                break
            else:
                dex = random.choice(data)
                route_name, route = dex

        if tx_count and len(result_objects)>=tx_count:
            # ONLY FOR LENDING route
            # if lending and group[0] != ZKSYNC_TOKENS['USDC']:
            #     return generate_route_data(lending,n+1)

            break

        result_objects.append({
            'function': route['function'],
            'function_name': route['function'].__name__,
            'grouped_tokens': group,
            'params': route['params'] if 'params' in route else []
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
