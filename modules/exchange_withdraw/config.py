from dotenv import dotenv_values

config = dotenv_values("config/.env")

# binance | okx | mexc | kucoin | huobi | bybit | bitget

CEX_KEYS = {
    'binance': {
        'api_key': config['BINANCE_API_KEY'], 'api_secret': config['BINANCE_API_SECRET']
    },
    # 'mexc': {
    #     'api_key': config['MEXC_API_KEY'], 'api_secret': config['MEXC_API_SECRET']
    # },
    # 'kucoin': {
    #     'api_key': config['KUCOIN_API_KEY'], 'api_secret': config['KUCOIN_API_SECRET'],
    #     'password': config['KUCOIN_PASSWORD']
    # },
    # 'huobi': {
    #     'api_key': config['HUOBI_API_KEY'], 'api_secret': config['HUOBI_API_SECRET']
    # },
    # 'bybit': {
    #     'api_key': config['BYBIT_API_KEY'], 'api_secret': config['BYBIT_API_SECRET']
    # },
    'okx': {
        'api_key': config['OKX_API_KEY'], 'api_secret': config['OKX_API_SECRET'],
        'password': config['OKX_PASSWORD']
    },

    'bitget': {
        'api_key': config['BITGET_API_KEY'], 'api_secret': config['BITGET_API_SECRET'],
        'password': config['BITGET_PASSWORD']
    },

}

CEX_DEFAULT_TOKENS = ['ETH', 'USDT', 'USDC', 'BNB', 'MATIC', 'AVAX', 'APT', 'GLMR', 'MOVR', 'FTM', 'ONE', 'METIS',
                      'CELO', 'TENET']

OKX_CHAIN_MAPPING = {
    'ETH': 'ERC20',
    'MATIC': 'Polygon',
    'AVAXC': 'Avalanche C',
    'ARBITRUM': 'Arbitrum One',
    'OPTIMISM': 'Optimism',
    'FTM': 'Fantom',
    'ZkSync': 'zkSync Era',
    'CORE': 'CORE',
    'MOVR': 'Moonriver',
    'HARMONY': 'Harmony',
    'CELO': 'CELO',
}

BITGET_CHAIN_MAPPING = {
    'ETH': 'ERC20',
    'MATIC': 'Polygon',
    'AVAXC': 'C-Chain',
    'ARBITRUM': 'ArbitrumOne',
    'OPTIMISM': 'Optimism',
    'BSC': 'BEP20',
    'METIS': 'MetisToken',
    'TENET': 'TENETEvm',

}
