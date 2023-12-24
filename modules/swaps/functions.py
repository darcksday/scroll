from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from config.settings import *
from helpers.functions import int_to_wei, sleeping, wei_to_int, get_min_balance

from modules.swaps.config import *


def swap_token_spacefi(web3, private_key, _amount, _from_token, _to_token):
    chain = 'zksync'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(SPACEFI_CONTRACTS)
    contract = web3.eth.contract(address=address_contract, abi=SPACEFI_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Start spacefi.io swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance=get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
        min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = WETH_ADDRESS
    if from_token == '':
        from_token = WETH_ADDRESS

    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        min_amount = get_min_amounts_out_space(contract, from_token, to_token, amount, 1)

        deadline = int(time.time()) + 1000000

        # check and approve not native token
        if from_token != WETH_ADDRESS:
            allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
            if amount > allowance_amount:
                cprint(f'/-- Approve token: {symbol}', 'green')
                approve_token(web3, private_key, chain, from_token, address_contract)
                sleeping(5, 10)
            contract_txn = contract.functions.swapExactTokensForETH(
                amount,
                min_amount,
                [
                    from_token,
                    to_token,
                ],
                wallet,
                deadline

            ).build_transaction(
                {
                    'from': wallet,
                    'nonce': web3.eth.get_transaction_count(wallet),
                    'value': 0,
                    'gasPrice': 0,
                    'gas': 0,
                })
        else:

            contract_txn = contract.functions.swapExactETHForTokens(
                min_amount,
                [
                    from_token,
                    to_token,
                ],
                wallet,
                deadline
            ).build_transaction(
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

def open_ocean(web3, private_key, _amount, from_token, to_token):
    chain = 'zksync'
    wallet = web3.eth.account.from_key(private_key).address

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
        min_transaction_amount = int_to_wei(0.0000001, decimals)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    cprint(f'/-- Start app.openocean.finance swap for {symbol} wallet {wallet} -->', 'green')

    if to_token == '':
        to_token = NULL_TOKEN_ADDRESS
    if from_token == '':
        from_token = NULL_TOKEN_ADDRESS

    balance = get_token_balance(web3, wallet, from_token)
    min_balance=get_min_balance(chain)
    amount = 0
    if not _amount:
        if from_token == NULL_TOKEN_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == NULL_TOKEN_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        # Check and approve token
        if from_token != NULL_TOKEN_ADDRESS:
            allowance_amount = check_allowance(web3, from_token, wallet, OPENOCEAN_CONTRACT['router'])
            if amount > allowance_amount:
                cprint(f'/-- Approve token', 'green')
                approve_token(web3, private_key, chain, from_token, OPENOCEAN_CONTRACT['router'])
                sleeping(5, 8)

        params = {
            "inTokenAddress": from_token,
            "outTokenAddress": to_token,
            "amount": wei_to_int(amount, decimals),
            "gasPrice": web3.from_wei(web3.eth.gas_price, "gwei"),
            "slippage": 1,
            "account": wallet,
        }

        if USE_REF:
            params.update({
                "referrer": Web3.to_checksum_address("0x28faD3430EcA42e3F89eD585eB10ceB9be35f7b9"),
                "referrerFee": 0.01
            })

        response = ocean_request(params)

        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'to': response['data']['to'],
            'data': response['data']['data'],
            'value': int(response['data']['value']),
            'chainId': web3.eth.chain_id

        }
        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


def ocean_request(params, retry=0):
    proxies = get_random_proxy()
    url = "https://open-api.openocean.finance/v3/324/swap_quote"

    response_req = requests.get(url=url, params=params, proxies=proxies)
    if response_req.status_code == 200:
        response = response_req.json()
        if 'data' in response and response['data'] and 'to' in response['data']:
            return response

    if retry < MAX_RETRIES:
        cprint(f'error: status code {response_req.status_code}, retry...', 'red')
        return ocean_request(params, retry + 1)
    else:
        raise Exception(f'SKIP. Responce error')


def get_min_amounts_out_space(contract, from_token: str, to_token: str, amount: int, slippage: float):
    min_amount_out = contract.functions.getAmountsOut(
        amount,
        [
            from_token,
            to_token
        ]
    ).call()
    return int(min_amount_out[1] - (min_amount_out[1] / 100 * slippage))


def mint_origin_nft(web3, private_key, _amount=0):
    chain = 'scroll'
    address_contract = web3.to_checksum_address(NFT_ORIGINS_CONTRACT)
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Wallet {wallet} --> Mint Origin NFT', 'green')

    params={'address':wallet}
    metadata, proof = origin_nft_request(params)

    cprint(f'/-- Rarity {int(metadata.get("rarityData", 0), 16)} ', 'blue')


    contract = web3.eth.contract(address=address_contract, abi=NFT_ORGINS_ABI)
    contract_txn = contract.functions.mint(
        wallet,
        (
            metadata.get("deployer"),
            metadata.get("firstDeployedContract"),
            metadata.get("bestDeployedContract"),
            int(metadata.get("rarityData", 0), 16),
        ),
        proof


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


def origin_nft_request(params, retry=0):
    proxies = get_random_proxy()
    url = f"https://nft.scroll.io/p/{params['address']}.json"

    response_req = requests.get(url=url, params=[], proxies=proxies)
    if response_req.status_code == 200:
        response = response_req.json()
        if 'metadata' in response:
            return response["metadata"], response["proof"]

    if retry < MAX_RETRIES:
        cprint(f'error: status code {response_req.status_code}, retry...', 'red')
        return origin_nft_request(params, retry + 1)
    else:
        raise Exception(f'SKIP. Responce error')
