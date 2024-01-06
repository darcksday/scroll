import csv
from datetime import datetime

from eth_account.messages import encode_defunct
from termcolor import cprint

from config.settings import CHAINS, MAX_RETRIES
from helpers.functions import get_min_balance, int_to_wei, wei_to_int, api_call
from helpers.settings_helper import get_own_contract_address, get_random_proxy
from helpers.web3_helper import get_token_balance, check_data_token, add_gas_price, add_gas_limit, sign_tx
from modules.contracts.config import DEPOSIT_ABI, STAKE_ABI

chain = 'zkfair'


def check(web3, private_key,merkle=False):
    wallet = web3.eth.account.from_key(private_key).address

    current_date_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    text_origin = current_date_time + "GET/api/airdrop?address=" + wallet
    message = encode_defunct(text=text_origin)
    text_signature = web3.eth.account.sign_message(message, private_key=private_key)
    signature_value = text_signature.signature.hex()
    url = f"https://airdrop.zkfair.io/api/airdrop?address={wallet}&API-SIGNATURE={signature_value}&TIMESTAMP={current_date_time}"
    headers = {
        "authority": "airdrop.zkfair.io",
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "origin": "https://zkfair.io",
        "referer": "https://zkfair.io/",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    result = api_call(url,[],headers)

    if result['data']:
        data = result['data']

        if merkle:
            url2=f"https://airdrop.zkfair.io/api/airdrop_merkle?address={wallet}&API-SIGNATURE={signature_value}&TIMESTAMP={current_date_time}"
            result2 = api_call(url2, [], headers)
            data2=result2['data']
            return data,data2


        else:
            profit=wei_to_int(int(data['account_profit']),18) if data['account_profit'] else 0
            return {
                'wallet':wallet,
                'account_profit':profit,
                'index':data['index'],
            }


def save_csv(data):
    csv_filename = 'results/zkfair.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)






def claim(web3, private_key, _amount):
    address_contract=web3.to_checksum_address('0x53c390b02339519991897b59eb6d9e0b211eb840')
    wallet = web3.eth.account.from_key(private_key).address


    data, data2 = check(web3,private_key,True)
    cprint(f'/-- Claim rewards on {wallet} amount:{ data["account_profit"]}', 'green')


    if data['account_profit']:
        tx_data = "0xae0b51df" + web3.to_bytes(int(data['index'])).hex().zfill(64) + web3.to_bytes(int(data['account_profit'])).hex().zfill(
            64) + "00000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000014"
        proof_array = [item.replace("0x", "") for item in data2["proof"]]

        tx_data=tx_data+ "".join(proof_array)
        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': 0,
            'to': address_contract,
            'gasPrice': 0,
            'gas': 0,
            'data': tx_data

        }

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash

    else:
        raise Exception(f'SKIP. No airdrop')






