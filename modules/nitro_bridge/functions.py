from helpers.web3_helper import *
from modules.nitro_bridge.config import NITRO_MIN_AMOUNT
from modules.orbiter_bridge.config import *
from helpers.functions import int_to_wei, get_min_balance, api_call, post_call


def nitro_eth_bridge(web3, private_key: str, _amount: float, from_chain: str, to_chain: str):
    account = web3.eth.account.from_key(private_key)
    wallet = web3.to_checksum_address(account.address)

    cprint(f'/-- Nitro ETH Bridge: {from_chain} => {to_chain} for {wallet} -->', 'green')

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
    if amount >= NITRO_MIN_AMOUNT:
        value = int_to_wei(amount, 18)
        chain_id = web3.eth.chain_id
        nonce = web3.eth.get_transaction_count(wallet)


        response = send_request(from_chain,to_chain,value,wallet)

        contract_txn= {
            'chainId': chain_id,
            'nonce': nonce,
            'from': web3.to_checksum_address(response["txn"]["from"]),
            'to': web3.to_checksum_address(response["txn"]["to"]),
            'value': value,
            'gasPrice': 0,
            'data': response["txn"]["data"]
        }

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(
            f'{STR_CANCEL} Can\'t bridge: amount less than minimal ({amount} < {ORBITER_MIN_AMOUNT}), skip.')



def send_request(from_chain,to_chain,value,wallet):
    url = "https://api-beta.pathfinder.routerprotocol.com/api/v2/quote"

    params = {
        "fromTokenAddress": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "toTokenAddress": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "amount": value,
        "fromTokenChainId": CHAINS[from_chain]['chain_id'],
        "toTokenChainId": CHAINS[to_chain]['chain_id'],
        "partnerId": 1
    }
    response = api_call(url, params)
    response.update({"senderAddress": wallet, "receiverAddress": wallet})

    tx_url = "https://api-beta.pathfinder.routerprotocol.com/api/v2/transaction"
    tx_data = post_call(tx_url, response)
    return  tx_data