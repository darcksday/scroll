
from helpers.web3_helper import *
from helpers.functions import *
from modules.run_layer_zero.config import *





def stargate_bridge_usdv(web3, private_key, amount,from_chain, to_chain,from_token, retry=0):
        account = web3.eth.account.from_key(private_key)
        wallet = account.address
        router_address,router_contract =__get_stargate_bridge_contract(web3,from_chain)

        address_contract = web3.to_checksum_address(SWAP_RECOLOR_CONTRACTS[from_chain])


        bridge_contract = web3.eth.contract(address=address_contract, abi=SWAP_RECOLOR_ABI)


        token_contract, token_decimal, symbol = check_data_token(web3, from_token)



        if not  amount:
            amount = get_token_balance(web3, wallet, from_token)
        else:
            amount = int_to_wei(amount,6)

        cprint(f'/-- {symbol} {wei_to_int(amount, token_decimal)} {from_chain} => {to_chain} for USDV {wallet} -->', 'green')


        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)

        if amount > allowance_amount:
            cprint(f'/-- Approve token: USDT', 'green')
            approve_token(web3, private_key, from_chain, from_token, address_contract)
            sleeping(5, 10)



        lz_fee = stargate_lz_fee(wallet, from_chain, to_chain, router_contract)
        print('LZ Fees:', wei_to_int(lz_fee, 18))

        if amount:
            min_amount=amount-50
            swap_params = [from_token, amount, min_amount]
            wallet_bytes = wallet.replace('0x', '0x000000000000000000000000')

            param = [wallet_bytes, amount, min_amount, LZ_CHAIN_IDS[to_chain]]
            extra_options='0x00010000000000000000000000000000000000000000000000000000000000029810'
            msg_fee=[lz_fee, 0]
            compose_msg=b''



            chain_id = web3.eth.chain_id

            contract_txn = bridge_contract.functions.swapRecolorSend(
                swap_params,
                3,
                param,
                extra_options,
                msg_fee,
                wallet,
                compose_msg
            ).build_transaction(
                {
                    'from': wallet,
                    'nonce': web3.eth.get_transaction_count(wallet),
                    'value': int(lz_fee),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )
            contract_txn = add_gas_price(web3, contract_txn, chain_id)
            contract_txn = add_gas_limit(web3, contract_txn, chain_id)
            tx_hash = sign_tx(web3, contract_txn, private_key)
            return tx_hash
        else:
            raise Exception(f'SKIP. Insufficient balance, balance:{amount}')

def stargate_send_usdv(web3, private_key, amount, from_chain, to_chain, from_token, retry=0):
    account = web3.eth.account.from_key(private_key)
    wallet = account.address
    router_address, router_contract = __get_stargate_bridge_contract(web3, from_chain)

    address_contract = web3.to_checksum_address(SWAP_RECOLOR_CONTRACTS[from_chain])



    bridge_contract = web3.eth.contract(address=address_contract, abi=SEND_USDV_ABI[from_chain])


    token_contract, token_decimal, symbol = check_data_token(web3, from_token)

    if not amount:
        amount = get_token_balance(web3, wallet, from_token)
    else:
        amount = int_to_wei(amount, 6)

    cprint(f'/-- {symbol} {wei_to_int(amount, token_decimal)} {from_chain} => {to_chain} for USDV {wallet} -->', 'green')



    lz_fee = stargate_lz_fee(wallet, from_chain, to_chain, router_contract)
    print('LZ Fees:', wei_to_int(lz_fee, 18))

    if amount:
        min_amount = amount - 50
        wallet_bytes = wallet.replace('0x', '0x000000000000000000000000')

        if from_chain=='avalanche':
            param = [wallet_bytes, amount, min_amount, LZ_CHAIN_IDS[to_chain]]
            extra_options = '0x00010000000000000000000000000000000000000000000000000000000000029810'

        else:
            param = [wallet_bytes, amount, min_amount, LZ_CHAIN_IDS[to_chain]]
            extra_options = '0x00020000000000000000000000000000000000000000000000000000000000029810'
        msg_fee = [lz_fee, 0]
        compose_msg = b''

        chain_id = web3.eth.chain_id

        contract_txn = bridge_contract.functions.send(
            param,
            extra_options,
            msg_fee,
            wallet,
            compose_msg
        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': int(lz_fee),
                'gasPrice': 0,
                'gas': 0,
            }
        )
        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(f'SKIP. Insufficient balance, balance:{amount}')




