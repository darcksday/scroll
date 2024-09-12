from config.settings import  MIN_SLEEP, MAX_SLEEP, CHAINS
from helpers.cli import print_input_contract_address, print_input_network, print_input_amounts_range
from helpers.functions import sleeping
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import get_web3
from modules.exchange_withdraw.cli import *
from modules.transfer.functions import transfer, map_recipients
from web3 import Web3


def interface_transfer():
    network = print_input_network()
    token_address = print_input_contract_address()
    amount_str = print_input_amounts_range('Transfer amount')

    cprint("/-- Run transfer balances -->", "green")

    recipients = get_recipients()
    private_keys = get_private_keys()
    if len(recipients) == 0:
        cprint(f"No recipients found in config/wallet.csv {DEFAULT_CEX}", "red")
        return
    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    recipient_map = map_recipients(recipients, private_keys)

    for item in get_private_keys():
        amount = get_amount_in_range(amount_str)
        web3 = get_web3(CHAINS[network]['rpc'], item['proxy'])
        private_key=item['private_key']
        transfer(web3, private_key, recipients[item['index']], network, token_address, amount)
        sleeping(MIN_SLEEP, MAX_SLEEP)
