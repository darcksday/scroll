from helpers.web3_helper import *
from config.settings import *
from helpers.functions import int_to_wei, wei_to_int, post_call, get_min_balance
from modules.relay_bridge.config import *


def data_request(from_chain, to_chain, value, wallet):
    url = "https://api.relay.link/execute/bridge"
    params = {
        "amount": str(value),
        "currency": "eth",
        "destinationChainId": CHAINS[to_chain]['chain_id'],
        "originChainId": CHAINS[from_chain]['chain_id'],
        "recipient": wallet,
        "source": "relay.link",
        "useExternalLiquidity": False,
        "usePermit": False,
        "user": wallet,
    }

    return post_call(url, params)


def relay_call(web3, private_key, _amount, from_chain, to_chain):
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Start relay {from_chain} => {to_chain}, wallet {wallet} -->', 'green')

    decimals = 18
    symbol = CHAINS[from_chain]['token']
    min_transaction_amount = int_to_wei(MIN_RELAY_TRANSACTION_AMOUNT, decimals)

    # Amount
    amount = 0
    balance = get_token_balance(web3, wallet, NATIVE_TOKEN_ADDRESS)
    if not _amount:
        min_balance = get_min_balance(from_chain)

        if balance > int_to_wei(min_balance, decimals):
            amount = int(balance - int_to_wei(min_balance, decimals))
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount:
        raise Exception(f'SKIP. Insufficient balance, min balance: {MIN_BALANCE[from_chain]} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        tx_data = data_request(from_chain, to_chain, amount, wallet)

        transaction_data = tx_data['steps'][0]['items'][0]['data']
        gas = transaction_data.get('gas', 0)

        contract_txn = {
            'from': transaction_data['from'],
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': int(transaction_data['value']),
            'gasPrice': 0,
            'gas': gas,
            'to': Web3.to_checksum_address(transaction_data['to']),
            'data': transaction_data['data'],
            'chainId': transaction_data['chainId'],
        }
        contract_txn = add_gas_price(web3, contract_txn, from_chain)
        if gas == 0:
            contract_txn = add_gas_limit(web3, contract_txn, from_chain)

        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
