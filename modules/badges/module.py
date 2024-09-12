from tabulate import tabulate
from termcolor import cprint
from web3 import Web3

from config.settings import MIN_SLEEP, MAX_SLEEP
from helpers.cli import print_input_amounts_range
from helpers.factory import run_script
from helpers.functions import sleeping
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_web3
from modules.badges.functions import *
from loguru import logger

from scripts.functions import run_script_one


def interface_badges():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Mint canvas profile && origin nft badge ', 'yellow')
            cprint(f'2. Claim other badges', 'yellow')

            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                private_keys = get_private_keys(USE_SHUFFLE)
                web3=get_web3(CHAINS['scroll']['rpc'])
                for item in private_keys:
                    private_key = item['private_key']
                    claim_canvas_profile(web3,private_key)
                    claim_origin_badge(web3, private_key)

                break


            elif option == '2':

                private_keys = get_private_keys(USE_SHUFFLE)
                web3 = get_web3(CHAINS['scroll']['rpc'])
                for item in private_keys:
                    private_key = item['private_key']
                    claim_custom_badges(web3, private_key)

                break
            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
