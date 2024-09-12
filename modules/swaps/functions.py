import datetime

from eth_account.messages import encode_structured_data
from hexbytes import HexBytes

from config.settings import SLIPPAGE
from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from config.settings import *
from helpers.functions import int_to_wei, sleeping, wei_to_int, get_min_balance, api_call

from modules.swaps.config import *
from eth_abi import encode, abi
from time import time




def open_ocean(web3, private_key, _amount, from_token, to_token):
    chain = 'scroll'
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
    min_balance = get_min_balance(chain)
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
            "slippage": SLIPPAGE,
            "account": wallet,
        }

        # if USE_REF:
        # params.update({
        #     "referrer": Web3.to_checksum_address("0x28faD3430EcA42e3F89eD585eB10ceB9be35f7b9"),
        #     "referrerFee": 0.03
        # })

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
    url = "https://open-api.openocean.finance/v3/534352/swap_quote"

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


def xy_swap(web3, private_key, _amount, from_token, to_token):
    chain = 'scroll'
    wallet = web3.eth.account.from_key(private_key).address

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
        min_transaction_amount = int_to_wei(0.0000001, decimals)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    cprint(f'/-- Start app.xy.finance swap for {symbol} wallet {wallet} -->', 'green')

    if to_token == '':
        to_token = NATIVE_TOKEN_ADDRESS
    if from_token == '':
        from_token = NATIVE_TOKEN_ADDRESS

    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)
    amount = 0
    if not _amount:
        if from_token == NATIVE_TOKEN_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == NATIVE_TOKEN_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        # Check and approve token
        if from_token != NATIVE_TOKEN_ADDRESS:
            allowance_amount = check_allowance(web3, from_token, wallet, XYSWAP_CONTRACT)
            if amount > allowance_amount:
                cprint(f'/-- Approve token', 'green')
                approve_token(web3, private_key, chain, from_token, XYSWAP_CONTRACT)
                sleeping(5, 8)

        params = {
            "srcChainId": web3.eth.chain_id,
            "srcQuoteTokenAddress": from_token,
            "srcQuoteTokenAmount": amount,
            "dstChainId": web3.eth.chain_id,
            "dstQuoteTokenAddress": to_token,
            "slippage": SLIPPAGE,
            "receiver": wallet,

        }

        response = xy_request(params)
        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'to': response['tx']['to'],
            'data': response['tx']['data'],
            'value': response['tx']['value'],
            'chainId': web3.eth.chain_id

        }
        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash


def xy_request(params, retry=0):
    proxies = get_random_proxy()
    url_qt = "https://aggregator-api.xy.finance/v1/quote"

    response_req = requests.get(url=url_qt, params=params, proxies=proxies)
    if response_req.status_code == 200:
        response = response_req.json()
        if 'routes' in response:
            provider = response["routes"][0]["srcSwapDescription"]["provider"]
            url = "https://aggregator-api.xy.finance/v1/buildTx"
            params.update({
                "affiliate": "0x28faD3430EcA42e3F89eD585eB10ceB9be35f7b9",
                "commissionRate": 300,
                "srcSwapProvider": provider
            })
            response = requests.get(url=url, params=params, proxies=proxies)

            if response.status_code == 200:
                return response.json()

    if retry < MAX_RETRIES:
        cprint(f'error: status code {response_req.status_code}, retry...', 'red')
        return xy_request(params, retry + 1)
    else:
        raise Exception(f'SKIP. Responce error')


