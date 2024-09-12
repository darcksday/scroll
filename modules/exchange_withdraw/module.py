from config.settings import MIN_SLEEP, MAX_SLEEP
from helpers.cli import print_exchange_withdraw_token
from helpers.functions import sleeping
from helpers.settings_helper import get_withdraw_wallet_list
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw


def interface_exchange_withdraw():

    wallet_list = get_withdraw_wallet_list()

    token = print_exchange_withdraw_token()
    network = print_exchange_networks(token)
    amount_str = print_exchange_withdraw_amount()
    if print_approve_transaction(amount_str, token, network, wallet_list):
        for wallet_address in wallet_list:
            amount = get_amount_in_range(amount_str)
            call_exchange_withdraw(wallet_address, amount, token, network)
            sleeping(MIN_SLEEP, MAX_SLEEP)
