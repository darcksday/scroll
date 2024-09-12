import random
from termcolor import cprint
from config.settings import CHAINS
from modules.exchange_withdraw.config import CEX_DEFAULT_TOKENS


def print_input_network(title='Select network', chains_disable=[], add_chains=[]):
    try:
        while True:
            chains_result = list(CHAINS.keys())

            for chain in add_chains:
                chains_result.append(chain)

            for chain in chains_result.copy():
                if chain in chains_disable:
                    chains_result.remove(chain)

            cprint(f'>>> {title}:', 'yellow')
            for index, chain in enumerate(chains_result):
                cprint(f'{index + 1}. {chain.capitalize()}', 'yellow')

            try:
                option_chain = int(input("> "))
            except ValueError:
                option_chain = 0

            if option_chain < 1 or option_chain > len(chains_result) + 1:
                cprint(f'Wrong network. Please try again.\n', 'red')
                continue
            else:
                return chains_result[option_chain - 1]
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def print_input_contract_address(title='Contract address'):
    try:
        while True:
            cprint(f'>>> {title} (empty for native):', 'yellow')
            contract_address = input("> ")

            if len(contract_address) and len(contract_address) != 42:
                cprint(f'Wrong contract address. Please try again.\n', 'red')
                continue
            else:
                return contract_address.lower()
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit



def print_input_value(title='Input value'):
    try:
        while True:
            cprint(f'>>> {title} (1-yes or 0-no):', 'yellow')
            value = input("> ")

            return value
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def print_input_wallets_range():
    try:
        while True:
            cprint(f'>>> Choose wallets range (number / range / empty = ALL):', 'yellow')
            wallets_range = input("> ")

            # Selected one wallet
            if wallets_range.isnumeric():
                return f"{wallets_range}-{wallets_range}"

            if len(wallets_range) and '-' not in wallets_range:
                cprint(f'Wrong contract address. Please try again.\n', 'red')
                continue

            return wallets_range
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def print_input_amounts_range(title='Swap amount'):
    try:
        while True:
            cprint(f'>>> {title} (number / range / empty = ALL):', 'yellow')
            return input("> ")
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def get_amount_in_range(amount,check_range=True):
    if check_range and amount!=0 and len(amount) and '-' in amount:
        amount_from, amount_to = amount.split('-')
        diff = float(amount_to) - float(amount_from)
        amount = round(random.uniform(float(amount_from), float(amount_to)), 5 if diff <= 1 else 3)

    try:
        amount = float(amount)
    except ValueError:
        amount = 0
    return amount


def get_int_in_range(amount,check_range=True):
    amount=str(amount)
    if check_range and amount!=0 and len(amount) and '-' in amount:
        amount_from, amount_to = amount.split('-')
        if amount_from:
            return random.randint(int(amount_from), int(amount_to))
        else:
            return int(amount)

    return int(amount)


def print_exchange_withdraw_token():
    try:
        while True:
            cprint(f'>>> Select token OR write custom one:', 'yellow')
            for index, token in enumerate(CEX_DEFAULT_TOKENS):
                cprint(f'{index + 1}. {token}', 'yellow')
            cprint(f'/ or write custom token symbol', 'yellow')
            option_token = input("> ")

            if option_token.isnumeric() and 1 <= int(option_token) <= len(CEX_DEFAULT_TOKENS):
                return CEX_DEFAULT_TOKENS[int(option_token) - 1]
            else:
                if 1 < len(option_token) < 5:
                    return option_token.upper()
                else:
                    cprint(f'Wrong token symbol. Please try again.\n', 'red')
                    continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
