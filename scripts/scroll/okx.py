from helpers.functions import get_min_balance
from modules.run_zksync.functions import xy_swap, supply_eth_eralend, enable_collateral, borrow_usdc, get_borrowed_balance, buy_full_repay, \
    repay_usdc, withdraw_eth_eralend
from scripts.zksync.functions import *


# OKX need to have your wallet addresses in whitelist
# OKX need to have ETH balance
def script_zksync_okx():
    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()
    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    recipient_map = map_recipients(recipients, private_keys)

    try:
        for item in private_keys:
            web3 = get_web3(CHAINS['zksync']['rpc'], item['proxy'])
            private_key = item['private_key']
            one_wallet_zksync(web3, private_key, recipient_map[private_key])
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def one_wallet_zksync(web3, private_key, recipient_wallet):
    start_time = datetime.now()
    full_path = ''
    csv_name = f'volume_report'
    wallet_address = web3.eth.account.from_key(private_key).address
    zk_start_balance = get_token_balance(web3, wallet_address, '', True)

    # # ------------------ Withdraw ------------------
    pct = ZKSYNC_ETH_AMOUNT_PER_ACC * 0.02
    amount = round(ZKSYNC_ETH_AMOUNT_PER_ACC - random.uniform(0, pct), 4)
    cprint(f"/-- Withdraw {amount} to wallet: {wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.0004, 4), 'ETH', 'ETH-zkSync Era', 'okx')

    sleeping(MIN_SLEEP, MAX_SLEEP)
    # ------------------ Check wallet balance ------------------

    # if empty balance on zk
    if zk_start_balance <= 0.005:
        zk_start_balance = random.uniform(0.0058, 0.0062)
        amount = amount - zk_start_balance

    for step in range(VOLUME_REPEAT):
        routes = generate_route_data()
        # Generate swap path
        path = generate_path(web3, routes)
        full_path += path

        cprint(f"/-- Swap PATH: {path} step {step + 1}/{VOLUME_REPEAT}", "yellow")
        check_wait_web3_balance(web3, 'zksync', wallet_address, '', amount)
        sleeping(2, 3)

        # ------------- Swap ETH > USD ------------
        first_token = routes[0]['grouped_tokens'][0]
        first_function = random.choice([odos_swap])
        params = ['', first_token]
        run_script_one(first_function, private_key, 'zksync', str(amount), params)
        return_amount = get_eth_price(amount)
        balance = check_wait_web3_balance(web3, 'zksync', wallet_address, first_token, return_amount)
        add_to_stat(1, balance)
        sleeping(MIN_SLEEP, MAX_SLEEP)
        # -------------------------------------------

        # -------------BODY of ROUTE-----------------
        for route in routes:
            grouped_tokens = route['grouped_tokens']
            params = grouped_tokens
            if route['params']:
                params = route['params'] + params
            run_script_one(route['function'], private_key, 'zksync', str(balance), params)
            balance = check_wait_web3_balance(web3, 'zksync', wallet_address, grouped_tokens[1], balance * 0.98)

            add_to_stat(1, balance)

            sleeping(MIN_SLEEP, MAX_SLEEP)
        # -------------BODY of ROUTE-----------------

        # ------------- Swap USD > ETH ------------
        last_token = routes[-1]['grouped_tokens'][1]
        last_function = random.choice([odos_swap])
        params = [last_token, '']
        run_script_one(last_function, private_key, 'zksync', balance, params)
        add_to_stat(1, balance)
        sleeping(MIN_SLEEP, MAX_SLEEP)
        # -------------------------------------------

        amount = amount * 0.98
        amount = check_wait_web3_balance(web3, 'zksync', wallet_address, '', amount)
        amount = amount - zk_start_balance

    # CHOOSE random network  and bridge
    if USE_BRIDGE == 'random':
        bridge_fn = random.choice([eth_bridge, orbiter_eth_bridge])
    elif USE_BRIDGE == 'across':
        bridge_fn = eth_bridge
    else:
        bridge_fn = orbiter_eth_bridge

    if BRIDGE_NETWORK == 'random':

        bridge_network = random.choice(['arbitrum', 'optimism'])
    else:
        bridge_network = BRIDGE_NETWORK

    web3_random = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))
    # ----------------------------------

    # --------------- Bridge to Arbitrum or OPT ---------------
    min_balance = get_token_balance(web3_random, wallet_address, '', True)

    # MIN required balance for transfer tx to OKX
    if min_balance <= 0.0001:
        min_balance = get_min_balance(bridge_network)

    params = ['zksync', bridge_network]
    run_script_one(bridge_fn, private_key, 'zksync', str(amount), params)

    add_to_stat(1, get_eth_price(amount))

    sleeping(MIN_SLEEP, MAX_SLEEP)
    # -------------------------------------------------

    # ------------------ Withdraw to OKX ------------------
    # Include orbiter max fees
    amount = round(amount - 0.0055, 4)
    amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, '', amount)
    amount = amount - min_balance
    sleeping(MIN_SLEEP, MAX_SLEEP)
    cprint("/-- Withdraw to OKX", "blue")
    transfer(web3_random, private_key, recipient_wallet, bridge_network, '', amount)
    # -----------------------------------------------------

    # ------------------ Write to CSV -------------------
    end_time = datetime.now()
    write_csv_volume(csv_name, [
        wallet_address,
        private_key,
        full_path + '->orbiter|accross->okx',
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
            for sub_account_num in range(1, 6):
                if len(config[f'OKX_SUB{sub_account_num}_API_KEY']) > 0:
                    cprint(f"/-- Check OKX subAccount {config[f'OKX_SUB{sub_account_num}_NAME']}", "blue")
                    acc_balance = get_okx_token_balance(sub_account_num, 'ETH')
                    if acc_balance >= amount * 0.99:
                        cprint(f"{acc_balance} ETH found, transfer to OKX main account", "green")
                        account = get_okx_account()
                        account.transfer("ETH", acc_balance, config[f'OKX_SUB{sub_account_num}_NAME'], 'master')
                        time.sleep(2)
                        break
        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue


def script_zksync_eralend():
    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()
    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    recipient_map = map_recipients(recipients, private_keys)

    try:
        for item in private_keys:
            web3 = get_web3(CHAINS['zksync']['rpc'], item['proxy'])
            private_key = item['private_key']
            one_wallet_zksync_eralend(web3, private_key, recipient_map[private_key])
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def one_wallet_zksync_eralend(web3, private_key, recipient_wallet):
    start_time = datetime.now()
    full_path = ''
    csv_name = f'volume_report'
    wallet_address = web3.eth.account.from_key(private_key).address
    zk_start_balance = get_token_balance(web3, wallet_address, '', True)

    # # ------------------ Withdraw ------------------
    pct = ZKSYNC_ETH_AMOUNT_PER_ACC * 0.02
    amount = round(ZKSYNC_ETH_AMOUNT_PER_ACC - random.uniform(0, pct), 4)
    cprint(f"/-- Withdraw {amount} to wallet: {wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.0004, 4), 'ETH', 'ETH-zkSync Era', 'okx')

    sleeping(MIN_SLEEP, MAX_SLEEP)
    # ------------------ Check wallet balance ------------------

    # if empty balance on zk
    if zk_start_balance <= 0.005:
        zk_start_balance = get_min_balance('zksync')
        amount = amount - zk_start_balance

    for step in range(VOLUME_REPEAT):
        routes = generate_route_data(True)
        # Generate swap path
        path = generate_path(web3, routes)
        full_path += path

        cprint(f"/-- Swap PATH: {path} step {step + 1}/{VOLUME_REPEAT}", "yellow")
        check_wait_web3_balance(web3, 'zksync', wallet_address, '', amount)
        sleeping(2, 3)

        # ------------- Supply and Borrow  ------------
        run_script_one(supply_eth_eralend, private_key, 'zksync', str(amount))
        sleeping(2, 3)
        run_script_one(enable_collateral, private_key, 'zksync')
        sleeping(2, 3)
        run_script_one(borrow_usdc, private_key, 'zksync')
        sleeping(2, 3)
        balance = check_wait_web3_balance(web3, 'zksync', wallet_address, ZKSYNC_TOKENS['USDC'], 1)

        add_to_stat(1, balance)
        # -------------------------------------------

        # -------------BODY of ROUTE-----------------
        for route in routes:
            grouped_tokens = route['grouped_tokens']
            params = grouped_tokens
            if route['params']:
                params = route['params'] + params
            run_script_one(route['function'], private_key, 'zksync', str(balance), params)
            balance = check_wait_web3_balance(web3, 'zksync', wallet_address, grouped_tokens[1], balance * 0.98)

            add_to_stat(1, balance)

            sleeping(MIN_SLEEP, MAX_SLEEP)
        # -------------BODY of ROUTE-----------------


        # Swap to USDC
        if grouped_tokens[1] != ZKSYNC_TOKENS['USDC']:
            run_script_one(route['function'], private_key, 'zksync', str(balance), [grouped_tokens[1],ZKSYNC_TOKENS['USDC']])
            balance = check_wait_web3_balance(web3, 'zksync', wallet_address, ZKSYNC_TOKENS['USDC'], balance * 0.98)
            sleeping(MIN_SLEEP, MAX_SLEEP)




        # ------------- REPAY USDC  ------------
        buy_full_repay(web3, private_key)
        sleeping(MIN_SLEEP, MAX_SLEEP)
        run_script_one(repay_usdc, private_key, 'zksync')
        sleeping(2, 3)
        run_script_one(withdraw_eth_eralend, private_key, 'zksync')

        # -------------------------------------------

        amount = amount * 0.9
        amount = check_wait_web3_balance(web3, 'zksync', wallet_address, '', amount)
        amount = amount - zk_start_balance

    # CHOOSE random network  and bridge
    if USE_BRIDGE == 'random':
        bridge_fn = random.choice([eth_bridge, orbiter_eth_bridge])
    elif USE_BRIDGE == 'across':
        bridge_fn = eth_bridge
    else:
        bridge_fn = orbiter_eth_bridge

    if BRIDGE_NETWORK == 'random':

        bridge_network = random.choice(['arbitrum', 'optimism'])
    else:
        bridge_network = BRIDGE_NETWORK

    web3_random = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))
    # ----------------------------------

    # --------------- Bridge to Arbitrum or OPT ---------------
    min_balance = get_token_balance(web3_random, wallet_address, '', True)

    # MIN required balance for transfer tx to OKX
    if min_balance <= 0.0001:
        min_balance = get_min_balance(bridge_network)

    params = ['zksync', bridge_network]
    run_script_one(bridge_fn, private_key, 'zksync', str(amount), params)

    add_to_stat(1, get_eth_price(amount))

    sleeping(MIN_SLEEP, MAX_SLEEP)
    # -------------------------------------------------

    # ------------------ Withdraw to OKX ------------------
    # Include orbiter max fees
    amount = round(amount - 0.0055, 4)
    amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, '', amount)
    amount = amount - min_balance
    sleeping(MIN_SLEEP, MAX_SLEEP)
    cprint("/-- Withdraw to OKX", "blue")
    transfer(web3_random, private_key, recipient_wallet, bridge_network, '', amount)
    # -----------------------------------------------------

    # ------------------ Write to CSV -------------------
    end_time = datetime.now()
    write_csv_volume(csv_name, [
        wallet_address,
        private_key,
        full_path + '->orbiter|accross->okx',
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
            for sub_account_num in range(1, 6):
                if len(config[f'OKX_SUB{sub_account_num}_API_KEY']) > 0:
                    cprint(f"/-- Check OKX subAccount {config[f'OKX_SUB{sub_account_num}_NAME']}", "blue")
                    acc_balance = get_okx_token_balance(sub_account_num, 'ETH')
                    if acc_balance >= amount * 0.99:
                        cprint(f"{acc_balance} ETH found, transfer to OKX main account", "green")
                        account = get_okx_account()
                        account.transfer("ETH", acc_balance, config[f'OKX_SUB{sub_account_num}_NAME'], 'master')
                        time.sleep(2)
                        break
        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue
