from config.multiple_routes import USE_FUNCTIONS
from helpers.cli import *
from helpers.factory import run_multiple, run_script
from modules.balance.module import interface_check_balance
from modules.contracts.module import interface_contracts
from modules.exchange_withdraw.module import interface_exchange_withdraw
from modules.orbiter_bridge.module import interface_orbiter_bridge
from modules.run_layer_zero.module import interface_usdv
from modules.swaps.functions import mint_origin_nft
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

            cprint(f'-------- BRIDGE/SWAP --------', 'blue')
            cprint(f'4. Orbiter Bridge', 'yellow')
            cprint(f'5. Swaps In dev...', 'yellow')

            cprint(f'-------- Own Contracts --------', 'blue')
            cprint(f'6. Interact  with contracts', 'yellow')

            cprint(f'-------- USDV Stargate --------', 'blue')
            cprint(f'7. Bridge USDT to USDV', 'yellow')


            cprint(f'8. LAYER ZERO: Bridge ${LZ_SCRIPT_USDT_AMOUNT}: Arbitrum > BSC > Bitget', 'yellow')
            cprint(f'-------- Orbiter Promotion --------', 'blue')

            cprint(f'9. Orbiter: Bridge {ETH_AMOUNT}ETH: OKX->[LINEA->RANDOM NETWORKS->LINEA]->OKX', 'yellow')

            cprint(f'10. Mint origin nft', 'yellow')


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
                run_script(mint_origin_nft, 'scroll', 0,[])
                break





            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue


    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
