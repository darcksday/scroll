import random

from helpers.factory import run_multiple
from helpers.functions import get_min_balance
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import check_wait_web3_balance
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.orbiter_bridge.functions import orbiter_eth_bridge
from modules.transfer.functions import map_recipients, transfer
from web3 import Web3
from scripts.functions import *
from config.orbiter_config  import *


def script_orbiter_eth():
    cprint("/-- Start Bridge process -->", "blue")

    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()

    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    okx_eth = get_okx_token_balance(0, 'ETH')
    if okx_eth < ETH_AMOUNT:
        cprint(f"Not enough ETH on OKX, need at least {ETH_AMOUNT} ETH", "red")

    recipient_map = map_recipients(recipients, private_keys)
    web3_linea = Web3(Web3.HTTPProvider(CHAINS['linea']['rpc']))
    try:
        for item in private_keys:
            private_key = item['private_key']

            run_orbiter_bridge_eth(web3_linea, item, recipient_map[private_key])
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt as error:
        cprint(f' Exit, bye bye\n', 'red')
        # raise SystemExit


def run_orbiter_bridge_eth(web3_linea, item, recipient_wallet):
    wallet_address = web3_linea.eth.account.from_key(item['private_key']).address
    pct = ETH_AMOUNT * 0.02
    amount = round(ETH_AMOUNT - random.uniform(0, pct), 4)

    # ------------------ Withdraw ------------------
    cprint(f"/-- Withdraw {amount} to wallet: [{item['index']}]{wallet_address}", "blue")

    call_exchange_withdraw(wallet_address, round(amount + 0.0002, 4), 'ETH', 'Linea', 'okx')
    sleeping(MIN_SLEEP, MAX_SLEEP)
    line_orb_fee=0.0005
    # ------------------ Start Bridge ------------------
    random.shuffle(NETWORKS)
    for bridge_network in NETWORKS:
        amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, '', amount * 0.98)
        #  balance left linea
        amount = amount - get_min_balance('linea')-line_orb_fee

        # BRIDGE FROM LINEA TO RANDOM NETWORK
        params = ['linea', bridge_network]
        run_script_one(orbiter_eth_bridge, item['private_key'], 'linea', str(amount), params)

        # RUN ADDITIONAL FUNCTION
        web3_random = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))
        if bridge_network in ADDITIONAL_FUNCTIONS:
            amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, '', amount * 0.98)
            run_multiple(ADDITIONAL_FUNCTIONS[bridge_network], bridge_network, [item])

        # BRIDGE FROM RANDOM NETWORK TO LINEA
        amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, '', amount * 0.98)
        params2 = [bridge_network, 'linea']
        #  balance left on random network
        amount = amount - get_min_balance(bridge_network)-line_orb_fee
        run_script_one(orbiter_eth_bridge, item['private_key'], bridge_network, str(amount), params2)

    amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, '', amount * 0.98)
    amount = amount - get_min_balance('linea')-line_orb_fee

    if END_NETWORK=='arbitrum' or END_NETWORK=='optimism':
        web3 = Web3(Web3.HTTPProvider(CHAINS[END_NETWORK]['rpc']))
        params3 = ['linea', END_NETWORK]
        run_script_one(orbiter_eth_bridge, item['private_key'], 'linea', str(amount), params3)
        sleeping(MIN_SLEEP, MAX_SLEEP)
        amount = check_wait_web3_balance(web3, END_NETWORK, wallet_address, '', amount * 0.98)
        amount = amount - get_min_balance(END_NETWORK)


        # ------------------ Withdraw to OKX ------------------
        cprint("/-- Withdraw to OKX", "blue")
        transfer(web3, item['private_key'], recipient_wallet, END_NETWORK, '', amount)

    else:
        # ------------------ Withdraw to OKX ------------------
        sleeping(MIN_SLEEP, MAX_SLEEP)
        cprint("/-- Withdraw to OKX", "blue")
        transfer(web3_linea, item['private_key'], recipient_wallet, 'linea', '', amount)

    # ----------- Check OKX subAccount balances -------------
    while True:
        cprint("/-- Check OKX main account balance", "blue")
        main_acc_balance = get_okx_token_balance(0, 'ETH')
        if main_acc_balance >= amount:
            cprint(f"/-- {main_acc_balance} ETH found", "green")
            break
        else:
            tranfer_from_subs_okx()
        sleeping(MIN_SLEEP * 2, MAX_SLEEP * 2)
        continue
