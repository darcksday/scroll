from modules.swaps.functions import *

MIN_TRANSACTION_AMOUNT = 0.0001
MIN_STABLE = 0.1
TOKENS = {
    "USDC": "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4",
    "USDT": "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df",
    "DAI": "0xcA77eB3fEFe3725Dc33bccB54eDEFc3D9f764f97",
    "WBTC": "0x3C1BCa5a656e69edCD0D4E36BEbb3FcDAcA60Cf1",
    "WETH": "0x5300000000000000000000000000000000000004",
}

USE_DEXES=[
    swap_token_syncswap,
    swap_token_skydrome,
    swap_ambient,
    swap_izumi,
    swap_sushi
]