import datetime

from config_sample.settings import SLIPPAGE
from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from config.settings import *
from helpers.functions import int_to_wei, sleeping, wei_to_int, get_min_balance

from modules.swaps.config import *
from eth_abi import encode




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
        params.update({
            "referrer": Web3.to_checksum_address("0x28faD3430EcA42e3F89eD585eB10ceB9be35f7b9"),
            "referrerFee": 0.03
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
            # amount = balance * 0.999999
            amount = balance
        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
    else:
        amount = int_to_wei(_amount, decimals)

    from_token = web3.to_checksum_address(from_token)
    to_token = web3.to_checksum_address(to_token)
    pool_address = get_syncswap_pool(web3, from_token, to_token)
    min_amount_out = get_min_amount_out(web3, pool_address, from_token, amount, wallet)

    if not amount and from_token == WETH_ADDRESS:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    elif amount < min_transaction_amount:
        raise Exception(f'SKIP. Min transaction amount: {wei_to_int(min_transaction_amount, decimals)} {symbol}')
    else:
        contract = web3.eth.contract(address=address_contract, abi=ABI_SYNC_SWAP)

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

        swap_data = encode(['address', 'address', 'uint8'], [
            from_token, wallet, 1
        ])

        steps = [{
            'pool': pool_address,
            'data': swap_data,
            'callback': NULL_TOKEN_ADDRESS,
            'callbackData': b''
        }]

        path = [{
            'steps': steps,
            'tokenIn': token_in,
            'amountIn': amount
        }]

        ct = datetime.datetime.now()
        deadline = int(ct.timestamp()) + 60 * 60 * 2

        contract_txn = contract.functions.swap(
            path,
            min_amount_out,
            deadline
        ).build_transaction(
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
    pool_contract = web3.eth.contract(address=SYNCSWAP_CONTRACTS["classic_pool"], abi=SYNCSWAP_CLASSIC_POOL_ABI)

    return pool_contract.functions.getPool(
        from_token,
        to_token
    ).call()


def get_min_amount_out(web3, pool_address, token_address, amount, wallet):
    pool_contract = web3.eth.contract(pool_address, abi=SYNCSWAP_CLASSIC_POOL_DATA_ABI)

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
    min_amount_out = get_min_amount_out_zb(contract, from_token, to_token, amount)
    ct = datetime.datetime.now()
    deadline = int(ct.timestamp()) + 60 * 60 * 2

    if from_token == WETH_ADDRESS:
        contract_txn = contract.functions.swapExactETHForTokens(
            min_amount_out,
            [
                from_token,
                to_token,
            ],
            wallet,
            deadline
        )
    else:
        contract_txn = contract.functions.swapExactTokensForETH(
            amount,
            min_amount_out,
            [
                from_token,
                to_token,
            ],
            wallet,
            deadline
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
    ct = datetime.datetime.now()
    deadline = int(ct.timestamp()) + 60 * 60 * 2

    if from_token == WETH_ADDRESS:
        contract_txn = contract.functions.swapExactETHForTokens(
            min_amount_out,
            [[
                from_token,
                to_token,
                swap_type
            ]],
            wallet,
            deadline
        )
    else:
        contract_txn = contract.functions.swapExactTokensForETH(
            amount,
            min_amount_out,
            [[
                from_token,
                to_token,
                swap_type
            ]],
            wallet,
            deadline
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