def swap_token_syncswap(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(SYNCSWAP_CONTRACTS['router'])
    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Start SyncSwap swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = WETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = WETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
    else:
        amount = int_to_wei(_amount, decimals)


    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)
    pool_address = get_syncswap_pool(web3, from_token, to_token)
    min_amount_out = get_min_amount_out(web3, pool_address, from_token, amount, wallet)

    _, decimals2, symbol2 = check_data_token(web3, to_token)
    cprint(f'/-- Swap: {wei_to_int(amount, decimals)} {symbol} to {symbol2}', 'green')
    price_impact_defender(symbol, symbol2, wei_to_int(amount, decimals), wei_to_int(min_amount_out, decimals2))

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        contract = web3.eth.contract(address=address_contract, abi=SYNCSWAP_ABI['router'])

        # check and approve not native token
        if from_token != WETH_ADDRESS:
            allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
            if amount > allowance_amount:
                cprint(f'/-- Approve token: {symbol}', 'green')
                approve_token(web3, private_key, chain, from_token, address_contract)
                sleeping(5, 10)

        value = 0
        token_in = from_token
        if from_token == WETH_ADDRESS:
            value = amount
            token_in = NULL_TOKEN_ADDRESS

        withdraw_mode = 2

        if to_token == WETH_ADDRESS:
            withdraw_mode = 1

        swap_data = encode(['address', 'address', 'uint8'], [
            from_token, wallet, withdraw_mode
        ])

        steps = [
             pool_address,
             web3.to_hex(swap_data),
             NULL_TOKEN_ADDRESS,
             '0x',
        ]



        path = [
             [steps],
             token_in,
             amount
        ]




        deadline = int(time()) + 1800


        if from_token == WETH_ADDRESS or to_token == WETH_ADDRESS:
            contract_txn = contract.functions.swap(
                [path],
                min_amount_out,
                deadline
            )

        else:
            sign_permission(web3, private_key, from_token)
            contract_txn = contract.functions.swap(
                [path],
                min_amount_out,
                deadline
            )

        contract_txn = contract_txn.build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': value if from_token == WETH_ADDRESS else 0,
                'gasPrice': 0,
                'gas': 0,
            }
        )

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)

        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash






def get_syncswap_pool(web3, from_token, to_token):
    if from_token==WETH_ADDRESS or to_token==WETH_ADDRESS:
        contract_address=SYNCSWAP_CONTRACTS["classic_pool"]
    else:
        contract_address=SYNCSWAP_CONTRACTS["stable_pool"]

    pool_contract = web3.eth.contract(address=contract_address, abi=SYNCSWAP_ABI['classic_pool_factory'])
    return pool_contract.functions.getPool(
        from_token,
        to_token
    ).call()

def sign_permission(web3, private_key, from_token):
    address = web3.eth.account.from_key(private_key).address

    token_contract, decimals, token_name = check_data_token(web3, from_token)
    token_data= {
        'USDT': ("Tether USD", 1),
        'USDC': ("USD Coin", 2)
    }
    domain, version=token_data[token_name]

    deadline =int(time()) + 1800


    sign_data = {
        "types": {
            "Permit": [
                {
                    "name": "owner",
                    "type": "address"
                },
                {
                    "name": "spender",
                    "type": "address"
                },
                {
                    "name": "value",
                    "type": "uint256"
                },
                {
                    "name": "nonce",
                    "type": "uint256"
                },
                {
                    "name": "deadline",
                    "type": "uint256"
                }
            ],
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "version",
                    "type": "string"
                },
                {
                    "name": "chainId",
                    "type": "uint256"
                },
                {
                    "name": "verifyingContract",
                    "type": "address"
                }
            ]
        },
        "domain": {
            "name": domain,
            "version": f"{version}",
            "chainId": web3.eth.chain_id,
            "verifyingContract": from_token
        },
        "primaryType": "Permit",
        "message": {
            "owner": address,
            "spender": SYNCSWAP_CONTRACTS['router'],
            "value": 2 ** 256 - 1,
            "nonce": 0,
            "deadline": deadline
        }
    }
    data_encoded = encode_structured_data(sign_data)
    sing_data = web3.eth.account.sign_message(data_encoded,private_key=private_key)

    return deadline, sing_data.v, hex(sing_data.r), hex(sing_data.s)




def get_min_amount_out(web3, pool_address, token_address, amount, wallet):
    pool_contract = web3.eth.contract(pool_address, abi=SYNCSWAP_ABI['classic_pool'])

    min_amount_out = pool_contract.functions.getAmountOut(
        token_address,
        amount,
        wallet
    ).call()

    return int(min_amount_out - (min_amount_out / 100 * SLIPPAGE))


def get_min_amount_out_zb(contract, from_token, to_token, amount):
    min_amount_out = contract.functions.getAmountsOut(
        amount,
        [
            from_token,
            to_token
        ]
    ).call()
    return int(min_amount_out[1] - (min_amount_out[1] / 100 * SLIPPAGE))



