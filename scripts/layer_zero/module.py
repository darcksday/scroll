import random
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import check_wait_web3_balance
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.run_layer_zero.config import *
from modules.run_layer_zero.functions import stargate_bridge_usdv, stargate_send_usdv
from modules.transfer.functions import map_recipients, transfer
from web3 import Web3
from scripts.functions import *
from config.lz_config  import *


def script_usdv_layer_zero():
    cprint("/-- Start USDV process -->", "blue")

    recipients = get_recipients('bitget_address')
    private_keys = get_private_keys()

    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    bitget_usdt = get_bitget_token_balance('USDT')
    if bitget_usdt < LZ_SCRIPT_USDT_AMOUNT:
        cprint(f"Not enough USDT on Bitget, need at least {LZ_SCRIPT_USDT_AMOUNT} USDT", "red")

    recipient_map = map_recipients(recipients, private_keys)
    web3_bsc = Web3(Web3.HTTPProvider(CHAINS['bsc']['rpc']))
    web3_arbitrum = Web3(Web3.HTTPProvider(CHAINS['arbitrum']['rpc']))
    try:
        wallet_num = 0
        for item in private_keys:
            wallet_num += 1
            private_key = item['private_key']

            run_usdv_one_wallet(web3_bsc, web3_arbitrum, private_key, recipient_map[private_key], wallet_num)
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def run_usdv_one_wallet(web3_bsc, web3_arbitrum, private_key, recipient_wallet, wallet_num):
    web3_polygon = Web3(Web3.HTTPProvider(CHAINS['avalanche']['rpc']))

    amount = round(LZ_SCRIPT_USDT_AMOUNT - random.uniform(0, 10), 2)
    # ------------------ Withdraw ------------------
    wallet_address = web3_bsc.eth.account.from_key(private_key).address
    cprint(f"/-- Withdraw {amount} USDT from bitget to wallet: {wallet_address} [{wallet_num}]", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.8, 2), 'USDT', 'ArbitrumOne', 'bitget')

    sleeping(MIN_SLEEP, MAX_SLEEP)

    # ------------------ Check Arbitrum balance ------------------
    check_wait_web3_balance(web3_arbitrum, 'arbitrum', wallet_address, ARB_USDT_ADDRESS, amount*0.97)

    sleeping(2, 3)

    params = ['arbitrum', 'avalanche', ARB_USDT_ADDRESS]

    run_script_one(stargate_bridge_usdv, private_key, 'arbitrum', 0, params)


    # ------------------ Check avalanche balance ------------------
    amount = check_wait_web3_balance(web3_polygon, 'avalanche', wallet_address, USDV_TOKEN_ADDRESS['avalanche'], amount)
    sleeping(2, 3)

    params = ['avalanche', 'bsc', USDV_TOKEN_ADDRESS['avalanche']]

    run_script_one(stargate_send_usdv, private_key, 'avalanche', 0, params)

    amount = check_wait_web3_balance(web3_bsc, 'BSC', wallet_address, USDV_TOKEN_ADDRESS['bsc'], amount)
    sleeping(2, 3)


    # ------------------ Withdraw to Bitget ------------------
    cprint("/-- Withdraw to Bitget", "blue")

    transfer(web3_bsc, private_key, recipient_wallet, 'bsc', USDV_TOKEN_ADDRESS['bsc'], 0)

    sleeping(MIN_SLEEP, MAX_SLEEP)

    while True:
        sleeping(MIN_SLEEP * 2, MAX_SLEEP * 2)
        cprint("/-- Check Bitget USDV balance", "blue")
        bitget_usdv = get_bitget_token_balance('USDV')
        if bitget_usdv >= amount:
            cprint(f"/-- {bitget_usdv} USDV found, continue...", "green")
            break

    cprint(f"/-- {bitget_usdv} Create sell order USDV/USDT amount:{bitget_usdv} price:{USDV_LIMI_PRICE}", "blue")

    symbol = 'USDVUSDT_SPBL'
    order_info = sell_token(symbol, USDV_LIMI_PRICE, bitget_usdv)

    while True:
        cprint(f"/-- {bitget_usdv} Check order status ", "blue")
        order_info = get_order_info(order_info['id'], order_info['symbol'])
        if order_info['status'] == 'closed':
            cprint(f"/-- {bitget_usdv} Order closed", "green")
            break
        else:
            sleeping(MIN_SLEEP * 2, MAX_SLEEP * 2)
            continue



