from helpers.cli import print_input_amounts_range, get_amount_in_range, print_input_network
from helpers.factory import run_script
from modules.run_layer_zero.functions import *


def interface_usdv():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Bridge USDT Avax > USDV BSC / Stargate', 'yellow')
            cprint(f'2. Bridge USDT Arbitrum > USDV BSC / Stargate', 'yellow')



            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                # Swap using mute.io
                amount_str = print_input_amounts_range('Bridge amount')
                params = ['avalanche','bsc',AVAX_USDT_TOKEN]
                run_script(stargate_bridge_usdv, 'avalanche', amount_str, params)
                break


            elif option == '2':
                amount_str = print_input_amounts_range('Bridge amount')
                params = ['arbitrum', 'bsc', ARB_USDT_ADDRESS]
                run_script(stargate_bridge_usdv, 'arbitrum', amount_str, params)
                break





            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
