import decimal
import time

from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from modules.orbiter_bridge.config import *
from helpers.functions import int_to_wei, get_min_balance, api_call
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from modules.transfer.functions import map_recipients


def orbiter_eth_bridge(web3, private_key: str, _amount: float, from_chain: str, to_chain: str):
    account = web3.eth.account.from_key(private_key)
    wallet = account.address

    cprint(f'/-- Orbiter ETH Bridge: {from_chain} => {to_chain} for {wallet} -->', 'green')

    # Amount
    balance = 0
    if not _amount:
        balance = get_token_balance(web3, wallet, '', True)

    min_balance = get_min_balance(from_chain)

    if balance > min_balance:
        # Increase amount to cover gas fees
        amount = balance - min_balance
        cprint(f'/-- Amount: {amount} ETH', 'green')
    else:
        amount = _amount

    amount += 0.00071

    if amount >= ORBITER_MIN_AMOUNT:
        amount = __get_orbiter_eth_value(amount, to_chain)
        value = int_to_wei(amount, 18)
        chain_id = web3.eth.chain_id
        nonce = web3.eth.get_transaction_count(wallet)

        contract_txn = {
            'chainId': chain_id,
            'nonce': nonce,
            'from': wallet,
            'to': web3.to_checksum_address('0xe4edb277e41dc89ab076a1f049f4a3efa700bce8'),
            'value': value,
            'gasPrice': 0,
        }

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(
            f'{STR_CANCEL} Can\'t bridge: amount less than minimal ({amount} < {ORBITER_MIN_AMOUNT}), skip.')


def orbiter_token_bridge(web3, private_key: str, _amount: float, from_chain: str, to_chain: str, token_address: str):
    account = web3.eth.account.from_key(private_key)
    wallet = account.address
    cprint(f'/-- Orbiter Token Bridge: {from_chain} => {to_chain} for {account.address} -->', 'green')
    token_contract, token_decimal, symbol = check_data_token(web3, token_address)

    # Amount
    if not _amount:
        balance = get_token_balance(web3, account.address, token_address, False)
        # left some amount for next orbiter amount update
        amount = wei_to_int(int(balance * 0.995), token_decimal)
        cprint(f'/-- Amount: {amount} {symbol}', 'green')
    else:
        amount = _amount

    if amount >= ORBITER_MIN_STABLE_TRANSFER:
        if token_decimal == 18:
            orbiter_amount = __get_orbiter_eth_value(amount, to_chain)
        elif token_decimal == 6:
            orbiter_amount = __get_orbiter_token_value(amount, to_chain)
        else:
            raise Exception(f'Unsupported token decimal: {token_decimal}')

        # allowance_amount = check_allowance(web3, token_address, account.address, '0x41d3D33156aE7c62c094AAe2995003aE63f587B3')
        # if amount > allowance_amount:
        #     cprint(f'/-- Approve token: {symbol}', 'green')
        #     approve_token(web3, private_key, from_chain, token_address, '0x41d3D33156aE7c62c094AAe2995003aE63f587B3')
        #     sleeping(5, 10)

        value = int_to_wei(orbiter_amount, token_decimal)
        token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=get_erc20_abi())

        tx = {
            'from': wallet,
            'chainId': web3.eth.chain_id,
            'gasPrice': 0,
            'gas': 0,
            'nonce': web3.eth.get_transaction_count(wallet),
        }

        transaction = token_contract.functions.transfer(
            '0x41d3D33156aE7c62c094AAe2995003aE63f587B3',
            value
        ).build_transaction(tx)

        transaction = add_gas_price(web3, transaction, from_chain)
        transaction = add_gas_limit(web3, transaction, from_chain)

        tx_hash = sign_tx(web3, transaction, private_key)
        return tx_hash
    else:
        raise Exception(
            f'{STR_CANCEL} Can\'t bridge: amount less than minimal ({amount} < {ORBITER_MIN_STABLE_TRANSFER}), skip.')


def __get_orbiter_eth_value(base_num, chain):
    base_num_dec = decimal.Decimal(str(base_num))
    orbiter_amount_dec = decimal.Decimal(str(ORBITER_AMOUNT[chain]))
    difference = base_num_dec - orbiter_amount_dec
    random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
    result_dec = difference + random_offset
    orbiter_str = ORBITER_AMOUNT_STR[chain][-4:]
    result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
    result_str = result_str[:-4] + orbiter_str
    return decimal.Decimal(result_str)


def __get_orbiter_token_value(base_num, chain):
    base_num_dec = decimal.Decimal(str(base_num))
    orbiter_amount_dec = decimal.Decimal(str(ORBITER_AMOUNT[chain]))
    difference = base_num_dec - orbiter_amount_dec
    random_offset = decimal.Decimal(str(random.uniform(-0.001, 0.001)))
    result_dec = difference + random_offset
    orbiter_str = ORBITER_AMOUNT_STR[chain][-4:]
    result_str = '{:.6f}'.format(result_dec.quantize(decimal.Decimal('0.000001')))
    result_str = result_str[:-4] + orbiter_str
    return decimal.Decimal(result_str)


def claim_points(address):
    url = 'https://api.orbiter.finance/points_system/user/card/draw'
    params = {'address': address}
    proxies = get_random_proxy()

    try:
        requests.get('https://api.orbiter.finance/points_system/v2/user/points', params=params, headers=None, proxies=proxies)
        requests.get('https://api.orbiter.finance/points_system/user/nfts', params=params, headers=None, proxies=proxies)
        time.sleep(1)
        requests.get('https://api.orbiter.finance/points_system/user/cards', params=params, headers=None, proxies=proxies)

        response = requests.post(url, json=params, headers=None, proxies=proxies)

        print(response.json())
        return response
    except Exception as e:
        cprint(f"Error {e}, retry...", 'red')
        time.sleep(3)
        return claim_points(address)