def swap_token_zebra(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(ZEBRA_CONTRACTS['router'])
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=ZEBRA_ABI)

    cprint(f'/-- Start Zebra swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = WETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = WETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')

    # check and approve not native token
    if from_token != WETH_ADDRESS:
        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: {symbol}', 'green')
            approve_token(web3, private_key, chain, from_token, address_contract)
            sleeping(5, 10)



    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)
    min_amount_out = get_min_amount_out_zb(contract, from_token, to_token, amount)

    _, decimals2, symbol2 = check_data_token(web3, to_token)
    cprint(f'/-- Swap: {wei_to_int(amount, decimals)} {symbol} to {symbol2}', 'green')
    price_impact_defender(symbol, symbol2, wei_to_int(amount, decimals), wei_to_int(min_amount_out, decimals2))

    deadline = int(time()+ 60 * 60 * 2)

    params=(
        min_amount_out,
        [
            from_token,
            to_token,
        ],
        wallet,
        deadline
    )



    if from_token == WETH_ADDRESS:
        contract_txn = contract.functions.swapExactETHForTokens(
            *params
        )
    elif to_token==WETH_ADDRESS:
        contract_txn = contract.functions.swapExactTokensForETH(
            amount,
            *params
        )
    else:
        contract_txn = contract.functions.swapExactTokensForTokens(
            amount,
            *params
        )

    contract_txn = contract_txn.build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': amount if from_token == WETH_ADDRESS else 0,
            'gasPrice': 0,
            'gas': 0,
        }
    )

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)

    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def swap_token_skydrome(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(SKYDROME_CONTRACTS['router'])
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=SKYDROME_ABI)

    cprint(f'/-- Start SKYDROME swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = WETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = WETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            # amount = balance * 0.999999
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

    # check and approve not native token
    if from_token != WETH_ADDRESS:
        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: {symbol}', 'green')
            approve_token(web3, private_key, chain, from_token, address_contract)
            sleeping(5, 10)



    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)
    min_amount_out,swap_type = get_min_amount_out_sd(contract, from_token, to_token, amount)

    _, decimals2, symbol2 = check_data_token(web3, to_token)
    cprint(f'/-- Swap: {wei_to_int(amount, decimals)} {symbol} to {symbol2}', 'green')
    price_impact_defender(symbol, symbol2, wei_to_int(amount, decimals), wei_to_int(min_amount_out, decimals2))

    ct = datetime.datetime.now()
    deadline = int(ct.timestamp()) + 60 * 60 * 2

    params = (
        min_amount_out,
        [[
            from_token,
            to_token,
            swap_type
        ]],
        wallet,
        deadline
    )

    if from_token == WETH_ADDRESS:
        contract_txn = contract.functions.swapExactETHForTokens(
            *params
        )
    elif to_token == WETH_ADDRESS:
        contract_txn = contract.functions.swapExactTokensForETH(
            amount,
            *params
        )
    else:
        contract_txn = contract.functions.swapExactTokensForTokens(
            amount,
            *params
        )

    contract_txn = contract_txn.build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': amount if from_token == WETH_ADDRESS else 0,
            'gasPrice': 0,
            'gas': 0,
        }
    )

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)

    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def get_min_amount_out_sd(contract, from_token, to_token, amount):
    min_amount_out,swap_type = contract.functions.getAmountOut(
        amount,
        from_token,
        to_token

    ).call()
    return int(min_amount_out - (min_amount_out / 100 * SLIPPAGE)),swap_type



