from modules.contracts.functions import stake_unused, withdraw_unused
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
    # OPENOCEAN_CONTRACT["router"]: open_ocean,
    # XYSWAP_CONTRACT: xy_swap,
    # # LAYERBANK_CONTRACT: [supply_eth_layerbank, withdraw_eth_layerbank],
    #
    # SYNCSWAP_CONTRACTS['router']: swap_token_syncswap,
    # # ZEBRA_CONTRACTS['router']: swap_token_zebra,
    # SKYDROME_CONTRACTS['router']: swap_token_skydrome,
    # AMBIENT_CONTRACT['router']: swap_ambient,
    # IZUMI_CONTRACTS['router']: swap_izumi,
    DMAIL_CONTRACT: send_email,
    SAFE_CONTRACT: safe_create,
    # "0x874ADe3582354D3A30Bb484607717e6e61b8619B": mint_nfts2_me,
    # MERKLEY_BRIDGE_CONTRACTS_V2['scroll']: merkly_v2,
    RUBYSCORE_VOTE_CONTRACT: rubyscore,


    '0x094BF23d9b098328337C0FB902B3fb8C7d5F2c9C':[stake_unused, withdraw_unused],
    '0x52FEF10d05D806D6DC58dd7bc263C27B586A8159':[stake_unused, withdraw_unused],
    '0x52c8e26D3c625ac40d4f36e7DF106A06Fe059Db9':[stake_unused, withdraw_unused],
    '0x3F37EBC9EFB6C0acB36aA7C8e1F3f0aC2c2e1381':[stake_unused, withdraw_unused],
    '0x95b9Ba4d63c3746ae453001d21c027EbfE863e7E':[stake_unused, withdraw_unused],
    '0x3c646E4348C0a8a15f1ab777631d8C70faC17be6':[stake_unused, withdraw_unused],
    '0x8C988FE1b642FC01C55FedB57dD1dC24e8aD32e2':[stake_unused, withdraw_unused],
    '0x846A78e3484C27Cd55452Db74EA5446AF9117500':[stake_unused, withdraw_unused],
    '0x5F65F338d736Ec4296b1D0c1fa20363243dEE4bA':[stake_unused, withdraw_unused],
    '0x7a0928582C8754EE40019EbCfaF80909b8EF14cb':[stake_unused, withdraw_unused],
    '0x834D925251988cf229cE006aDf99661bb5dEd519':[stake_unused, withdraw_unused],
    '0x6BA5C59f10a4e91c6528959926c66585Bfb71a44':[stake_unused, withdraw_unused],
    '0x9cc41A4A9B741076fB02aB41885E311E7e2a68aC':[stake_unused, withdraw_unused],
    '0x4a9B264C1cF02988680591CA84f82105CdBA70fc':[stake_unused, withdraw_unused],
    '0x643Ef03B53715e338775E62C6051512D1f462502':[stake_unused, withdraw_unused],
    '0x7ffaD2C659EE4470100340469aCD06ca136c167D':[stake_unused, withdraw_unused],
    '0x432A8dAC9488492F802ec062785067c9a94Ff838':[stake_unused, withdraw_unused],
    '0x60F4736daA153C6e302496F023137AB76299F475':[stake_unused, withdraw_unused],
    '0x0578C678Cc07728f8C63C91DD5FA24f1Ce9b58A1':[stake_unused, withdraw_unused],
    '0xE910fcE8e74B40CcAD70f577019D5bBA54Fb2085':[stake_unused, withdraw_unused],
    '0xf4dCC4495C85f9F1b5A0650bE228225433e4022E':[stake_unused, withdraw_unused],
    '0x89118e0Aa1CD5BB166c4001004aA04BF54C7c352':[stake_unused, withdraw_unused],
    '0xE9611E3700de72b58569E69B33eC1cB364A49399':[stake_unused, withdraw_unused],
    '0xf6a286CC67C9D4e4760147a3D88b35d648845292':[stake_unused, withdraw_unused],
    '0xe681B1d9826Fd01f45c537504cE856803567b9D4':[stake_unused, withdraw_unused],
    '0xFFdd56c3B425C0431b230cD8473eAaA98EbC73ba':[stake_unused, withdraw_unused],
    '0x2FA360C801b3E11225cb7a1E3821A26e90e2c1e0':[stake_unused, withdraw_unused],
    '0x7CBA85e97e32d7756C4692912195A6B0b6AB26C7':[stake_unused, withdraw_unused],
    '0x5B191faE12d40dB0008CA99BBE53087Bb4aea3A6':[stake_unused, withdraw_unused],
    '0x18d1D4D9E9bf9C21a93592Fb298374DDBc18480c':[stake_unused, withdraw_unused],
    '0xf2550d2354d96fC6438e3f62f52eB8532442CA53':[stake_unused, withdraw_unused],























}
