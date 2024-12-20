import json
import random
from datetime import datetime

from eth_account.messages import encode_defunct, encode_structured_data
from hexbytes import HexBytes
from loguru import logger
from termcolor import cprint

from config.settings import CHAINS
from helpers.functions import get_min_balance, int_to_wei, wei_to_int, api_call, post_call, post_scroll_call, post_odos_call
from helpers.settings_helper import get_own_contract_address, get_ref_list
from helpers.web3_helper import get_token_balance, check_data_token, add_gas_price, add_gas_limit, sign_tx
from modules.contracts.config import DEPOSIT_ABI, STAKE_ABI, PUMP_CONTRACT, PUMP_ABI, SCROLL_ABI, ODOS_ABI

chain = 'scroll'


def stake(web3, private_key, _amount):

    address_contract,type_contract = get_own_contract_address(private_key)



    abi= STAKE_ABI if type_contract=='Staking' else DEPOSIT_ABI

    contract = web3.eth.contract(address=address_contract, abi=abi)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Start stake on {wallet} at contract {address_contract}', 'green')
    balance = get_token_balance(web3, wallet)
    min_balance=get_min_balance(chain)


    decimals = 18
    symbol = CHAINS[chain]['token']



    # Amount
    amount = 0
    if not _amount:
        if balance > int_to_wei(min_balance, decimals):
            amount = int(balance - int_to_wei(min_balance, decimals))
    else:
        amount = int_to_wei(_amount, decimals)
    cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')

    if not amount :
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    else:
        if type_contract=='Staking':
            method=contract.functions.stake()
        else:
            current_timestamp = int(datetime.now().timestamp()+5)

            method=contract.functions.deposit(current_timestamp)

        contract_txn = method.build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': amount,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


def withdraw(web3, private_key, _amount):

    address_contract,type_contract = get_own_contract_address(private_key)


    abi= STAKE_ABI if type_contract=='Staking' else DEPOSIT_ABI

    contract = web3.eth.contract(address=address_contract, abi=abi)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Withdraw on {wallet} from contract {address_contract}', 'green')



    contract_txn = contract.functions.withdraw().build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
        })

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def claim(web3, private_key, _amount):

    address_contract,type_contract = get_own_contract_address(private_key)



    contract = web3.eth.contract(address=address_contract, abi=STAKE_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Claim rewards on {wallet} contract: {address_contract}', 'green')

    if not type_contract == 'Staking':
        raise Exception(f'SKIP. Not Staking contract')

    contract_txn = contract.functions.claimRewards().build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
        })

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash




def stake_unused(web3, private_key, _amount,address_contract):




    abi= STAKE_ABI

    contract = web3.eth.contract(address=address_contract, abi=abi)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Start stake on {wallet} at contract {address_contract}', 'green')
    balance = get_token_balance(web3, wallet)
    min_balance=get_min_balance(chain)


    decimals = 18
    symbol = CHAINS[chain]['token']



    # Amount
    amount = 0
    if not _amount:
        if balance > int_to_wei(min_balance, decimals):
            amount = int(balance - int_to_wei(min_balance, decimals))
    else:
        amount = int_to_wei(_amount, decimals)
    cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')

    if not amount :
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    else:
        method=contract.functions.stake()

        contract_txn = method.build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': amount,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
def withdraw_unused(web3, private_key, _amount,address_contract):



    abi= STAKE_ABI

    contract = web3.eth.contract(address=address_contract, abi=abi)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Withdraw on {wallet} from contract {address_contract}', 'green')

    staked_amount=contract.functions.stakedBalances(wallet).call()

    cprint(f'/-- Staked amount {staked_amount}', 'blue')

    if staked_amount>0:
        contract_txn = contract.functions.withdraw().build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': 0,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