def swap_ambient(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(AMBIENT_CONTRACT['router'])
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=AMBIENT_ABI)
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)


    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = WETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    cprint(f'/-- Start Ambient swap for wallet {wallet} {symbol} -->', 'green')

    if to_token == '':
        to_token = WETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')

    # check and approve not native token
    if from_token != WETH_ADDRESS:
        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: {symbol}', 'green')
            approve_token(web3, private_key, chain, from_token, address_contract)
            sleeping(5, 10)



    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)


    min_amount_out=get_min_amount_out_amb(web3,from_token,to_token,amount)

    _, decimals2, symbol2 = check_data_token(web3, to_token)
    cprint(f'/-- Swap: {wei_to_int(amount, decimals)} {symbol} to {symbol2}', 'green')
    price_impact_defender(symbol, symbol2, wei_to_int(amount, decimals), wei_to_int(min_amount_out, decimals2))

    pool_idx = 420
    reserve_flags = 0
    tip = 0
    is_buy=True
    limit_price = 21267430153580247136652501917186561137

    #from ETH
    if from_token == WETH_ADDRESS:
        base=NULL_TOKEN_ADDRESS
        quote=to_token
    #TO ETH
    elif to_token==WETH_ADDRESS:
        base =NULL_TOKEN_ADDRESS
        quote=from_token
        is_buy=False
        limit_price=65537
    #Stable
    else:
        base=from_token
        quote=to_token




    encode_data = abi.encode(
        ['address', 'address', 'uint16', 'bool', 'bool', 'uint256', 'uint8', 'uint256', 'uint256', 'uint8'], [
            base,
            quote,
            pool_idx,
            is_buy,
            is_buy,
            amount,
            tip,
            limit_price,
            min_amount_out,
            reserve_flags
        ]
    )


    contract_txn = contract.functions.userCmd(
        1,
        encode_data
    )

    contract_txn = contract_txn.build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': amount if from_token==WETH_ADDRESS else 0,
            'gasPrice': 0,
            'gas': 0,
        }
    )

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)

    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash

def get_min_amount_out_amb(web3,from_token, to_token, from_token_amount):
    token_contract1, decimals1, symbol1 = check_data_token(web3, from_token)
    token_contract2, decimals2, symbol2 = check_data_token(web3, to_token)
    prices=all_prices()

    from_price = float(price_token(prices, symbol1))
    to_price = float(price_token(prices, symbol2))

    amount_in_usd=from_price*wei_to_int(from_token_amount,decimals1)

    min_amount_out = (amount_in_usd / to_price)

    min_amount_out_in_wei =int_to_wei(min_amount_out,decimals2)

    return int(min_amount_out_in_wei - (min_amount_out_in_wei / 100 * SLIPPAGE))



def swap_izumi(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(IZUMI_CONTRACTS['router'])
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=IZUMI_ABI['router'])
    quoter_contract = web3.eth.contract(address=IZUMI_CONTRACTS['quoter'], abi=IZUMI_ABI['quoter'])

    cprint(f'/-- Start Izumi swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = WETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = WETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == WETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')

    # check and approve not native token
    if from_token != WETH_ADDRESS:
        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: {symbol}', 'green')
            approve_token(web3, private_key, chain, from_token, address_contract)
            sleeping(5, 10)



    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)
    ct = datetime.datetime.now()
    deadline = int(ct.timestamp()) + 60 * 60 * 2

    path=get_path_izumi(web3,from_token,to_token)
    min_amount_out = get_min_amount_out_iz(quoter_contract, path, amount)

    _, decimals2, symbol2 = check_data_token(web3, to_token)
    cprint(f'/-- Swap: {wei_to_int(amount, decimals)} {symbol} to {symbol2}', 'green')
    price_impact_defender(symbol, symbol2, wei_to_int(amount, decimals), wei_to_int(min_amount_out, decimals2))

    tx_data = contract.encodeABI(
        fn_name='swapAmount',
        args=[(
            path,
            wallet if to_token != WETH_ADDRESS else NULL_TOKEN_ADDRESS,
            amount,
            min_amount_out,
            deadline
        )]
    )

    result=[tx_data]
    tx_additional=[]

    if from_token==WETH_ADDRESS:
        tx_additional = contract.encodeABI(
            fn_name='refundETH',
        )


    elif to_token==WETH_ADDRESS:
        tx_additional = contract.encodeABI(
            fn_name='unwrapWETH9',
            args=[
                0,
                wallet
            ]
        )

    if tx_additional:
        result.append(tx_additional)
    contract_txn = contract.functions.multicall(result).build_transaction(
        {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'value': amount if from_token == WETH_ADDRESS else 0,
            'gasPrice': 0,
            'gas': 0,
        }
    )

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)

    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash



