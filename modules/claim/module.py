from tabulate import tabulate
from termcolor import cprint
from web3 import Web3

from config.settings import MIN_SLEEP, MAX_SLEEP
from helpers.cli import print_input_amounts_range
from helpers.factory import run_script
from helpers.functions import sleeping
from helpers.settings_helper import get_private_keys
from modules.claim.functions import *
from loguru import logger


def interface_zkfair():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Check wallet', 'yellow')
            cprint(f'2. Claim rewards', 'yellow')

            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                private_keys = get_private_keys()
                web3 = Web3(Web3.HTTPProvider(CHAINS['zkfair']['rpc']))

                try:
                    result = []
                    for item in private_keys:
                        private_key = item['private_key']
                        one = {}
                        one['#'] = item['index']
                        one['private_key'] = item['private_key']
                        one.update(check(web3, private_key))
                        result.append(one)
                        print(one)

                        sleeping(MIN_SLEEP, MAX_SLEEP)
                    save_csv(result)
                    table = tabulate(result, headers='keys', tablefmt='fancy_grid')
                    print(table)


                except KeyboardInterrupt:
                    cprint(f' Exit, bye bye\n', 'red')
                break


            elif option == '2':
                run_script(claim, 'zkfair', 0, [])

                break

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
