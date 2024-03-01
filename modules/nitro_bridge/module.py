from helpers.cli import *
from modules.nitro_bridge.functions import nitro_eth_bridge
from modules.orbiter_bridge.functions import orbiter_eth_bridge, orbiter_token_bridge
from helpers.factory import run_script


def interface_nitro_bridge():
    from_network = print_input_network("From network")
    to_network = print_input_network("To network", [])
    amount_str = print_input_amounts_range('Bridge amount')

    params = [from_network, to_network]
    run_script(nitro_eth_bridge, from_network, amount_str, params)




