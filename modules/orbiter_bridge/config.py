ORBITER_MIN_AMOUNT = 0.0005

ORBITER_VALUE = {
    'ethereum': 9001,
    'optimism': 9007,
    'bsc': 9015,
    'arbitrum': 9002,
    'nova': 9016,
    'polygon': 9006,
    'polygon_zkevm': 9017,
    'zksync': 9014,
    'starknet': 9004,
    'linea': 9023,
    "scroll": 9019,
    "zkfair": 9038,
    "base": 9021,
    "zora": 9030,
    "taiko": 9020,
    "blast": 9040,
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

ORBITER_MIN_STABLE_TRANSFER = 3

ABI_ORBITER_TO_STARKNET = '[{"inputs":[{"internalType":"address payable","name":"_to","type":"address"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transfer","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transferERC20","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

USE_PAYMASTER=False
PAYMASTER_FEE_ADDRESS='0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'
PAYMASTER_CONTRACT='0x069246dFEcb95A6409180b52C071003537B23c27'
PAYMASTER_ABI=[{'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_minAllowance', 'type': 'uint256'}, {'internalType': 'bytes', 'name': '_innerInput', 'type': 'bytes'}], 'name': 'approvalBased', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bytes', 'name': 'input', 'type': 'bytes'}], 'name': 'general', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
