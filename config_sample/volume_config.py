from modules.swaps.functions import *



# '4-6' || 6
VOLUME_REPEAT='4-6'

#Max 5000$ in ETH for Nitro | Min 0.2 ETH
VOLUME_ETH_AMOUNT = 1.5

USE_DEXES=[
    swap_token_syncswap,
    swap_izumi,
    open_ocean,
    swap_sushi,
    # xy_swap

]

# False or :'0.018-0.021'
BALANCE_LEFT ='0.018-0.021'


# nitro|orbiter|random
START_BRIDGE='orbiter'
# arbitrum|optimism|linea|random
START_NETWORK='linea'

# arbitrum|optimism|linea|random
END_NETWORK = 'linea'
# nitro|orbiter|random
END_BRIDGE = 'orbiter'

MAX_DEVIATION_PCT=2