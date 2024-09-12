from config.volume_config import *
from modules.nitro_bridge.functions import nitro_eth_bridge
from modules.unused_contracts.module import run_unused_fn
from scripts.scroll.functions import *
from modules.swaps.functions import *
from modules.landings.functions import *
from datetime import datetime


# OKX need to have your wallet addresses in whitelist
# OKX need to have ETH balance
def script_scroll_okx():
    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()
    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    recipient_map = map_recipients(recipients, private_keys)

    try:
        for item in private_keys:
            private_key = item['private_key']
            one_wallet(item, recipient_map[private_key])
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit



def one_wallet(item, recipient_wallet):
    # ------------------ Init ------------------
    if START_NETWORK == 'random':

        start_network = random.choice(['arbitrum', 'optimism','linea'])
    else:
        start_network = START_NETWORK


    web3_start = get_web3(CHAINS[start_network]['rpc'], item['proxy'])
    web3_scroll = get_web3(CHAINS['scroll']['rpc'], item['proxy'])
    private_key = item['private_key']
    start_time = datetime.now()
    full_path = ''
    csv_name = f'volume_report'
    wallet_address = web3_scroll.eth.account.from_key(private_key).address
    left_for_fee = 0.025
    # ------------------------------------------



    # ------------------ Withdraw ------------------
    withdraw_keys = {
        'linea': 'ETH-Linea',
        'optimism': 'ETH-Optimism',
        'arbitrum': 'ETH-Arbitrum One',
        'zksync': 'ETH-zkSync Era',

    }
    pct = VOLUME_ETH_AMOUNT * MAX_DEVIATION_PCT/100
    amount = round(VOLUME_ETH_AMOUNT - random.uniform(0, pct), 4)
    cprint(f"/-- Withdraw {amount} to wallet: {wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.0002, 4), 'ETH', withdraw_keys[start_network], 'okx')
    sleeping(MIN_SLEEP, MAX_SLEEP)
    # ------------------------------------------

    # ------------------ Bridge To Scroll ------------------
    check_wait_web3_balance(web3_start, start_network, wallet_address, '', amount)
    params = [start_network, 'scroll']
    # CHOOSE random  bridge
    if START_BRIDGE == 'random':
        bridge_fn_start = random.choice([nitro_eth_bridge, orbiter_eth_bridge])
    elif START_BRIDGE == 'nitro':
        bridge_fn_start = nitro_eth_bridge
    else:
        bridge_fn_start = orbiter_eth_bridge




    run_script_one(bridge_fn_start, private_key, start_network, '', params)
    # ------------------------------------------------------

    # ------------------ Fee deduction ------------------
    amount = check_wait_web3_balance(web3_scroll, 'scroll', wallet_address, '', amount*0.97)
    amount -= left_for_fee
    # ----------------------------------------------

    # ------------- Supply and Borrow  ------------
    run_script_one(supply_eth_layerbank, private_key, 'scroll', str(amount))
    sleeping(2, 3)
    run_script_one(enable_collateral, private_key, 'scroll','')
    sleeping(2, 3)
    run_script_one(borrow_usdc, private_key, 'scroll','')
    sleeping(2, 3)
    balance = check_wait_web3_balance(web3_scroll, 'scroll', wallet_address, TOKENS['USDC'], 5)
    add_to_stat(1, balance)
    # -------------------------------------------

    # -------------BODY of ROUTE-----------------
    routes=generate_route_data(VOLUME_REPEAT)
    path = generate_path(web3_scroll, routes)
    full_path += path
    cprint(f"/-- Swap PATH: {path}", "yellow")

    for route in routes:
        grouped_tokens = route['grouped_tokens']
        run_script_one(route['function'], private_key, 'scroll', '', grouped_tokens)
        balance = check_wait_web3_balance(web3_scroll, 'scroll', wallet_address, grouped_tokens[1], balance * 0.98)

        add_to_stat(1, balance)

        sleeping(MIN_SLEEP, MAX_SLEEP)
    # ------------------------------------------


    # ------------- REPAY USDC  ------------
    buy_full_repay(web3_scroll, private_key)
    sleeping(MIN_SLEEP, MAX_SLEEP)
    run_script_one(repay_usdc, private_key, 'scroll','')
    sleeping(2, 3)

    # ------ --------------Random Unused fn----------------------------------
    run_unused_fn('scroll')
    # ---------------------------------------------------


    run_script_one(withdraw_eth_layerbank, private_key, 'scroll','')
    # -------------------------------------------


    # --------------- Bridge to END network ---------------
    amount = amount * 0.9
    amount = check_wait_web3_balance(web3_scroll, 'scroll', wallet_address, '', amount)

    if BALANCE_LEFT:
        amount = amount -get_amount_in_range(BALANCE_LEFT)

    # CHOOSE random network  and bridge
    if END_BRIDGE == 'random':
        bridge_fn = random.choice([nitro_eth_bridge, orbiter_eth_bridge])
    elif END_BRIDGE == 'nitro':
        bridge_fn = nitro_eth_bridge
    else:
        bridge_fn = orbiter_eth_bridge

    if END_NETWORK == 'random':

        bridge_network = random.choice(['arbitrum', 'optimism','linea'])
    else:
        bridge_network = END_NETWORK

    web3_end = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))

    params = ['scroll', bridge_network]
    run_script_one(bridge_fn, private_key, 'scroll', str(amount), params)
    add_to_stat(1, get_eth_price(amount))
    sleeping(MIN_SLEEP, MAX_SLEEP)
    # -------------------------------------------------



    # ------------------ Withdraw to OKX ------------------
    amount = check_wait_web3_balance(web3_end, bridge_network, wallet_address, '', amount*0.95)
    # MIN required balance for transfer tx to OKX

    amount = amount - get_min_balance(bridge_network)
    sleeping(MIN_SLEEP, MAX_SLEEP)
    cprint("/-- Withdraw to OKX", "blue")
    transfer(web3_end, private_key, recipient_wallet, bridge_network, '', amount)
    # -----------------------------------------------------

    # ------------------ Write to CSV -------------------
    end_time = datetime.now()
    write_csv_volume(csv_name, [
        wallet_address,
        private_key,
        full_path + '->orbiter|nitro->okx',
        total_volume,
        total_txs,
        start_time.strftime("%Y-%m-%d %H:%M"),
        end_time.strftime("%Y-%m-%d %H:%M")
    ])

    sleeping(MIN_SLEEP, MAX_SLEEP)
    # --------------------------------------------------

    # ----------- Check OKX subAccount balances -------------
    while True:
        cprint("/-- Check OKX main account balance", "blue")
        main_acc_balance = get_okx_token_balance(0, 'ETH')
        if main_acc_balance >= amount:
            cprint(f"/-- {main_acc_balance} ETH found", "green")
            break
        else:
            tranfer_from_subs_okx()

        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue
