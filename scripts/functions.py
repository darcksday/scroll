import ccxt
import time
import sys
from dotenv import dotenv_values
from loguru import logger
from termcolor import cprint

from config.settings import CHAINS, STR_DONE, MIN_SLEEP, MAX_SLEEP, CHECK_GWEI
from helpers.cli import get_amount_in_range
from helpers.functions import sleeping
from helpers.web3_helper import check_status_tx, get_web3, wait_gas, sign_tx
from okx.SubAccount import SubAccountAPI




config = dotenv_values("config/.env")

def get_okx_account(sub_account=0):
    if sub_account:
        api_key = f'OKX_SUB{sub_account}_API_KEY'
        api_secret = f'OKX_SUB{sub_account}_API_SECRET'
        api_password = f'OKX_SUB{sub_account}_PASSWORD'
    else:
        api_key = 'OKX_API_KEY'
        api_secret = 'OKX_API_SECRET'
        api_password = 'OKX_PASSWORD'

    return ccxt.okx({
        'apiKey': config[api_key],
        'secret': config[api_secret],
        'password': config[api_password],
        'enableRateLimit': True,
        'options': {
            'defaultType': 'main',
        }
    })

def get_okx_sub():
    return SubAccountAPI(
        api_key=config['OKX_API_KEY'],
        api_secret_key=config['OKX_API_SECRET'],
        passphrase=config['OKX_PASSWORD'],
        flag='0',
        debug=False
        )


def tranfer_from_subs_okx(token='ETH'):
    okx_main_account = get_okx_account()
    okx_sub_account = get_okx_sub()
    accounts=okx_sub_account.get_subaccount_list()



    for account in accounts['data']:
        response = okx_sub_account.get_funding_balance(
            subAcct=account['subAcct'],
            ccy=token
        )
        if response['code'] != '0':
            cprint(f"Error: {response['msg']}", "red")
            continue

        cprint(f"/-- Check {token} subAccount {account['subAcct']} ", "blue")
        balance = float(response['data'][0]['availBal'])
        balance = int(balance * 10**8) / 10**8
        time.sleep(2)

        if balance>0:
            cprint(f"{balance} ETH found, transfer to OKX main account", "green")
            okx_main_account.transfer(token, balance,account['subAcct'], 'master')
            time.sleep(2)


def get_okx_token_balance(sub_account=0, token='USDT'):
    okx_main_account = get_okx_account(sub_account)

    balances = okx_main_account.fetch_balance({"ccy": token, "type": "funding"})
    return balances['free'][token]


def get_binance_token_balance(token):
    account = ccxt.binance({
        'apiKey': config['BINANCE_API_KEY'],
        'secret': config['BINANCE_API_SECRET'],
        'enableRateLimit': True,
        'options': {
            'defaultType': 'main',
        }
    })
    balances = account.fetch_balance({"type": "spot"})
    return balances['free'][token]


def get_bitget_token_balance(token):
    account = ccxt.bitget({
        'apiKey': config['BITGET_API_KEY'],
        'secret': config['BITGET_API_SECRET'],
        'password': config['BITGET_PASSWORD'],
        'enableRateLimit': True,
        'options': {
            'defaultType': 'main',
        }

    })
    balances = account.fetch_balance({"type": "spot"})
    return balances['free'][token]


def sell_token(token,price,amount):
    account = ccxt.bitget({
        'apiKey': config['BITGET_API_KEY'],
        'secret': config['BITGET_API_SECRET'],
        'password': config['BITGET_PASSWORD'],
        'enableRateLimit': True,
        # 'options': {
        #     'defaultType': 'main',
        # }

    })

    return  account.create_order(token,'limit','sell',amount,price)

def get_order_info(order_id,symbol):
    account = ccxt.bitget({
        'apiKey': config['BITGET_API_KEY'],
        'secret': config['BITGET_API_SECRET'],
        'password': config['BITGET_PASSWORD'],
        'enableRateLimit': True,

    })

    return account.fetch_order(order_id,symbol)


def run_script_one(method, private_key, chain, _amount, params=[], repeat=0):
    if CHECK_GWEI:
        wait_gas()

    web3 = get_web3(CHAINS[chain]['rpc'])
    amount = get_amount_in_range(_amount,False)

    try:
        tx_hash = method(web3, private_key, amount, *params)
        if tx_hash:
            tx_link = f'{CHAINS[chain]["scan"]}/{tx_hash}'
            time.sleep(2)
            status = check_status_tx(web3, chain, tx_hash)
            if status == 1:
                logger.success(f'{STR_DONE} {chain} transaction: {tx_link}')
            else:
                raise Exception(f'{chain} transaction failed: {tx_link}')
            sleeping(MIN_SLEEP, MAX_SLEEP)

    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        err_formated = f'{str(error)}. {exc_tb.tb_frame.f_code.co_filename}, line: {exc_tb.tb_lineno}'
        logger.error(err_formated)

        if repeat < 5:
            time.sleep(10)
            return run_script_one(method, private_key, chain, _amount, params, repeat + 1)
        else:
            raise Exception(f'{chain} Repeat limit exceeded')



