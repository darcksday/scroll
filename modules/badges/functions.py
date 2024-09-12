import random
import re
import time

import eth_abi
from hexbytes import HexBytes
from loguru import logger
from termcolor import cprint

from config.settings import *
from helpers.functions import api_call, sleeping, int_to_wei
from helpers.settings_helper import get_ref_list
from helpers.web3_helper import  add_gas_price, add_gas_limit, sign_tx, wait_gas, check_status_tx
from modules.badges.config import *
import sys

from modules.functions.config import NFT_ORGINS_ABI, NFT_ORIGINS_CONTRACT

chain='scroll'
CUSTOM_BADGES = [
    {
        'name':'Ethereum Year',
        'baseUrl':'https://canvas.scroll.cat/badge',
        'badgeContract':'0x3dacAd961e5e2de850F5E027c70b56b5Afa5DfeD',
        'description':"Check out the Ethereum Year Badge! It's like a digital trophy that shows off the year your wallet made its debut on Ethereum. It's a little present from Scroll to celebrate all the cool stuff you've done in the Ethereum ecosystem."
    }
]



def claim_canvas_profile(web3, private_key):
    wallet = web3.eth.account.from_key(private_key).address
    contract = web3.eth.contract(address=web3.to_checksum_address(PROFILE_CONTRACT), abi=PROFILE_CONTRACT_ABI)


    if check_minted(web3, private_key):
        logger.info(f'Canvas Profile already minted on {wallet}')
        return
    else:
        name=generate_domain_name(web3)
        signature,ref=get_signature(wallet)


        logger.info(f'Mint canvas name {name} on {wallet} refereal:{ref}')

        contract_txn = contract.functions.mint(name,signature).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': int_to_wei(0.0005,18),
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        sign_tx_one(web3,contract_txn,private_key)



def claim_origin_badge(web3, private_key):
    wallet = web3.eth.account.from_key(private_key).address
    badge_contract = web3.eth.contract(address=web3.to_checksum_address(ORIGIN_CONTRACT), abi=ORIGIN_ABI)
    nft_contract=web3.eth.contract(address=NFT_ORIGINS_CONTRACT, abi=NFT_ORGINS_ABI)
    badge_claim_contract=web3.eth.contract(address=ORIGIN_BADGE_CLAIM_CT, abi=ORIGIN_BADGE_CLAIM_ABI)

    if badge_contract.functions.hasBadge(wallet).call():
        logger.info(f'Scroll Canvas  Origins NFT badge is already claimed | {wallet}')

    elif nft_contract.functions.minted(wallet).call():
        logger.success(f'Claim  Scroll Origins NFT  badge | {wallet}')

        nft_id = nft_contract.functions.tokenOfOwnerByIndex(
            wallet,
            0
        ).call()

        data = eth_abi.encode(
            ['address', 'uint256', 'uint256', 'address', 'uint256'],
            [
                badge_contract.address,
                0x40,
                0x40,
                nft_contract.address,
                nft_id
            ]
        )

        contract_txn = badge_claim_contract.functions.attest(
                (
                    HexBytes('0xd57de4f41c3d3cc855eadef68f98c0d4edd22d57161d96b7c06d2f4336cc3b49'),
                    (
                        wallet,
                        0,
                        False,
                        HexBytes(f'0x{"00" * 32}'),
                        data,
                        0
                    )
                )
            ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': 0,
                'gasPrice': 0,
                'gas': 0,
            })

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        sign_tx_one(web3,contract_txn,private_key)



def check_minted(web3,private_key):
    wallet = web3.eth.account.from_key(private_key).address

    contract = web3.eth.contract(address=web3.to_checksum_address(PROFILE_CONTRACT), abi=PROFILE_CONTRACT_ABI)
    getprofile = contract.functions.getProfile(wallet).call()
    is_claimed = contract.functions.isProfileMinted(getprofile).call()
    return is_claimed


