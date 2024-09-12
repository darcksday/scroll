from config.settings import MIN_SLEEP, MAX_SLEEP, USE_SHUFFLE, CHAINS, MIN_TRANSACTION_AMOUNT
from helpers.factory import run_script
from helpers.functions import int_to_wei
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_web3, get_token_balance, check_data_token
from loguru import logger
import random
import time

from modules.swaps.functions import xy_swap, unwrap_weth
from modules.to_eth.config import TOKENS, USE_DEXES, MIN_STABLE


def swap_to_eth(rpc_chain):
    prt_keys = get_private_keys()
    web3 = get_web3(CHAINS[rpc_chain]['rpc'])

    if USE_SHUFFLE:
        random.shuffle(prt_keys)

    for key in prt_keys:
        address = web3.eth.account.from_key(key['private_key']).address
        logger.info(f"[{key['index']}][{address}] Start swap tokens")
        for name,token_address in TOKENS.items():
            logger.info(f"[{name}] Check")

            balance=get_token_balance(web3, address, token_address)
            token_contract, decimals, symbol = check_data_token(web3, token_address)

            min_amount = MIN_TRANSACTION_AMOUNT if decimals>6 else MIN_STABLE

            if balance > int_to_wei(min_amount, decimals):
                to_token =''
                amount_str = ''
                params = [token_address, to_token]
                dex=random.choice(USE_DEXES)

                if token_address in [TOKENS['WBTC'],TOKENS['DAI']]:
                    dex = xy_swap


                if token_address == TOKENS['WETH']:
                    run_script(unwrap_weth, 'scroll', 0, [], key)
                else:
                    run_script(dex, 'scroll', amount_str, params,key)
                time.sleep(1)




