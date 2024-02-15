from config.multiple_routes import USE_FUNCTIONS
from config.swap_routes import ROUTES
from helpers.cli import *
from helpers.factory import run_multiple, run_script, run_unused_fn, run_random_swap
from modules.balance.module import interface_check_balance
from modules.contracts.module import interface_contracts
from modules.exchange_withdraw.module import interface_exchange_withdraw
from modules.functions.module import interface_others
from modules.orbiter_bridge.module import interface_orbiter_bridge
from modules.run_layer_zero.module import interface_usdv
from modules.swaps.module import interface_swaps
from modules.transfer.module import interface_transfer
from config.lz_config  import *
from scripts.layer_zero.module import script_usdv_layer_zero
from config.orbiter_config  import ETH_AMOUNT
from scripts.orbiter.module import script_orbiter_eth

if __name__ == '__main__':
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'0. Exit', 'yellow')
            cprint(f'1. Check Balances', 'yellow')
            cprint(f'2. Transfer Tokens', 'yellow')
            cprint(f'3. Exchange Withdraw', 'yellow')

            cprint(f'-------- BRIDGE/SWAP/NFT/LEND/etc --------', 'blue')
            cprint(f'4. Orbiter Bridge', 'yellow')
            cprint(f'5. Swaps on Dex', 'yellow')
            cprint(f'10. Nft/Lendings/DMAIL/etc', 'yellow')

            cprint(f'-------- Own Contracts --------', 'blue')
            cprint(f'6. Interact  with contracts', 'yellow')

            cprint(f'-------- USDV Stargate --------', 'blue')
            cprint(f'7. Bridge USDT to USDV', 'yellow')


            cprint(f'8. LAYER ZERO: Bridge ${LZ_SCRIPT_USDT_AMOUNT}: Arbitrum > Polygon > BSC > Bitget', 'yellow')
            cprint(f'-------- Orbiter Promotion --------', 'blue')

            cprint(f'9. Orbiter: Bridge {ETH_AMOUNT}ETH: OKX->[LINEA->RANDOM NETWORKS->LINEA]->OKX', 'yellow')

            cprint(f'---------- Random Swaps ----------', 'blue')
            cprint(f'11. Swap ETH <=> Random Token / Random Dex',
                   'yellow')
            cprint(f'---------- Multiple Functions ----------', 'blue')
            cprint(f'12. Run multiple functions configured in config/multiple_routes.py',
                   'yellow')

            # cprint(f'---------- Unused Functions ----------', 'blue')
            # cprint(f'13. Find and run unused contract for wallet ',
            #        'yellow')

            # cprint(f'10. Orbiter: Bridge {USDT_AMOUNT}USDC: OKX->OP[LINEA->RANDOM NETWORKS->LINEA]->OP->OKX', 'yellow')



            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break
            elif option == '1':
                interface_check_balance()
                break
            elif option == '2':
                interface_transfer()
                break
            elif option == '3':
                interface_exchange_withdraw()
                break



            elif option == '4':
                interface_orbiter_bridge()
                break


            elif option == '5':
                interface_swaps()
                break



            elif option == '6':
                interface_contracts()
                break


            elif option == '7':
                interface_usdv()
                break


            elif option == '8':
                script_usdv_layer_zero()
                break

            elif option == '9':
                script_orbiter_eth()
                break


            elif option == '10':
                interface_others()
                break


            elif option == '11':
                amount_str = print_input_amounts_range('Swap amount ETH')
                run_random_swap(ROUTES, 'scroll', amount_str)

            elif option == '12':
                run_multiple(USE_FUNCTIONS, 'scroll')
                break


            # elif option == '13':
            #     run_unused_fn('scroll')
            #     break


            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue


    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
