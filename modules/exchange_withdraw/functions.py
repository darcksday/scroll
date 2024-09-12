
import ccxt

from helpers.retry import retry
from modules.exchange_withdraw.config import CEX_KEYS
from modules.exchange_withdraw.cli import *


@retry
def call_exchange_withdraw(wallet_address: str, amount: float, token: str, network, cex: str = DEFAULT_CEX):
    # amount_ = round(random.uniform(amount_from, amount_to), 7)
    cprint(f"/-- Start withdraw to {wallet_address} -->", "green")
    account = get_ccxt(cex)
    params = {}

    if cex == 'okx':
        network = network.split("-", 1)
        network=network[0] if len(network) == 1 else network[1]
        account.load_markets()
        networks = account.currencies[token]['networks']

        params['fee'] = networks[network]['fee']
        if network == 'CELO':
            params['fee'] = 0.0008
        params['pwd'] = CEX_KEYS[cex]['password']

    if cex == 'bitget':
        params = {'chain': network}

    # Harmony network
    # if token == 'ONE':
    #     wallet_address = util.convert_hex_to_one(wallet_address)


    # if token == 'KAVA':
    #     wallet_address = eth_to_kava_address(wallet_address)

    params['network'] = network
    account.withdraw(
        code=token,
        amount=amount,
        address=wallet_address,
        tag=None,
        params=params
    )

    cprint(f'{cex} withdraw {amount} {token} success => {wallet_address}', 'green')



def bitget_get_withdrawal_info(token):
    exchange = get_ccxt(DEFAULT_CEX)

    currencies = exchange.fetch_currencies()

    networks = []
    network_data = {}

    if currencies is not None:
        for currency_code, currency in currencies.items():
            if currency_code == token.upper():
                try:
                    chains_info = currency.get('info', {}).get('chains', [])
                    for chain_info in chains_info:
                        is_withdraw_enabled = chain_info.get('withdrawable', 'false') == 'true'

                        fee = chain_info.get('withdrawFee')
                        if fee is not None:
                            fee = float(fee)

                        min_withdrawal = chain_info.get('minWithdrawAmount')
                        if min_withdrawal is not None:
                            min_withdrawal = float(min_withdrawal)

                        chain_name = chain_info.get('chain', '')
                        if is_withdraw_enabled:
                            network_data[chain_name] = (chain_name, fee, min_withdrawal)
                            networks.append(chain_name)
                except Exception as e:
                    print(f"\n>>>  Error fetching fees for {currency_code}: {str(e)}")
                break
    else:
        print("\n>>>  Currencies not found")

    return networks, network_data



def mexc_get_withdrawal_info(token):
    exchange = get_ccxt(DEFAULT_CEX)

    currencies = exchange.fetch_currencies()

    networks = []
    network_data = {}

    if token in currencies  :
        currency = currencies[token]
        try:
            chains_info = currency.get('info', {}).get('networkList', [])
            for chain_info in chains_info:

                is_withdraw_enabled = chain_info.get('withdrawEnable', True) == True
                fee = chain_info.get('withdrawFee')
                if fee is not None:
                    fee = float(fee)

                min_withdrawal = chain_info.get('withdrawMin')
                if min_withdrawal is not None:
                    min_withdrawal = float(min_withdrawal)

                chain_name = chain_info.get('network', '')
                if is_withdraw_enabled:
                    network_data[chain_name] = (chain_name, fee, min_withdrawal)
                    networks.append(chain_name)
        except Exception as e:
            print(f"\n>>>  Error fetching fees for {token}: {str(e)}")
    else:
        print("\n>>>  Currencies not found")
    return networks, network_data