def __get_stargate_bridge_contract(web3, chain):
    address_contract = COMMON_STARGATE_BRIDGE_CONTRACT

    if chain == 'fantom':
        address_contract = FANTOM_STARGATE_BRIDGE_CONTRACT
    elif chain == 'bsc':
        address_contract = BSC_STARGATE_BRIDGE_CONTRACT
    elif chain == 'optimism':
        address_contract = OPTIMISM_STARGATE_BRIDGE_CONTRACT
    elif chain == 'metis':
        address_contract = METIS_STARGATE_BRIDGE_CONTRACT
    elif chain == 'arbitrum':
        address_contract = ARBITRUM_STARGATE_BRIDGE_CONTRACT
    elif chain == 'coredao':
        address_contract = CORE_COREDAO_CONTRACT
    elif chain == 'zksync':
        address_contract = ZKSYNC_STARGATE_BRIDGE_CONTRACT
    elif chain == 'base':
        address_contract = BASE_STARGATE_ROUTER_CONTRACT
    elif chain == 'kava':
        address_contract = KAVA_STARGATE_ROUTER_CONTRACT

    address_contract = web3.to_checksum_address(address_contract)
    contract = web3.eth.contract(address=address_contract, abi=ABI_STARGATE_BRIDGE_V1)
    return address_contract, contract

def merkly_v2(web3, private_key, amount, from_chain='scroll', to_chain=''):
    account = web3.eth.account.from_key(private_key)
    wallet = account.address

    if not amount:
        amount = 200000
    else:
        amount = int_to_wei(amount, 18)


    replacement_hex_value = hex(amount)
    original_hex_value = '0x00030100110100000000000000000000000000000000'

    options = replace_end(original_hex_value, replacement_hex_value)

    if not to_chain:
        to_chain=random.choice(CHEAP_NETWORKS)


    address_contract = web3.to_checksum_address(MERKLEY_BRIDGE_CONTRACTS_V2[from_chain])

    bridge_contract = web3.eth.contract(address=address_contract, abi=MERKLY_ABI)




    cprint(f'/-- Start merkly bridge {from_chain} => {to_chain}, wallet {wallet} -->', 'green')

    lz_fee = merkly_lz_fee(bridge_contract,to_chain)



    print('LZ Fees:', wei_to_int(lz_fee[0], 18))

    if amount:

        contract_txn = bridge_contract.functions.bridgeGas(
            LZ_CHAIN_IDS_V2[to_chain],
            '',
            options
        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': int(lz_fee[0]),
                'gasPrice': 0,
                'gas': 0,
            }
        )
        contract_txn = add_gas_price(web3, contract_txn, from_chain)
        contract_txn = add_gas_limit(web3, contract_txn, from_chain)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash
    else:
        raise Exception(f'SKIP. Insufficient balance, balance:{amount}')



def replace_end(original_hex_value, replacement_hex):
    # Convert the replacement_hex to a string without the '0x' prefix
    replacement_hex_str = replacement_hex[2:]

    # Extract the length of the original_hex_value excluding the '0x' prefix
    original_hex_str = original_hex_value[2:]
    original_length = len(original_hex_str)

    # Replace the end of the original_hex_value with the replacement_hex
    modified_hex_value = '0x' + original_hex_str[:-len(replacement_hex_str)] + replacement_hex_str

    return modified_hex_value
def merkly_lz_fee(contract,to_chain):


    return contract.functions.quote(
        LZ_CHAIN_IDS_V2[to_chain],
        '',
        '0x00030100110100000000000000000000000000030d40',
        False
    ).call()



