def script_usdv_lz_bitget():
    cprint("/-- Start USDV process -->", "blue")

    recipients = get_recipients('bitget_address')
    private_keys = get_private_keys()

    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    bitget_usdv = get_bitget_token_balance('USDV')
    if bitget_usdv < LZ_SCRIPT_USDV_AMOUNT:
        cprint(f"Not enough USDT on Bitget, need at least {LZ_SCRIPT_USDV_AMOUNT} USDT", "red")

    recipient_map = map_recipients(recipients, private_keys)
    try:
        wallet_num = 0
        for item in private_keys:
            wallet_num += 1
            private_key = item['private_key']

            run_usdv_one_wallet_bidget(private_key, recipient_map[private_key], wallet_num)
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def run_usdv_one_wallet_bidget(private_key, recipient_wallet, wallet_num):
    web3_bsc = Web3(Web3.HTTPProvider(CHAINS['bsc']['rpc']))


    amount = round(LZ_SCRIPT_USDV_AMOUNT - random.uniform(0, 10), 2)
    # ------------------ Withdraw ------------------
    wallet_address = web3_bsc.eth.account.from_key(private_key).address
    cprint(f"/-- Withdraw {amount} USDV from bitget to wallet: {wallet_address} [{wallet_num}]", "blue")


    call_exchange_withdraw(wallet_address, round(amount + 0.8, 2), 'USDV', 'BEP20', 'bitget')

    sleeping(MIN_SLEEP, MAX_SLEEP)




    bridge_networks =  BRIDGE_NETWORKS.copy()
    random.shuffle(bridge_networks)

    bridge_networks.insert(0, 'bsc')
    bridge_networks.append('bsc')


    for index,network in enumerate(bridge_networks):

        if index == len(bridge_networks)-1:
            break
        cprint(f"/-- Step {index+1} {network}->{bridge_networks[index+1]}", "blue")


        web3 = Web3(Web3.HTTPProvider(CHAINS[network]['rpc']))
        check_wait_web3_balance(web3, network, wallet_address, USDV_TOKEN_ADDRESS[network], amount * 0.97)
        params = [network, bridge_networks[index+1], USDV_TOKEN_ADDRESS[network]]
        run_script_one(stargate_send_usdv, private_key, network, 0, params)

        sleeping(MIN_SLEEP, MAX_SLEEP)






    # ------------------ Check avalanche balance ------------------
    amount = check_wait_web3_balance(web3_bsc, 'bsc', wallet_address, USDV_TOKEN_ADDRESS['bsc'], amount* 0.97)
    sleeping(2, 3)

    # ------------------ Withdraw to Bitget ------------------
    cprint("/-- Withdraw to Bitget", "blue")

    transfer(web3_bsc, private_key, recipient_wallet, 'bsc', USDV_TOKEN_ADDRESS['bsc'], amount)

    sleeping(MIN_SLEEP, MAX_SLEEP)

    while True:
        sleeping(MIN_SLEEP * 2, MAX_SLEEP * 2)
        cprint("/-- Check Bitget USDV balance", "blue")
        bitget_usdv = get_bitget_token_balance('USDV')
        if bitget_usdv >= amount:
            cprint(f"/-- {bitget_usdv} USDV found, continue...", "green")
            break
        else:
            sleeping(MIN_SLEEP, MAX_SLEEP)
            continue


