from helpers.cli import print_input_amounts_range, print_input_network
from helpers.csv_helper import start_csv
from helpers.factory import run_script, run_random_swap, run_multiple, call_function
from helpers.settings_helper import get_private_keys
from modules.functions.functions import *
from modules.landings.functions import supply_eth_layerbank, withdraw_eth_layerbank, enable_collateral, borrow_usdc, repay_usdc
from modules.run_layer_zero.functions import merkly_v2
from modules.swaps.functions import *


def interface_others():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Send email (cheap transaction) / dMail', 'yellow')
            cprint(f'2. Safe create wallet', 'yellow')
            cprint(f'3. RANDOM Mint nfts2me', 'yellow')
            cprint(f'4. RANDOM Mint ZkStars NFT', 'yellow')
            cprint(f'5. Mint origin nft', 'yellow')
            cprint(f'7. Deposit LayerBank', 'yellow')
            cprint(f'8. Withdraw LayerBank', 'yellow')
            cprint(f'9. Create Nft Collection Omnisea', 'yellow')
            cprint(f'10. Enable Collateral Layerbank', 'yellow')
            cprint(f'11. Borrow USDC Layerbank', 'yellow')
            cprint(f'12. Repay USDC Layerbank', 'yellow')
            cprint(f'13. Vote Rubyscore', 'yellow')
            cprint(f'14. Bridge scroll.io/bridge', 'yellow')

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
                contracts = [
                    "0x0B0EBDafA49e676A60445EcBdD4DdF5ABc83a54A",
                    "0x267412c94F78941F93a33E292fa7Bbf849751844",
                    "0x805AD7aE07c3eE6792e6CE105E2cc91F015294D7",
                    "0xAe7B1F56A251B1c608a5Ec536791955D2844C7c3",
                    "0xD20388fFEB7A761E775ECEbF05197323ab3aB7F8",
                    "0xBA396fF993947b06945CB5Ed9dEc31a8fc981F5A",
                    "0x874ADe3582354D3A30Bb484607717e6e61b8619B",
                ]

                csv_name = 'nfts2me'
                start_csv(csv_name)
                prt_keys = get_private_keys()
                if USE_SHUFFLE:
                    random.shuffle(prt_keys)

                for item in prt_keys:
                    params = ["scroll", random.choice(contracts)]
                    call_function(item, mint_nfts2_me, 'scroll', "0.0001", params, csv_name)
                    sleeping(MIN_SLEEP, MAX_SLEEP)


            elif option == '4':
                run_script(mint_zkstars, 'scroll', '')


            elif option == '5':
                run_script(mint_origin_nft, 'scroll', 0, [])
                break


            elif option == '7':
                amount_str = print_input_amounts_range('Deposit amount')
                run_script(supply_eth_layerbank, 'scroll', amount_str)


            elif option == '8':
                run_script(withdraw_eth_layerbank, 'scroll', 0)


            elif option == '9':
                run_script(create_omnisea_collection, 'scroll', 0)

            elif option == '10':
                run_script(enable_collateral, 'scroll', 0)


            elif option == '11':
                amount_str = print_input_amounts_range('Borrow amount')

                run_script(borrow_usdc, 'scroll', amount_str)


            elif option == '12':

                run_script(repay_usdc, 'scroll', 0)


            elif option == '13':

                run_script(rubyscore, 'scroll', 0)


            elif option == '14':

                amount_str = print_input_amounts_range('Deposit amount')
                run_script(deposit, 'ethereum', amount_str, [])

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
