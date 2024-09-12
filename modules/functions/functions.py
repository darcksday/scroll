from random import random

from faker import Faker
from termcolor import cprint

from helpers.functions import get_min_balance
from helpers.settings_helper import get_random_proxy
from helpers.web3_helper import *
from modules.functions.config import *


def send_email(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(DMAIL_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=DMAIL_ABI)
    wallet = web3.eth.account.from_key(private_key).address
    email = generate_email()

    data = contract.encodeABI('send_mail', args=(email, email))

    cprint(f'/-- Wallet {wallet} -->', 'green')

    contract_txn = {
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'gasPrice': 0,
        'gas': 0,
        'to': address_contract,
        'data': data,
        'chainId': web3.eth.chain_id
    }

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id, 1)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def rubyscore(web3, private_key, value=0):
    chain_id = 'scroll'
    address_contract = web3.to_checksum_address(RUBYSCORE_VOTE_CONTRACT)
    contract = web3.eth.contract(address=address_contract, abi=RUBYSCORE_VOTE_ABI)
    wallet = web3.eth.account.from_key(private_key).address


    cprint(f'/-- Wallet {wallet} Rubyscore -->', 'green')

    contract_txn = contract.functions.vote().build_transaction({
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'gasPrice': 0,
        'gas': 0,
    })

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def generate_email():
    domain_list = ["@gmail.com", "@dmail.ai", '@ukr.net']

    domain_address = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(7, 15)))

    return domain_address + random.choice(domain_list)


def safe_create(web3, private_key, value=0):
    chain = 'scroll'
    address_contract = web3.to_checksum_address(SAFE_CONTRACT)
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Wallet {wallet}  create Safe', 'green')

    contract = web3.eth.contract(address=address_contract, abi=SAFE_ABI)

    bytes_data = contract.encodeABI(
        fn_name="setup",
        args=[
            [wallet],
            1,
            NULL_TOKEN_ADDRESS,
            "0x",
            web3.to_checksum_address("0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4"),
            NULL_TOKEN_ADDRESS,
            0,
            NULL_TOKEN_ADDRESS
        ]
    )

    contract_txn = contract.functions.createProxyWithNonce(
        web3.to_checksum_address("0x3E5c63644E683549055b9Be8653de26E0B4CD36E"),
        bytes_data,
        int(time.time() * 1000)
    ).build_transaction({
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'gasPrice': 0,
        'gas': 0,
    })

    contract_txn = add_gas_price(web3, contract_txn, chain)
    contract_txn = add_gas_limit(web3, contract_txn, chain)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def mint_nfts2_me(web3, private_key, _amount, chain_id='scroll', contract_address=''):
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Mint NFT, wallet {wallet} -->', 'green')

    if not _amount:
        _amount = 0.0001

    amount = int_to_wei(_amount, 18)
    contract_txn = {
        "chainId": web3.eth.chain_id,
        "from": wallet,
        "to": contract_address,
        "nonce": web3.eth.get_transaction_count(wallet),
        'gasPrice': 0,
        'gas': 0,
        "value": amount,
        "data": "0x1249c58b"
    }

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)

    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def mint_zkstars(web3, private_key, _amount):
    chain_id = 'scroll'
    contracts = [
        "0x609c2f307940b8f52190b6d3d3a41c762136884e",
        "0x16c0baa8a2aa77fab8d0aece9b6947ee1b74b943",
        "0xc5471e35533e887f59df7a31f7c162eb98f367f7",
        "0xf861f5927c87bc7c4781817b08151d638de41036",
        "0x954e8ac11c369ef69636239803a36146bf85e61b",
        "0xa576ac0a158ebdcc0445e3465adf50e93dd2cad8",
        "0x17863384c663c5f95e4e52d3601f2ff1919ac1aa",
        "0x4c2656a6d1c0ecac86f5024e60d4f04dbb3d1623",
        "0x4e86532cedf07c7946e238bd32ba141b4ed10c12",
        "0x6b9db0ffcb840c3d9119b4ff00f0795602c96086",
        "0x10d4749bee6a1576ae5e11227bc7f5031ad351e4",
        "0x373148e566e4c4c14f4ed8334aba3a0da645097a",
        "0xdacbac1c25d63b4b2b8bfdbf21c383e3ccff2281",
        "0x2394b22b3925342f3216360b7b8f43402e6a150b",
        "0xf34f431e3fc0ad0d2beb914637b39f1ecf46c1ee",
        "0x6f1e292302dce99e2a4681be4370d349850ac7c2",
        "0xa21fac8b389f1f3717957a6bb7d5ae658122fc82",
        "0x1b499d45e0cc5e5198b8a440f2d949f70e207a5d",
        "0xec9bef17876d67de1f2ec69f9a0e94de647fcc93",
        "0x5e6c493da06221fed0259a49beac09ef750c3de1"
    ]

    contract_address = random.choice(contracts)

    wallet = web3.eth.account.from_key(private_key).address
    address_contract = web3.to_checksum_address(contract_address)

    contract = web3.eth.contract(address=address_contract, abi=ZKSTARS_ABI)

    mint_price = contract.functions.getPrice().call()
    nft_id = contract.functions.name().call()

    cprint(f'/-- Mint ZkStars NFT #{nft_id} , wallet {wallet} -->', 'green')

    contract_txn = contract.functions.safeMint(
        web3.to_checksum_address('0x28faD3430EcA42e3F89eD585eB10ceB9be35f7b9')
    ).build_transaction({
        'from': wallet,
        'nonce': web3.eth.get_transaction_count(wallet),
        'gasPrice': 0,
        'gas': 0,
        "value": mint_price,

    })

    contract_txn = add_gas_price(web3, contract_txn, chain_id)
    contract_txn = add_gas_limit(web3, contract_txn, chain_id)
    tx_hash = sign_tx(web3, contract_txn, private_key)
    return tx_hash