def okx_get_withdrawal_info(token):
    exchange = get_ccxt(DEFAULT_CEX)
    currencies = exchange.fetch_currencies()
    networks = []
    network_data = {}

    if currencies is not None:
        for currency_code, currency in currencies.items():
            if currency_code == token.upper():
                networks_info = currency.get('networks')
                if networks_info is not None:
                    for network, network_info in networks_info.items():

                        fee = network_info.get('fee')
                        if fee is not None:
                            fee = float(fee)

                        min_withdrawal = network_info.get('limits', {}).get('withdraw', {}).get('min')
                        if min_withdrawal is not None:
                            min_withdrawal = float(min_withdrawal)

                        id = network_info.get('id')
                        is_withdraw_enabled = network_info.get('withdraw', False)

                        if is_withdraw_enabled:
                            network_data[network] = (id, fee, min_withdrawal)
                            networks.append(network)
                else:
                    print(f"\n>>>  Currency {currency_code} doesn't contain 'networks' attribute")
    else:
        print("\n>>>  Currencies not found")

    return networks, network_data


def binance_get_withdrawal_info(token):
    exchange = get_ccxt(DEFAULT_CEX)
    currencies = exchange.fetch_currencies()

    networks = []
    network_data = {}

    if currencies is not None:
        for currency_code, currency in currencies.items():
            if currency_code == token.upper():
                try:
                    network_list = currency.get('info', {}).get('networkList', [])
                    for network in network_list:
                        is_withdraw_enabled = network.get('withdrawEnable', False)

                        fee = network.get('withdrawFee')
                        if fee is not None:
                            fee = float(fee)

                        min_withdrawal = network.get('withdrawMin')
                        if min_withdrawal is not None:
                            min_withdrawal = float(min_withdrawal)

                        network_name = network.get('name', '')
                        network_code = network.get('network', '')

                        if is_withdraw_enabled:
                            network_data[network_name] = (network_code, fee, min_withdrawal)
                            networks.append(network_name)
                except Exception as e:
                    print(f"\n>>>  Error fetching fees for {currency_code}: {str(e)}")
                break
    else:
        print("\n>>>  Currencies not found")

    return networks, network_data


def kucoin_get_withdrawal_info(token):
    exchange = get_ccxt(DEFAULT_CEX)
    currencies = exchange.fetch_currencies()
    networks = []
    network_data = {}

    if currencies is not None:
        for currency_code, currency in currencies.items():
            if currency_code == token.upper():
                try:
                    for network_code, network in currency['networks'].items():
                        is_withdraw_enabled = network.get('info', {}).get('isWithdrawEnabled', 'false') == 'true'

                        fee = network.get('fee')
                        if fee is not None:
                            fee = float(fee)

                        min_withdrawal = network.get('info', {}).get('withdrawMinSize')
                        if min_withdrawal is not None:
                            min_withdrawal = float(min_withdrawal)

                        chain_full_name = network.get('info', {}).get('chainFullName', '')
                        if is_withdraw_enabled:
                            network_data[chain_full_name] = (network_code, fee, min_withdrawal)
                            networks.append(chain_full_name)
                except Exception as e:
                    print(f"\n>>>  Error fetching fees for {currency_code}: {str(e)}")
                break
    else:
        print("\n>>>  Currencies not found")

    return networks, network_data


def get_wd_info(token):
    result = []
    if DEFAULT_CEX == 'binance':
        result = binance_get_withdrawal_info(token)
    elif DEFAULT_CEX == 'kucoin':
        result = kucoin_get_withdrawal_info(token)

    elif DEFAULT_CEX == 'okx':
        result = okx_get_withdrawal_info(token)

    elif DEFAULT_CEX == 'bitget':
        result = bitget_get_withdrawal_info(token)


    elif DEFAULT_CEX == 'mexc':
        result = mexc_get_withdrawal_info(token)

    return result


def get_ccxt(cex):
    dict_ = {
        'apiKey': CEX_KEYS[cex]['api_key'],
        'secret': CEX_KEYS[cex]['api_secret'],
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    }

    if cex in ['kucoin', 'okx', 'bitget']:
        dict_['password'] = CEX_KEYS[cex]['password']

    return ccxt.__dict__[cex](dict_)


# def eth_to_kava_address(eth_address):
#     if not eth_address.startswith("0x"):
#         raise ValueError("Invalid Ethereum address")
#
#     eth_bytes = bytes.fromhex(eth_address[2:])
#     converted_bits = bech32.convertbits(eth_bytes, 8, 5)
#     kava_address = bech32.bech32_encode('kava', converted_bits)
#     return kava_address