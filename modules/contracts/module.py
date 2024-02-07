from termcolor import cprint

from config.settings import MIN_SLEEP, MAX_SLEEP
from helpers.cli import print_input_amounts_range
from helpers.factory import run_script
from helpers.functions import sleeping
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_web3
from modules.contracts.functions import *
from modules.orbiter_bridge.functions import claim_points


def interface_contracts():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Deposit to contract', 'yellow')
            cprint(f'2. Withdraw from contract', 'yellow')
            cprint(f'3. Claim rewards', 'yellow')
            cprint(f'4. Claim Orbiter points', 'yellow')



            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                amount_str = print_input_amounts_range('Deposit amount')
                run_script(stake, 'scroll', amount_str, [])
                break


            elif option == '2':
                run_script(withdraw, 'scroll',0, [])

                break

            elif option == '3':
                run_script(claim, 'scroll', 0, [])

                break


            elif option == '4':
                prt_keys = get_private_keys()
                web3 = get_web3(CHAINS['zksync']['rpc'])

                for item in prt_keys:
                    account = web3.eth.account.from_key(item['private_key'])
                    claim_points(account.address)
                    sleeping(MIN_SLEEP, MAX_SLEEP)

                break


            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
