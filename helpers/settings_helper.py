import csv
import random

from web3 import Web3
from termcolor import cprint

from config.settings import CHAINS, DEFAULT_CEX, USE_PROXY
from helpers.csv_helper import get_csv_separator


def get_private_keys(shufle=False):
    with open('config/wallets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=get_csv_separator())
        private_keys = [row['private_key'].strip() for row in reader if row['private_key'].strip()]
        account_proxy=None
        if USE_PROXY:
            proxy=get_proxy_list()
            account_proxy={key: proxy[i % len(proxy)] for i, key in enumerate(private_keys)}

        privates=[]


        for index,prt in enumerate(private_keys):
            obj= {
                'private_key': prt.strip(),
                'index':index,
                'proxy': None

            }
            if account_proxy:
                obj['proxy']= {
                    'http': account_proxy[prt],
                    'https': account_proxy[prt],
                }
            privates.append(obj)








    if len(privates) == 0:
        cprint("No private keys found in wallets.csv", "red")
    if shufle:
        random.shuffle(privates)


    return privates


def get_private_keys_txt():
    with open('config/wallets.txt', "r") as file:
        return [row.strip() for row in file]






    if len(privates) == 0:
        cprint("No private keys found in wallets.csv", "red")
    return privates



def get_withdraw_wallet_list():
    with open('config/wallets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=get_csv_separator())
        prt_list = [row['private_key'].strip() for row in reader if row['private_key'] != '']
    if len(prt_list) == 0:
        cprint("No private keys found in config/wallet.csv", "red")

    web3 = Web3(Web3.HTTPProvider(CHAINS['ethereum']['rpc']))
    wallet_list = [web3.eth.account.from_key(prt).address for prt in prt_list]
    return wallet_list


def get_aptos_wallet_list():
    with open("config/aptos_wallets.txt", "r") as f:
        wallet_list = [row.strip() for row in f]
    if len(wallet_list) == 0:
        cprint("No wallet list found in config/aptos_wallets.txt", "red")
    return wallet_list


def get_recipients(key=f'{DEFAULT_CEX}_address'):
    with open('config/wallets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=get_csv_separator())
        recipients = [row[key].strip() for row in reader if row[key] != '']
    if len(recipients) == 0:
        cprint("No recipients found in config/wallet.csv", "red")
    return recipients


def get_proxy_list():
    with open("config/proxies.txt", "r") as f:
        recipients = [row.strip() for row in f]
    if len(recipients) == 0:
        cprint("No proxy found in config/proxies.txt", "red")
    return recipients


def get_ref_list():
    with open("config/canvas_ref.txt", "r") as f:
        recipients = [row.strip() for row in f]
    if len(recipients) == 0:
        cprint("No ref found in config/canvas_ref.txt", "red")
    return recipients

def get_contract_list():
    with open("config/contracts.txt", "r") as f:
        recipients = [row.strip() for row in f]
    if len(recipients) == 0:
        cprint("No contracts found in config/contracts.txt", "red")
    return recipients

def get_random_proxy():
    proxies = {}
    proxy_list = get_proxy_list()
    if len(proxy_list) > 0:
        proxy = random.choice(proxy_list)
        proxies = {
            'http': proxy,
            'https': proxy,
        }

    return proxies

def get_own_contract_address(prt_key):
    result=False
    with open('config/wallets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=get_csv_separator())
        for row in reader:
            if row['private_key'].strip() and row['private_key']==prt_key:
                result=(Web3.to_checksum_address(row['contract_address']),row['contract_type'])

    return result