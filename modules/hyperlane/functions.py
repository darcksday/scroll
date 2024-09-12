import decimal
import time

from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from modules.hyperlane.config import *
from helpers.functions import int_to_wei, get_min_balance, api_call
from modules.transfer.functions import map_recipients

def hyperlane_eth_bridge(web3, private_key: str, _amount: float, from_chain: str, to_chain: str):
    account = web3.eth.account.from_key(private_key)
    wallet = account.address
    address_contract = web3.to_checksum_address(HYPERLANE_CONTRACTS[from_chain])
    bridge_contract = web3.eth.contract(address=address_contract, abi=HYPERLANE_ABI)
    to_chain_domain = int(HYPERLANE_DOMAINS[to_chain])

    cprint(f'/-- Hypelane ETH Bridge: {from_chain} => {to_chain} for {wallet} -->', 'green')

    balance = 0
    if not _amount:
        balance = get_token_balance(web3, wallet, '', True)

    min_balance = get_min_balance(from_chain)

    if balance > min_balance:
        amount = balance - min_balance
        cprint(f'/-- Amount: {amount} ETH', 'green')
    else:
        amount = _amount


    if amount > HYPERLANE_MIN_AMOUNT and amount < HYPERLANE_MAX_AMOUNT:
        amount_wei = int(web3.to_wei(amount, 'ether'))
        chain_id = web3.eth.chain_id
        nonce = web3.eth.get_transaction_count(wallet)
        fee = bridge_contract.functions.quoteBridge(to_chain_domain, amount_wei).call()
        total_amount = amount_wei + fee

        contract_txn = bridge_contract.functions.bridgeETH(to_chain_domain, amount_wei).build_transaction({
            'nonce': nonce,
            'from': wallet,
            'value': total_amount,
            'gasPrice': 0,
        })

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(
            f'{STR_CANCEL} Can\'t bridge: amount less than minimal ({HYPERLANE_MAX_AMOUNT} < {amount} < {HYPERLANE_MIN_AMOUNT}), skip.')