def get_signature(wallet):
    ref_list=get_ref_list()
    ref=random.choice(ref_list)


    headers = {
        "Host": "canvas.scroll.cat",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "Accept-Language": "en-EN",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept": "*/*",
        "Origin": "https://scroll.io",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://scroll.io/",
        "Priority": "u=1, i"
    }
    url=f"https://canvas.scroll.cat/code/{ref}/sig/{wallet}"

    result=api_call(url,[],headers)
    signature=result.get('signature')

    return signature,ref


def generate_domain_name(web3):
    url=f"https://randomuser.me/api"
    contract = web3.eth.contract(address=web3.to_checksum_address(PROFILE_CONTRACT), abi=PROFILE_CONTRACT_ABI)


    while True:
        result=api_call(url)
        if result:
            username = result['results'][0]['login']['username']
            is_used=contract.functions.isUsernameUsed(username).call()
            is_valid= re.match(r'^[A-Za-z0-9_]{4,15}$', username)
            if not is_used and is_valid:
                return username






def claim_custom_badges(web3, private_key):
    wallet = web3.eth.account.from_key(private_key).address
    available_badges=get_eligible_badges(web3,wallet)

    for badge in available_badges:
        logger.info(f'Mint {badge["name"]} badge')
        contract_txn = {
            'from': wallet,
            'nonce': web3.eth.get_transaction_count(wallet),
            'gasPrice': 0,
            'gas': 0,
            'to': web3.to_checksum_address(badge['tx']['to']),
            'data': badge['tx']['data'],
            'chainId': web3.eth.chain_id
        }

        contract_txn = add_gas_price(web3, contract_txn, chain)
        contract_txn = add_gas_limit(web3, contract_txn, chain)
        sign_tx_one(web3,contract_txn,private_key)







def get_eligible_badges(web3, wallet):
    logger.info(f'Get eligible badges  on {wallet}')
    url='https://raw.githubusercontent.com/scroll-tech/canvas-badges/main/scroll.badgelist.json'
    response=api_call(url)

    badges=response['badges']

    badges=list(filter(lambda badge: 'baseUrl' in badge, badges))


    badges=CUSTOM_BADGES+badges

    available_badges=[]
    for badge in badges:
        badge_contract = web3.eth.contract(address=web3.to_checksum_address(badge['badgeContract']), abi=BADGE_ABI)

        if badge_contract.functions.hasBadge(wallet).call():
            logger.info(f'Scroll Canvas {badge["name"]} badge is already claimed ')
            continue


        check_url=f"{badge['baseUrl']}/check"
        params={
            'badge':badge['badgeContract'],
            'recipient':wallet
        }
        badge_response=api_call(check_url,params)


        if badge_response and badge_response['code']:
            claim_url=f"{badge['baseUrl']}/claim"
            claim_response = api_call(claim_url, params)

            if claim_response and claim_response['code']:
                badge['tx']=claim_response['tx']
                available_badges.append(badge)
                logger.success(f'Scroll Canvas {badge["name"]} badge eligible for claim ')
        else:
            logger.info(f'Scroll Canvas {badge["name"]} badge not eligible for claim ')

        # time.sleep(1)

    return  available_badges


def sign_tx_one(web3,txdata, private_key,repeat=0):
    if CHECK_GWEI:
        wait_gas()

    try:
        tx_hash = sign_tx(web3, txdata, private_key)
        if tx_hash:
            tx_link = f'{CHAINS[chain]["scan"]}/{tx_hash}'
            time.sleep(2)
            status = check_status_tx(web3, chain, tx_hash)
            if status == 1:
                logger.success(f'{STR_DONE} {chain} transaction: {tx_link}')
            else:
                raise Exception(f'{chain} transaction failed: {tx_link}')
            sleeping(MIN_SLEEP, MAX_SLEEP)

    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        err_formated = f'{str(error)}. {exc_tb.tb_frame.f_code.co_filename}, line: {exc_tb.tb_lineno}'
        logger.error(err_formated)

        if repeat < MAX_RETRIES:
            time.sleep(10)
            return sign_tx_one(web3,txdata, private_key,repeat+1)
        else:
            raise Exception(f'{chain} Repeat limit exceeded')