HYPERLANE_MIN_AMOUNT = 0.00001
HYPERLANE_MAX_AMOUNT = 0.5

HYPERLANE_DOMAINS = {
    "optimism": 10,
    "arbitrum": 42161,
    "base": 8453,
    "scroll": 534352,
    "mode": 34443,
}

# Адреса контрактов
HYPERLANE_CONTRACTS = {
    "optimism": "0xc110e7faa95680c79937ccaca3d1cab7902be25e",
    "arbitrum": "0x233888F5Dc1d3C0360b559aBc029675290DAFa70",
    "base": "0x0cb0354E9C51960a7875724343dfC37B93d32609",
    "scroll": "0xc0faBF14f8ad908b2dCE4C8aA2e7c1a6bD069957",
    "mode": "0x9970cB23f10dBd95B8A3E643f3A6A6ABB6f3cB9b",
}

# ABI контракта
HYPERLANE_ABI = [
    {
        "type": "function",
        "name": "quoteBridge",
        "constant": True,
        "stateMutability": "view",
        "payable": False,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"}
        ],
        "outputs": [
            {"type": "uint256", "name": "fee"}
        ]
    },
    {
        "type": "function",
        "name": "bridgeETH",
        "constant": False,
        "stateMutability": "payable",
        "payable": True,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"}
        ],
        "outputs": [
            {"type": "bytes32", "name": "messageId"}
        ]
    },
    {
        "type": "function",
        "name": "bridgeWETH",
        "constant": False,
        "stateMutability": "payable",
        "payable": True,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"}
        ],
        "outputs": [
            {"type": "bytes32", "name": "messageId"}
        ]
    }
]