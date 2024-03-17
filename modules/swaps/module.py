from termcolor import cprint

from helpers.cli import print_input_amounts_range, print_input_contract_address
from helpers.factory import run_script
from modules.swaps.functions import *


def interface_swaps():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Swap tokens / openocean.finance', 'yellow')
            cprint(f'2. Swap tokens / app.xy.finance', 'yellow')
            cprint(f'3. Swap tokens / syncswap.xyz', 'yellow')
            cprint(f'4. Swap tokens / zebra.xyz', 'yellow')
            cprint(f'5. Swap tokens / app.skydrome.finance', 'yellow')
            cprint(f'6. Swap tokens / ambient.finance', 'yellow')
            cprint(f'7. Swap tokens / izumi.finance', 'yellow')
            cprint(f'8. Swap tokens / sushi.com', 'yellow')




            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break




            elif option == '1':
                # open ocean swap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(open_ocean, 'scroll', amount_str, params)
                break


            elif option == '2':
                # open ocean swap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]

                run_script(xy_swap, 'scroll', amount_str, params)


            elif option == '3':
                # Syncswap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(swap_token_syncswap, 'scroll', amount_str, params)


            elif option == '4':
                # Zebra
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(swap_token_zebra, 'scroll', amount_str, params)


            elif option == '5':
                # Skydrome
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]
                run_script(swap_token_skydrome, 'scroll', amount_str, params)


            elif option == '6':
                # open ocean swap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]

                run_script(swap_ambient, 'scroll', amount_str, params)


            elif option == '7':
                # open ocean swap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]

                run_script(swap_izumi, 'scroll', amount_str, params)


            elif option == '8':
                # open ocean swap
                from_token = print_input_contract_address("From token")
                to_token = print_input_contract_address("To token")
                amount_str = print_input_amounts_range('Swap amount')
                params = [from_token, to_token]

                run_script(swap_sushi, 'scroll', amount_str, params)



            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
