
from termcolor import cprint
from loguru import logger

from config.settings import NULL_TOKEN_ADDRESS, NATIVE_TOKEN_ADDRESS
from helpers.functions import get_min_balance, int_to_wei, sleeping, wei_to_int
from helpers.web3_helper import get_token_balance, add_gas_price, add_gas_limit, sign_tx, approve_token, price_token, all_prices, \
    check_allowance
from modules.landings.config import ERA_LAND_CONTRACTS, ERA_LAND_ABI, LAYERBANK_CONTRACT, LAYERBANK_WETH_CONTRACT, LAYERBANK_ABI, \
    ZERO_VIX_CONTRACT, ABI_ZERO_VIX, LAYERBANK_USDC_CONTRACT, BORROW_RATE
from modules.swaps.config import TOKENS
from modules.swaps.functions import swap_token_syncswap
from scripts.functions import run_script_one


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


def enable_collateral(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Wallet {wallet} -->', 'green')

    logger.info(
        f"{wallet}] Enable collateral LAYERBANK | ETH"
    )

    contract_txn = {
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'value': 0,
        'gasPrice': 0,
        'gas': 0,
        'chainId': web3.eth.chain_id
    }

    contract_txn = contract.functions.enterMarkets(
        [web3.to_checksum_address(LAYERBANK_WETH_CONTRACT)]
    ).build_transaction(contract_txn)

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash



def borrow_usdc(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Wallet {wallet} borrow USDC -->', 'green')

    if value:
        amount = int_to_wei(value, 6)

    else:
        value = get_max_borrow_amount(web3, wallet)
        amount = int_to_wei(value, 6)

    logger.info(
        f"{wallet}] Borrow from Layerbank | " +
        f"{value} USDC"
    )

    contract_txn = {
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'value': 0,
        'gasPrice': 0,
        'gas': 0,
        'chainId': web3.eth.chain_id
    }

    contract_txn = contract.functions.borrow(LAYERBANK_USDC_CONTRACT,amount).build_transaction(contract_txn)

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash

def repay_usdc(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)

    wallet = web3.eth.account.from_key(private_key).address
    amount = get_token_balance(web3, wallet, TOKENS['USDC'])

    if amount > 0:

        cprint(f'/-- Wallet {wallet} -->', 'green')

        # if value > 0:
        logger.info(
            f"{wallet}] Repay to Layerbank | " +
            f"{wei_to_int(amount, 6)} USDC"
        )

        allowance_amount = check_allowance(web3, TOKENS['USDC'], wallet, LAYERBANK_USDC_CONTRACT)
        if amount > allowance_amount:
            cprint(f'/-- Approve token', 'green')

            approve_token(web3, private_key, chain_id, TOKENS['USDC'], LAYERBANK_USDC_CONTRACT)
            sleeping(5, 8)

        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'gasPrice': 0,
            'gas': 0,
            'chainId': web3.eth.chain_id
        }

        contract_txn = contract.functions.repayBorrow(LAYERBANK_USDC_CONTRACT,amount).build_transaction(contract_txn)

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(f'SKIP. No borrowed USDC')




def get_max_borrow_amount(web3, wallet):
    response = get_lb_data(web3, wallet)
    if response and response[1] > 0:
        return round(wei_to_int(response[1], 18) * BORROW_RATE, 2)

def get_lb_data(web3, wallet):
    address_contract = web3.to_checksum_address(LAYERBANK_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=LAYERBANK_ABI)
    response = contract.functions.accountLiquidityOf(wallet).call()
    return response if response else None

def buy_full_repay(web3, private_key):
    wallet = web3.eth.account.from_key(private_key).address

    response = get_lb_data(web3, wallet)
    if response and response[2] > 0:

        borrowed_balance =wei_to_int(response[2],18)

        current_balance = get_token_balance(web3, wallet, TOKENS['USDC'],True)



        rest = int((borrowed_balance - current_balance) * 1.1+0.9)

        if rest > 0:
            eth_price = price_token(all_prices(), "ETH")
            eth_amount = rest / float(eth_price)

            run_script_one(swap_token_syncswap, private_key, 'scroll', eth_amount, ['', TOKENS['USDC']])




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