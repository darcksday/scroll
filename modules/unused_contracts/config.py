from modules.functions.config import DMAIL_CONTRACT, SAFE_CONTRACT, NFT_ORIGINS_CONTRACT, OMNISEA_CONTRACT, RUBYSCORE_VOTE_CONTRACT
from modules.functions.functions import create_omnisea_collection, mint_origin_nft, mint_zkstars, safe_create, send_email, mint_nfts2_me, \
    rubyscore
from modules.landings.config import LAYERBANK_CONTRACT
from modules.landings.functions import withdraw_eth_layerbank, supply_eth_layerbank
from modules.run_layer_zero.config import MERKLEY_BRIDGE_CONTRACTS_V2
from modules.run_layer_zero.functions import merkly_v2
from modules.swaps.config import OPENOCEAN_CONTRACT, XYSWAP_CONTRACT, SYNCSWAP_CONTRACTS, ZEBRA_CONTRACTS, SKYDROME_CONTRACTS, \
    AMBIENT_CONTRACT, IZUMI_CONTRACTS
from modules.swaps.functions import open_ocean, xy_swap, swap_token_syncswap, swap_token_zebra, swap_token_skydrome, swap_ambient, \
    swap_izumi

ALL_FUNCTIONS = {
    OPENOCEAN_CONTRACT["router"]: open_ocean,
    # XYSWAP_CONTRACT: xy_swap,
    # LAYERBANK_CONTRACT: [supply_eth_layerbank, withdraw_eth_layerbank],

    SYNCSWAP_CONTRACTS['router']: swap_token_syncswap,
    ZEBRA_CONTRACTS['router']: swap_token_zebra,
    SKYDROME_CONTRACTS['router']: swap_token_skydrome,
    AMBIENT_CONTRACT['router']:swap_ambient,
    IZUMI_CONTRACTS['router']:swap_izumi,
    DMAIL_CONTRACT: send_email,
    SAFE_CONTRACT: safe_create,
    "0x609c2f307940b8f52190b6d3d3a41c762136884e": mint_zkstars,
    NFT_ORIGINS_CONTRACT: mint_origin_nft,
    OMNISEA_CONTRACT: create_omnisea_collection,
    "0x0B0EBDafA49e676A60445EcBdD4DdF5ABc83a54A": mint_nfts2_me,
    "0x267412c94F78941F93a33E292fa7Bbf849751844": mint_nfts2_me,
    "0x805AD7aE07c3eE6792e6CE105E2cc91F015294D7": mint_nfts2_me,
    "0xAe7B1F56A251B1c608a5Ec536791955D2844C7c3": mint_nfts2_me,
    "0xD20388fFEB7A761E775ECEbF05197323ab3aB7F8": mint_nfts2_me,
    "0xBA396fF993947b06945CB5Ed9dEc31a8fc981F5A": mint_nfts2_me,
    "0x874ADe3582354D3A30Bb484607717e6e61b8619B": mint_nfts2_me,
    MERKLEY_BRIDGE_CONTRACTS_V2['scroll']: merkly_v2,
    RUBYSCORE_VOTE_CONTRACT: rubyscore,




}
