from web3 import Web3
from termcolor import cprint
from config.settings import  CHAINS
from helpers.cli import print_input_contract_address, print_input_network
from helpers.csv_helper import save_csv_balance
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_token_balance, get_token_symbol


def interface_check_balance():
    network = print_input_network()
    contract_address = print_input_contract_address()
    web3 = Web3(Web3.HTTPProvider(CHAINS[network]['rpc']))

    cprint("/-- Run check balance -->", "green")

    for private_key in get_private_keys():
        wallet_address = web3.eth.account.from_key(private_key['private_key']).address

        balance = get_token_balance(web3, wallet_address, contract_address, True)
        symbol = get_token_symbol(web3, network, contract_address)

        cprint(f'Wallet [{private_key["index"]+1}]{wallet_address}', 'green')
        cprint(f'Balance: {balance} {symbol}', 'green')
        cprint(f'---', 'green')
        result={}
        result['wallet']=wallet_address
        result['symbol']=symbol
        result['balance']=balance
        save_csv_balance([result])

