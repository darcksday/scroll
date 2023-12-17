
from termcolor import cprint
from loguru import logger

from config.settings import NULL_TOKEN_ADDRESS, NATIVE_TOKEN_ADDRESS
from helpers.functions import get_min_balance, int_to_wei, sleeping, wei_to_int
from helpers.web3_helper import get_token_balance, add_gas_price, add_gas_limit, sign_tx, approve_token
from modules.landings.config import ERA_LAND_CONTRACTS, ERA_LAND_ABI, LAYERBANK_CONTRACT, LAYERBANK_WETH_CONTRACT, LAYERBANK_ABI, \
    ZERO_VIX_CONTRACT, ABI_ZERO_VIX


def supply_eth_eralend(web3, private_key, _amount):
    chain_id = 'zksync'
    address_contract = web3.to_checksum_address(ERA_LAND_CONTRACTS['landing'])
    wallet = web3.eth.account.from_key(private_key).address
    # if _amount == 0:
    #     raise Exception('Amount cannot be zero, you need ETH for withdraw supply')

    balance = get_token_balance(web3, wallet, NULL_TOKEN_ADDRESS)
    min_balance=get_min_balance(chain_id)

    if not _amount:
        if balance > int_to_wei(min_balance, 18):
            _amount = int(balance - int_to_wei(min_balance, 18))

    else:
        _amount = int_to_wei(_amount, 18)

    cprint(f'/-- Wallet {wallet} -->', 'green')
    contract_txn = {
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'value': _amount,
        'gasPrice': 0,
        'gas': 0,
        'to': address_contract,
        'data': f'0x1249c58b',
        'chainId': web3.eth.chain_id
    }

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash



def withdraw_eth_eralend(web3, private_key, value=0):
    chain_id = 'zksync'
    address_contract = web3.to_checksum_address(ERA_LAND_CONTRACTS['landing'])
    contract = web3.eth.contract(address=address_contract, abi=ERA_LAND_ABI)


    wallet = web3.eth.account.from_key(private_key).address
    amount = contract.functions.balanceOfUnderlying(wallet).call()

    cprint(f'/-- Wallet {wallet} -->', 'green')

    if amount > 0:
        logger.info(
            f"{wallet}] Make withdraw from Eralend | " +
            f"{web3.from_wei(amount, 'ether')} ETH"
        )


        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
            'chainId': web3.eth.chain_id
        }

        contract_txn=contract.functions.redeemUnderlying(amount).build_transaction(contract_txn)

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(f'SKIP. No staked ETH')



def supply_eth_layerbank(web3, private_key, _amount):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)


    # if _amount == 0:
    #     raise Exception('Amount cannot be zero, you need ETH for withdraw supply')

    balance = get_token_balance(web3, wallet, NULL_TOKEN_ADDRESS)
    min_balance=get_min_balance(chain_id)

    if not _amount:
        if balance > int_to_wei(min_balance, 18):
            _amount = int(balance - int_to_wei(min_balance, 18))

    else:
        _amount = int_to_wei(_amount, 18)

    cprint(f'/-- Wallet {wallet} -->', 'green')
    contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': _amount,
            'gasPrice': 0,
            'gas': 0,
            'chainId': web3.eth.chain_id
        }

    contract_txn = contract.functions.supply(
        web3.to_checksum_address(LAYERBANK_WETH_CONTRACT),
        _amount


    ).build_transaction(contract_txn)


    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash



def withdraw_eth_layerbank(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    amount = get_token_balance(web3, wallet, LAYERBANK_WETH_CONTRACT)


    cprint(f'/-- Wallet {wallet} -->', 'green')

    if amount > 0:
        logger.info(
            f"{wallet}] Make withdraw from Layerbank | " +
            f"{web3.from_wei(amount, 'ether')} ETH"
        )

        cprint(f'/-- Approve token', 'green')
        approve_token(web3, private_key, chain_id, LAYERBANK_WETH_CONTRACT, address_contract)
        sleeping(5, 8)

        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
            'chainId': web3.eth.chain_id
        }

        contract_txn=contract.functions.redeemToken(
            web3.to_checksum_address(LAYERBANK_WETH_CONTRACT),
            amount

        ).build_transaction(contract_txn)

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(f'SKIP. No staked ETH')


def supply_eth_0vix(web3, private_key, _amount):
    chain = 'polygon_zkevm'
    address_contract = web3.to_checksum_address(ZERO_VIX_CONTRACT)
    wallet = web3.to_checksum_address(web3.eth.account.from_key(private_key).address)
    cprint(f'/-- Supply ETH, wallet {wallet} -->', 'green')

    decimals = 18
    symbol = 'ETH'
    balance = get_token_balance(web3, wallet, NATIVE_TOKEN_ADDRESS)
    min_balance=get_min_balance(chain)

    # Amount
    amount = 0
    if not _amount:
        if balance > int_to_wei(min_balance, decimals):
            amount = int(balance - int_to_wei(min_balance,decimals))
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)
    if not amount:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    else:
        contract = web3.eth.contract(address=address_contract, abi=ABI_ZERO_VIX)
        contract_txn = contract.functions.mint().build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': amount,
                'gasPrice': 0,
                'gas': 0,
            }
        )

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)

        return tx_hash


def withdraw_supply_eth_0vix(web3, private_key, amount=0):
    chain = 'polygon_zkevm'
    address_contract = web3.to_checksum_address(ZERO_VIX_CONTRACT)
    wallet = web3.to_checksum_address(web3.eth.account.from_key(private_key).address)
    cprint(f'/-- Withdraw sypply ETH, wallet {wallet} -->', 'green')

    contract = web3.eth.contract(address=address_contract, abi=ABI_ZERO_VIX)
    data = contract.functions.getAccountSnapshot(wallet).call({'from': wallet})
    return_amount_wei = int(int(data[1]) * wei_to_int(data[3], 18))
    cprint(f'Return amount wei: {return_amount_wei}', 'green')

    if not return_amount_wei:
        raise Exception(f'SKIP. No supply')
    else:
        contract_txn = contract.functions.redeemUnderlying(
            return_amount_wei
        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': 0,
                'gasPrice': 0,
                'gas': 0,
            }
        )

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash