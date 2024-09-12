from termcolor import cprint

from config.settings import DEFAULT_CEX
from helpers.cli import get_amount_in_range
from modules.exchange_withdraw.functions import get_wd_info


def print_exchange_networks(token):
    try:
        while True:
            cprint(f'>>> Select network:', 'yellow')

            (list_tokens, networks) = get_wd_info(token)
            for index, (key, value) in enumerate(networks.items()):
                cprint(f'{index + 1}. {key} (fee:{value[1]} | min:{value[2]})', 'yellow')

            option_chain = int(input("> "))
            if option_chain < 1 or option_chain > len(networks.items()) + 1:
                cprint(f'Wrong network. Please try again.\n', 'red')
                continue
            else:
                selected_key = list(networks.keys())[option_chain - 1]


                return networks[selected_key][0]

    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def print_exchange_withdraw_amount():
    try:
        while True:
            return input("Withdraw amount (number / range): ")
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def print_approve_transaction(amount_str, token, network, wallet_list):
    try:
        approx_symbol = ""
        if '-' in amount_str:
            approx_symbol = "~"
            amount = get_amount_in_range(amount_str)
        else:
            amount = float(amount_str)

        cprint(f'{DEFAULT_CEX.upper()} Withdraw {amount_str} {token} using {network} chain for {len(wallet_list)} wallets.', 'blue')
        cprint(f'TOTAL: {approx_symbol}{round(len(wallet_list) * amount, 4)} {token}.\n', 'blue')

        approval = input("Do you approve withdraw? (y/N): ")
        if approval.lower() != "y":
            cprint(f'Action Canceled.\n', 'red')
            return False
        return True
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
