from datetime import datetime

from termcolor import cprint

from config.settings import CHAINS
from helpers.functions import get_min_balance, int_to_wei, wei_to_int
from helpers.settings_helper import get_own_contract_address
from helpers.web3_helper import get_token_balance, check_data_token, add_gas_price, add_gas_limit, sign_tx
from modules.contracts.config import DEPOSIT_ABI, STAKE_ABI

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
