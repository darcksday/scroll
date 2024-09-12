from config.settings import MIN_SLEEP, MAX_SLEEP, USE_SHUFFLE, CHAINS, UNUSED_REPEAT
from config.swap_routes import ROUTES
from helpers.cli import get_int_in_range
from helpers.factory import run_random_swap, run_script
from helpers.functions import sleeping, api_call
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_web3
from loguru import logger
import random

from modules.unused_contracts.config import *


def run_unused_fn(rpc_chain):
    prt_keys = get_private_keys()
    web3 = get_web3(CHAINS[rpc_chain]['rpc'])
    all_contracts = ALL_FUNCTIONS
    api_url = "https://api.scrollscan.com/api"

    if USE_SHUFFLE:
        random.shuffle(prt_keys)

    for key in prt_keys:
        address = web3.eth.account.from_key(key['private_key']).address
        logger.info(f'Start on {address}')
        repeats = get_int_in_range(UNUSED_REPEAT)

        for step in range(repeats):
            logger.info(f'Step {step + 1}/{repeats}')
            tx_list = api_call(api_url, {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 200,
            })

            contract_addresses = set()

            for tx in tx_list['result']:
                to_address = tx['to']
                if to_address:
                    contract_addresses.add(web3.to_checksum_address(to_address))

            filtered_contracts = [
                (value, key) for key, value in all_contracts.items() if
                web3.to_checksum_address(key) not in contract_addresses
            ]

            if len(filtered_contracts):
                random_choose = random.choice(filtered_contracts)
                random_fn = random_choose[0]

                if isinstance(random_fn, list):

                    params=[]
                    if random_fn[0].__name__ in ['stake_unused', 'withdraw_unused']:
                        params = [random_choose[1]]



                    # for Lending
                    logger.info(f'Random chosen  {random_fn[0].__name__} left {len(filtered_contracts)}')

                    run_script(random_fn[0], rpc_chain, '', params, key)
                    sleeping(30, 60)
                    run_script(random_fn[1], rpc_chain, '', params, key)


                elif random_fn.__name__ in ROUTES:
                    f_name = random_fn.__name__
                    logger.info(f'Random chosen  {f_name} left {len(filtered_contracts)}')
                    extracted_route = {f_name: ROUTES[f_name]}
                    run_random_swap(extracted_route, rpc_chain, '', key)

                else:
                    print(random_fn.__name__ )
                    f_name = random_fn.__name__
                    logger.info(f'Random chosen  {f_name} left {len(filtered_contracts)}')

                    params = []
                    # Add params for NFT mint
                    if f_name == 'mint_nfts2_me':
                        params = ["scroll", random_choose[1]]

                    run_script(random_fn, rpc_chain, '', params, key)

            else:
                logger.info(f'No unused contracts found for   {address}')
                break
