# 2 ETH max!
from modules.landings.functions import supply_eth_eralend, withdraw_eth_eralend, supply_eth_layerbank, withdraw_eth_layerbank, \
    supply_eth_0vix, withdraw_supply_eth_0vix

ETH_AMOUNT = 1.97

NETWORKS=[
    'zksync',
    'scroll',
    'scroll',
    'scroll',
    # 'nova',
    # 'base',
]

ADDITIONAL_FUNCTIONS={
    'zksync': [
        [supply_eth_eralend, withdraw_eth_eralend],
    ],
    'scroll': [
        [supply_eth_layerbank, withdraw_eth_layerbank],
    ],
    'polygon_zkevm': [
        [supply_eth_0vix, withdraw_supply_eth_0vix],
    ],




}

# arbitrum or optimism

END_NETWORK=''


