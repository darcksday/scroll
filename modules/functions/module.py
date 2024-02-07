from helpers.cli import print_input_amounts_range
from helpers.factory import run_script, run_random_swap, run_multiple, call_function
from helpers.settings_helper import get_private_keys
from modules.functions.functions import *
from modules.landings.functions import supply_eth_layerbank, withdraw_eth_layerbank
from modules.swaps.functions import *


def interface_others():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Send email (cheap transaction) / dMail', 'yellow')
            cprint(f'2. Safe create wallet', 'yellow')
            cprint(f'3. RANDOM Mint nfts2me (need add contracts)', 'yellow')
            cprint(f'4. RANDOM Mint ZkStars NFT', 'yellow')
            cprint(f'5. Mint origin nft', 'yellow')
            cprint(f'7. Deposit LayerBank', 'yellow')
            cprint(f'8. Withdraw LayerBank', 'yellow')
            cprint(f'9. Create Nft Collection Omnisea', 'yellow')


            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                # Send email (cheap transaction)
                run_script(send_email, 'scroll', '')

            elif option == '2':
                run_script(safe_create, 'scroll', '')


            elif option == '3':
                contracts = [""]

                prt_keys = get_private_keys()
                if USE_SHUFFLE:
                    random.shuffle(prt_keys)

                for item in prt_keys:
                    params = ["scroll", random.choice(contracts)]
                    call_function(item, mint_nfts2_me, 'scroll', "0.00005", params)
                    sleeping(MIN_SLEEP, MAX_SLEEP)


            elif option == '4':
                run_script(mint_zkstars, 'scroll', '')


            elif option == '5':
                run_script(mint_origin_nft, 'scroll', 0,[])
                break


            elif option == '7':
                amount_str = print_input_amounts_range('Deposit amount')
                run_script(supply_eth_layerbank, 'scroll', amount_str)


            elif option == '8':
                run_script(withdraw_eth_layerbank, 'scroll', 0)


            elif option == '9':
                run_script(create_omnisea_collection, 'scroll', 0)


            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
