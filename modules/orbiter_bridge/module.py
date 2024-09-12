from helpers.cli import *
from modules.orbiter_bridge.functions import orbiter_eth_bridge, orbiter_token_bridge
from helpers.factory import run_script


def interface_orbiter_bridge():
    from_network = print_input_network("From network")
    to_networks_added = ['starknet'] if from_network == 'arbitrum' else []
    to_network = print_input_network("To network", [], to_networks_added)
    token_address = print_input_contract_address("Token address")
    amount_str = print_input_amounts_range('Bridge amount')

    if token_address == '':
        params = [from_network, to_network]
        run_script(orbiter_eth_bridge, from_network, amount_str, params)
    else:
        params = [from_network,to_network,token_address]
        run_script(orbiter_token_bridge, from_network, amount_str, params)