def claim_pump(web3, private_key, _amount=0):
    wallet = web3.eth.account.from_key(private_key).address
    data=pump_claim_data(wallet)
    amout=int(data['amount'])

    logger.info(f"[{wallet}] Claim {wei_to_int(amout,18)}")
    contract = web3.eth.contract(address=PUMP_CONTRACT, abi=PUMP_ABI)

    ref=random.choice(get_ref_list(path='config/pump_ref.txt'))
    if ref:
        ref=web3.to_checksum_address(ref)

    print(amout,
        data['sign'],
        ref)
    contract_txn = contract.functions.claim(
        amout,
        HexBytes( data['sign']),
        ref
    ).build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
        })

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash

def pump_claim_data(wallet):
    url='https://api.scrollpump.xyz/api/Airdrop/GetSign'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://scrollpump.xyz',
        'priority': 'u=1, i',
        'referer': 'https://scrollpump.xyz/',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    params = {
        'address': wallet,
    }


    data=api_call(url,params,headers)

    return data.get('data')



def claim_scroll(web3, private_key, _amount=0):
    wallet =web3.to_checksum_address( web3.eth.account.from_key(private_key).address)
    data=scroll_claim_data(wallet)
    if not data['claimed_at']:
        amount=int(data['amount'])
        proof= data['proof']


        logger.info(f"[{wallet}] Claim {wei_to_int(amount,18)}")
        contract = web3.eth.contract(address='0xE8bE8eB940c0ca3BD19D911CD3bEBc97Bea0ED62', abi=SCROLL_ABI)
        contract_txn = contract.functions.claim(
            wallet,
            amount,
            proof

        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': 0,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


    else:
        logger.error(f'[{wallet}] | Already claimed')


def scroll_claim_data(wallet):
    url='https://claim.scroll.io/?step=4'
    headers = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Next-Action": "2ab5dbb719cdef833b891dc475986d28393ae963"

    }

    params = [
        wallet

    ]


    data=post_scroll_call(url,params,headers)

    return data



def odos_claim_data(wallet):
    url=f"https://api.odos.xyz/loyalty/permits/8453/0xca73ed1815e5915489570014e024b7EbE65dE679/{wallet}"





    data=post_odos_call(url)

    return data



def claim_odos(web3, private_key, _amount=0):
    wallet =web3.to_checksum_address( web3.eth.account.from_key(private_key).address)
    data=odos_claim_data(wallet)
    text = 'By signing this, you agree to be bound by the terms set forth in the Odos DAO LLC Amended and Restated Operating Agreement (as amended from time to time), available at: https://docs.odos.xyz/home/dao/operating-agreement.'

    if data:
        typed_data = {
            "domain": {
                "name": "OdosDaoRegistry",
                "version": "1",
                "chainId": 8453,
                "verifyingContract": "0x8bDA13Bc6DC08d4008C9f3A72C4572C98478502c",
            },
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Registration": [
                    {"name": "member", "type": "address"},
                    {"name": "agreement", "type": "string"},
                    {"name": "nonce", "type": "uint256"},
                ],
            },
            "primaryType": "Registration",
            "message": {
                "member": wallet,
                "agreement": "By signing this, you agree to be bound by the terms set forth in the Odos DAO LLC Amended and Restated Operating Agreement (as amended from time to time), available at: https://docs.odos.xyz/home/dao/operating-agreement.",
                "nonce": 0,
            },
        }

        data_encoded = encode_structured_data(typed_data)
        signed_message = web3.eth.account.sign_message(data_encoded, private_key=private_key)




        text_signature=signed_message.signature.hex()
        proof=data['data']['signature']
        data=data['data']['claim']
        amount =int(data['amount'])
        logger.info(f"[{wallet}] Claim {wei_to_int(amount,18)}")
        contract = web3.eth.contract(address='0x4C8f8055D88705f52c9994969DDe61AB574895a3', abi=ODOS_ABI)
        contract_txn = contract.functions.registerAndClaim(
            (
                wallet,
            wallet,
            data['payoutToken'],
            amount,
            int(data['nonce']),
            int(data['deadline'])
            ),
            (
            wallet,
            text,
            int(data['nonce']),
            ),
            proof,
            text_signature

        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': 0,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


    else:
        logger.error(f'[{wallet}] | Already claimed')