def get_path_izumi(web3,from_token: str, to_token: str):
    token_contract1, decimals1, from_token_name = check_data_token(web3, from_token)
    token_contract2, decimals2, to_token_name = check_data_token(web3, to_token)


    pool_fee_info = {
            "USDC/ETH": 3000,
            "USDT/ETH": 3000,
            "ETH/USDC": 3000,
            "ETH/USDT": 3000,
            "USDC/USDT": 500,
            "USDT/USDC": 500
    }

    # if 'USDT' not in [from_token_name, to_token_name]:
    from_token_bytes = HexBytes(from_token).rjust(20, b'\0')
    to_token_bytes = HexBytes(to_token).rjust(20, b'\0')
    fee_bytes = pool_fee_info[f"{from_token_name}/{to_token_name}"].to_bytes(3, 'big')
    return from_token_bytes + fee_bytes + to_token_bytes


def get_min_amount_out_iz(contract,path,amount):
    min_amount_out, _ = contract.functions.swapAmount(
        amount,
        path
    ).call()

    return int(min_amount_out - (min_amount_out / 100 * SLIPPAGE))


def swap_sushi(web3, private_key, _amount, _from_token, _to_token):
    chain = 'scroll'
    from_token = _from_token
    to_token = _to_token

    address_contract = web3.to_checksum_address(SUSHISWAP_CONTRACTS)
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=address_contract, abi=SUSHISWAP_ABI)

    cprint(f'/-- Start Sushi swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)
    min_balance = get_min_balance(chain)

    # Token
    if from_token != '':
        token_contract, decimals, symbol = check_data_token(web3, from_token)
    else:
        decimals = 18
        symbol = CHAINS[chain]['token']
        from_token = DEFAULT_ETH_ADDRESS
    min_transaction_amount = int_to_wei(MIN_TRANSACTION_AMOUNT, decimals)

    if to_token == '':
        to_token = DEFAULT_ETH_ADDRESS

    # Amount
    amount = 0
    if not _amount:
        if from_token == DEFAULT_ETH_ADDRESS:
            if balance > int_to_wei(min_balance, decimals):
                amount = int(balance - int_to_wei(min_balance, decimals))
        else:
            amount = balance
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount and from_token == DEFAULT_ETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')

    # check and approve not native token
    if from_token != DEFAULT_ETH_ADDRESS:
        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: {symbol}', 'green')
            approve_token(web3, private_key, chain, from_token, address_contract)
            sleeping(5, 10)



    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)




    result = api_call(f"https://api.sushi.com/swap/v4/{web3.eth.chain_id}",{
        'tokenIn':from_token,
        'tokenOut':to_token,
        'amount':amount,
        'maxPriceImpact':'0.005',
        'to':wallet,
        'preferSushi':True,

    })


    if result['routeProcessorArgs']:
        args=result['routeProcessorArgs'];

        contract_txn = contract.functions.processRoute(
            args['tokenIn'],
            int(args['amountIn']),
            args['tokenOut'],
            int(args['amountOutMin']),
            args['to'],
            args['routeCode']



        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': amount if from_token == DEFAULT_ETH_ADDRESS else 0,
                'gasPrice': 0,
                'gas': 0,
            }
        )


    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)


    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def price_impact_defender(from_token_name,to_token_name,from_token_amount,to_token_amount):


    token1_usd = float(price_token(all_prices(), from_token_name))*from_token_amount
    token2_usd = float(price_token(all_prices(), to_token_name))*to_token_amount

    price_impact = 100 - (token2_usd / token1_usd) * 100


    if price_impact > PRICE_IMPACT:
        raise Exception(f'SKIP. Price impact is too high: {price_impact}% > {PRICE_IMPACT}%')


def unwrap_weth(web3, private_key, _amount=0):
    chain = 'scroll'
    from_token = WETH_ADDRESS

    address_contract = web3.to_checksum_address(WETH_ADDRESS)
    contract = web3.eth.contract(address=address_contract, abi=WETH_ABI)

    wallet = web3.eth.account.from_key(private_key).address

    cprint(f'/-- Start SyncSwap swap for wallet {wallet} -->', 'green')
    balance = get_token_balance(web3, wallet, from_token)

    if not balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, 18)} WETH')


    contract_txn = contract.functions.withdraw(
        balance
    )

    contract_txn = contract_txn.build_transaction(
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
