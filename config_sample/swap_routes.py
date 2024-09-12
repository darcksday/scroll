from modules.swaps.functions import *
from modules.swaps.config import TOKENS

ROUTES = {
    'open_ocean': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
            TOKENS['WBTC'],
            TOKENS['DAI'],
        },
        'function': open_ocean

    },

    'xy_swap': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
            TOKENS['WBTC'],
            TOKENS['DAI'],
        },
        'function': xy_swap

    },

    'swap_token_syncswap': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
        },
        'function': swap_token_syncswap

    },

    'swap_token_zebra': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
        },
        'function': swap_token_zebra

    },

    'swap_token_skydrome': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
        },
        'function': swap_token_skydrome

    },

    'swap_ambient': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
        },
        'function': swap_ambient

    },
    'swap_izumi': {
        'tokens': {
            TOKENS['USDC'],
            # TOKENS['USDT'],
        },
        'function': swap_izumi

    },

    'swap_sushi': {
        'tokens': {
            TOKENS['USDC'],
            TOKENS['USDT'],
        },
        'function': swap_sushi

    },

}