from termcolor import cprint
from config.settings import ZKSYNC_ETH_AMOUNT_PER_ACC
from scripts.zksync.bitget import script_zksync_bitget
from scripts.zksync.okx import script_zksync_okx, script_zksync_eralend


def interface_zksync_volume():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. {ZKSYNC_ETH_AMOUNT_PER_ACC} ETH OKX > zkSync >(Odos<->1inch<->OpenOcean)->(orbiter|accross)->okex', 'yellow')
            cprint(f'2. {ZKSYNC_ETH_AMOUNT_PER_ACC} ETH OKX > zkSync >eralend->(Odos<->1inch<->OpenOcean)->(orbiter|accross)->okex',
                   'yellow')

            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                script_zksync_okx()
                break


            elif option == '2':
                script_zksync_eralend()
                break

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
