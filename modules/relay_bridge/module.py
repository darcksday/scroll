from helpers.cli import *
from modules.relay_bridge.functions import relay_call
from helpers.factory import run_script


def interface_relay_bridge():
    available_chains = ['arbitrum', 'nova', 'ethereum', 'optimism', 'zksync', 'base', 'zora', 'scroll','linea','blast']
    disabled_chains = [key for key in CHAINS.keys() if key not in available_chains]

    from_network = print_input_network("From network", disabled_chains)
    to_network = print_input_network("To network", disabled_chains)
    amount_str = print_input_amounts_range()

    params = [from_network, to_network]
    run_script(relay_call, from_network, amount_str, params)