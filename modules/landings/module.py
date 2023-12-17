from termcolor import cprint

from config.multiple_routes import USE_FUNCTIONS
from config.swap_routes import ROUTES
from helpers.cli import print_input_amounts_range, print_input_contract_address, print_input_value
from helpers.factory import run_script, run_random_swap, run_multiple
from modules.swaps.functions import *


def interface_swaps():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Swap tokens / mute.io', 'yellow')
            cprint(f'2. Swap tokens / zkswap.finance', 'yellow')



            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                # Swap using mute.io
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(swap_token_spacefi, 'zksync', amount_str, params)
                break


            elif option == '2':
                # Swap tokens/ zkswap.finance
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(open_ocean, 'zksync', amount_str, params)


                break

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
