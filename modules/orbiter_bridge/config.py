ORBITER_MIN_AMOUNT = 0.0005

ORBITER_AMOUNT = {
    'ethereum': 0.000000000000009001,
    'optimism': 0.000000000000009007,
    'bsc': 0.000000000000009015,
    'arbitrum': 0.000000000000009002,
    'nova': 0.000000000000009016,
    'polygon': 0.000000000000009006,
    'polygon_zkevm': 0.000000000000009017,
    'zksync': 0.000000000000009014,
    'starknet': 0.000000000000009004,
    'linea': 0.000000000000009023,
    'scroll':0.000000000000009019,
    'zkfair':0.000000000000009038,
    'base':0.000000000000009021,
}

ORBITER_AMOUNT_STR = {
    'ethereum': '9001',
    'optimism': '9007',
    'bsc': '9015',
    'arbitrum': '9002',
    'nova': '9016',
    'polygon': '9006',
    'polygon_zkevm': '9017',
    'zksync': '9014',
    'starknet': '9004',
    'linea': '9023',
    "scroll": "9019",
    "zkfair": "9038",
    "base": "9021",
}

CONTRACTS_ORBITER_TO_STARKNET = {
    'ethereum': '0xd9d74a29307cc6fc8bf424ee4217f1a587fbc8dc',
    'optimism': '',
    'bsc': '',
    'arbitrum': '0xd9d74a29307cc6fc8bf424ee4217f1a587fbc8dc',
    'nova': '',
    'polygon': '',
    'polygon_zkevm': '',
    'zksync': '',
    'zksync_lite': '',
    'linea': '',
}

ORBITER_MIN_STABLE_TRANSFER = 1

ABI_ORBITER_TO_STARKNET = '[{"inputs":[{"internalType":"address payable","name":"_to","type":"address"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transfer","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transferERC20","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
