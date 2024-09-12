from helpers.cli import *
from modules.hyperlane.functions import hyperlane_eth_bridge
from helpers.factory import run_script


def interface_hyperlane_bridge():
    from_network = print_input_network("From network")
    to_network = print_input_network("To network")
    token_address = print_input_contract_address("Token address")
    amount_str = print_input_amounts_range('Bridge amount')

    if token_address == '':
        params = [from_network, to_network]
        run_script(hyperlane_eth_bridge, from_network, amount_str, params)
    else:
        cprint(f'Wrong action. Please try again.\n', 'red')
        