def mint_origin_nft(web3, private_key, _amount=0):
    chain = 'scroll'
    address_contract = web3.to_checksum_address(NFT_ORIGINS_CONTRACT)
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Wallet {wallet} --> Mint Origin NFT', 'green')

    params = {'address': wallet}
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


def generate_collection_name():
    fake = Faker()
    title = fake.word()
    while len(title) > 15 or len(title) <= 5:
        title = fake.word()

    symbol = fake.word()
    while len(symbol) > 6 or len(symbol) <= 3:
        symbol = fake.word()

    return title, symbol


def create_omnisea_collection(web3, private_key, _amount=0):
    chain = 'scroll'
    address_contract = web3.to_checksum_address(OMNISEA_CONTRACT)
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Wallet {wallet} --> Create NFT collection on Omnisea', 'green')

    title, symbol = generate_collection_name()

    contract = web3.eth.contract(address=address_contract, abi=OMNISEA_ABI)
    contract_txn = contract.functions.create([
        title,
        symbol,
        "",
        "",
        0,
        True,
        0,
        int(time.time()) + 1000000]
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


def deposit(web3, private_key, _amount=0):
    chain_id = 'ethereum'
    address_contract = web3.to_checksum_address(BRIDGE_CONTRACTS['deposit'])
    contract = web3.eth.contract(address=address_contract, abi=BRIDGE_ABI['deposit'])
    contract_oracle = web3.eth.contract(address=BRIDGE_CONTRACTS['oracle'], abi=BRIDGE_ABI['oracle'])
    wallet = web3.eth.account.from_key(private_key).address
    cprint(f'/-- Wallet {wallet} scroll.io/bridge -->', 'green')


    fee = contract_oracle.functions.estimateCrossDomainMessageFee(168000).call()
    balance = get_token_balance(web3, wallet)
    min_balance = get_min_balance(chain_id)

    decimals = 18
    symbol = CHAINS[chain_id]['token']

    # Amount
    amount = 0
    if not _amount:
        if balance > int_to_wei(min_balance, decimals):
            amount = int(balance - int_to_wei(min_balance, decimals))
    else:
        amount = int_to_wei(_amount, decimals)

    if not amount:
        raise Exception(f'SKIP. Insufficient balance, min balance: {min_balance} {symbol}')
    elif amount > balance:
        raise Exception(f'SKIP. Not enough balance: {wei_to_int(balance, decimals)} {symbol}')
    else:

        cprint(f'/-- Amount: {wei_to_int(amount, decimals)} {symbol}', 'green')
        contract_txn = contract.functions.sendMessage(
            wallet,
            amount,
            '0x',
            168000,
        ).build_transaction({
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'gasPrice': 0,
            'gas': 0,
            'value':int(amount+fee)
        })

        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
