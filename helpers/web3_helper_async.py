import json
import random
import sys
import time
import math

from termcolor import cprint
from web3.eth import AsyncEth

from config.settings import *
from web3 import Web3, AsyncHTTPProvider
from helpers.functions import sleeping, wei_to_int, int_to_wei
from loguru import logger




async def add_gas_limit(web3, contract_txn, chain, approve=0):
    if chain == 'metis':
        contract_txn['gas'] = 572686
        return contract_txn
    elif chain == 'moonriver' or chain == 'moonbeam':
        contract_txn['gas'] = 348350
        return contract_txn

    gas_limit =await web3.eth.estimate_gas(contract_txn)

    if chain == 'zksync' and approve == 0 and 'GAS_LIMIT_COF' in globals():
        contract_txn['gas'] = int(gas_limit*GAS_LIMIT_COF)
    elif chain == 'dfk':
        contract_txn['gas'] = int(gas_limit * 2)
    elif chain == 'goerly':
        contract_txn['gas'] = int(gas_limit * 2)
    else:
        multiplier = [1.1, 1.2]
        contract_txn['gas'] = int(gas_limit * random.uniform(multiplier[0], multiplier[1]))

    return contract_txn


async def add_gas_price(web3, contract_txn, chain=''):
    try:
        if chain == 'moonbeam':
            contract_txn['gasPrice'] = int(await web3.eth.gas_price * 1.1)
        elif chain == 'moonriver':
            contract_txn['gasPrice'] = int(await web3.eth.gas_price * 1.1)
        elif chain == 'goerly':
            contract_txn['gasPrice'] = int(await web3.eth.gas_price * 2)
        elif chain == 'bsc':
            contract_txn['gasPrice'] = int(2000000000)
        else:
            contract_txn['gasPrice'] = int(await web3.eth.gas_price)

    except Exception as error:
        cprint(f"Gas Price error: {error}. Random gasPrice: {contract_txn['gasPrice']}", 'red')

    return contract_txn


async def sign_tx(web3, contract_txn, private_key):
    signed_tx = web3.eth.account.sign_transaction(contract_txn, private_key)
    raw_tx_hash = await web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = web3.to_hex(raw_tx_hash)

    return tx_hash


async def check_status_tx(web3, tx_hash):
    cprint(f'Checking tx_status: {tx_hash}', 'blue')
    repeat_count = 0
    while True:
        try:

            await web3.eth.wait_for_transaction_receipt(tx_hash)
            status_ = await web3.eth.get_transaction_receipt(tx_hash)
            status = status_["status"]
            if status in [0, 1]:
                return status
            time.sleep(3)
        except Exception as error:
            repeat_count += 1
            if repeat_count > 27:
                return 1
            else:
                cprint(f'{error} retry...', 'red')
                time.sleep(5)


async def check_data_token(web3, token_address, abi=None):
    if abi is None:
        abi = get_erc20_abi()

    try:
        token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=abi)
        decimals = await token_contract.functions.decimals().call()
        symbol = await token_contract.functions.symbol().call()
        return token_contract, decimals, symbol

    except Exception as error:
        cprint(f'Error: {error}', 'red')


async def check_allowance(web3, token_address, wallet, spender):
    try:
        contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=get_erc20_abi())
        amount_approved = await contract.functions.allowance(wallet, spender).call()
        return amount_approved

    except Exception as error:
        cprint(f'Error: {error}', 'red')


async def get_token_balance(web3, wallet_address, contract_address='', balance_round=False):
    try:
        if contract_address in ['', NATIVE_TOKEN_ADDRESS, NULL_TOKEN_ADDRESS]:
            balance = await web3.eth.get_balance(web3.to_checksum_address(wallet_address))
            token_decimal = 18
        else:
            token_contract, token_decimal, symbol = check_data_token(web3, contract_address)
            balance = await token_contract.functions.balanceOf(web3.to_checksum_address(wallet_address)).call()

        if balance_round:
            wei = wei_to_int(balance, token_decimal)
            # float number
            decimal_places = 8
            factor = 10 ** decimal_places
            rounded_number = math.floor(wei * factor) / factor
            return rounded_number
        return int(balance)
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cprint(f'{STR_CANCEL} {exc_type}: {str(error)}. {exc_tb.tb_frame.f_code.co_filename}, line: {exc_tb.tb_lineno}',
               'red')
        time.sleep(10)
        return get_token_balance(web3, wallet_address, contract_address='', balance_round=False)








def check_wait_web3_balance(web3_provider, chain, wallet_address, token, amount):

    while True:
        cprint(f"/-- Check {chain} wallet balance: {wallet_address} ({amount})", "blue")
        balance = await get_token_balance(web3_provider, wallet_address, token, True)
        if balance >= amount:
            cprint(f"/-- {balance} found", "green")
            time.sleep(5)
            return balance

        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue




def get_web3(url,proxy=None):
    if proxy:
        logger.info(f"Use proxy {proxy['http']}")


        return Web3(AsyncHTTPProvider(url,request_kwargs={"proxy": proxy}), modules={"eth": (AsyncEth)}, middlewares=[])


    else:
        return Web3(AsyncHTTPProvider(url), modules={"eth": (AsyncEth)}, middlewares=[])






def get_erc20_abi():
    with open("config/abi/erc20.json", "r") as file:
        erc20_abi = json.load(file)
    return erc20_abi


