import os
import sys

from termcolor import cprint
from web3 import Web3

from config.settings import *
from helpers.functions import int_to_wei, wei_to_int, round_to, sleeping, get_min_balance
from helpers.web3_helper_async import check_data_token, add_gas_price, add_gas_limit, sign_tx, check_status_tx


async def transfer(web3, private_key: str, to_address: str, chain: str, _token_address: str, _amount: float, retry=0):
    try:
        token_address = _token_address
        account = web3.eth.account.from_key(private_key)
        wallet = account.address
        nonce = await web3.eth.get_transaction_count(wallet)
        min_balance = get_min_balance(chain)

        chain_id=CHAINS[chain]['chain_id']

        if token_address != '':
            token_contract, decimals, symbol = await check_data_token(web3, token_address)
        else:
            decimals = 18
            symbol = CHAINS[chain]['token']
            token_contract = None
            token_address = NATIVE_TOKEN_ADDRESS

        min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

        # Amount
        value = 0
        if not _amount:
            if token_address == NATIVE_TOKEN_ADDRESS:
                balance = await web3.eth.get_balance(web3.to_checksum_address(wallet))
                if balance > int_to_wei(min_balance, decimals):
                    value = balance - int_to_wei(min_balance, decimals)

            else:
                value = await token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()
        else:
            value = int_to_wei(_amount, decimals)

        if not value and token_address == NATIVE_TOKEN_ADDRESS:
            cprint(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}', 'red')
        elif value < min_transaction_amount:
            cprint(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}', 'red')
        else:
            print(value)
            if token_address == NATIVE_TOKEN_ADDRESS:
                contract_txn = {
                    'chainId': chain_id,
                    'gasPrice': 0,
                    'nonce': nonce,
                    'gas': 0,
                    'from': wallet,
                    'to': Web3.to_checksum_address(to_address),
                    'value': int(value)
                }

            else:
                tx = {
                    'from': wallet,
                    'chainId': chain_id,
                    'gasPrice': 0,
                    'gas': 0,
                    'nonce': nonce,
                }

                contract_txn =await token_contract.functions.transfer(
                    Web3.to_checksum_address(to_address),
                    int(value)
                ).build_transaction(tx)

            contract_txn = await add_gas_price(web3, contract_txn, chain)
            contract_txn = await add_gas_limit(web3, contract_txn, chain)

            # Include gas price in value for transfer all
            if token_address == NATIVE_TOKEN_ADDRESS and not _amount:
                gas_estimate = int(contract_txn['gasPrice'] * contract_txn['gas'])
                contract_txn['value'] = round_to(int(value) - gas_estimate, 6)

            tx_hash = sign_tx(web3, contract_txn, private_key)
            tx_link = f'{CHAINS[chain]["scan"]}/{tx_hash}'

            tx_description = f'transfer {wei_to_int(value, decimals)} {symbol} => {to_address}'
            status = await check_status_tx(web3, tx_hash)
            if status == 1:
                cprint(f'{tx_description}: {tx_link}', 'green')
            else:
                raise Exception(f'{tx_description} tx failed: {tx_link}')

    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cprint(f'{STR_CANCEL} {exc_type}: {str(error)}. {exc_tb.tb_frame.f_code.co_filename}, line: {exc_tb.tb_lineno}',
               'red')
        if retry < MAX_RETRIES:
            cprint(f'Retry again in few seconds...', 'red')
            sleeping(7, 8)
        else:
            cprint(f'{STR_CANCEL} Max retries reached, STOP.', 'red')


