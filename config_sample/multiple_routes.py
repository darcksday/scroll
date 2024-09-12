from helpers.factory import run_random_swap
from modules.functions.functions import safe_create, send_email, mint_zkstars, mint_origin_nft, create_omnisea_collection
from modules.landings.functions import supply_eth_layerbank, withdraw_eth_layerbank
from modules.swaps.functions import open_ocean, xy_swap, swap_token_syncswap, swap_token_zebra, swap_token_skydrome, swap_ambient

"""
You can use:
run_random_swap
safe_create
send_email
mint_zkstars
mint_origin_nft
supply_eth_layerbank
withdraw_eth_layerbank

open_ocean
xy_swap
swap_token_syncswap
swap_token_zebra
swap_token_skydrome
swap_ambient


______________________________________________________
You can add functions to [] ,
example [module_1, module_2, [module_3, module_4], module 5]
The script will start module 3 and 4 sequentially, others modules 
module_1,module_2,module_5 will start randomly

You can duplicate function for example: [run_random_swap,run_random_swap,run_random_swap]
for swaps in different protocols

"""

USE_FUNCTIONS = [
    [
        open_ocean,
        xy_swap,
        swap_token_syncswap,
        swap_token_zebra,
        swap_token_skydrome,

        run_random_swap,
        swap_ambient,

        send_email,
        safe_create,
        mint_zkstars,
        create_omnisea_collection,
        # mint_origin_nft,
        # [
        #     supply_eth_layerbank,
        #     withdraw_eth_layerbank,
        # ],




    ]

]
