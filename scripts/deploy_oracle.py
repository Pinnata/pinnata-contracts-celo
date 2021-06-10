from brownie import accounts, ERC20KP3ROracle, UniswapV2Oracle, UbeswapV1Oracle, Contract

def main():
    # deployer = accounts.load('deployer')

    # Enable after contracts have been deployed
    # Replace the contract addresses with the ones from the first deploy
    ubeswap_oracle = Contract('0xFCD32eb8B34F93b593b38e512584223Fcc27F079')
    oracle = Contract('0xb921129859c9271Db3862B55818D825cA4d47cB1')
    lp_oracle = Contract('0x238EbFcd168f96807EBFE46Ae4Db93b11D35e5b8')

    # # mcUSD - cUSD
    # ubeswap_oracle.update(
    #         '0x64dEFa3544c695db8c535D289d843a189aa26b98', 
    #         '0x765DE816845861e75A25fCA122bb6898B8B1282a',
    #         {'from': deployer})
    # # CELO - cUSD
    # ubeswap_oracle.update(
    #         '0x471EcE3750Da237f93B8E339c536989b8978a438', 
    #         '0x765DE816845861e75A25fCA122bb6898B8B1282a',
    #         {'from': deployer})

# ----------------- #

    # Enable when deploying for the first time
    # ubeswap_oracle = UbeswapV1Oracle.deploy({'from': deployer});
    # oracle = ERC20KP3ROracle.deploy(
    #         ubeswap_oracle,
    #     {'from': deployer},
    # )
    # lp_oracle = UniswapV2Oracle.deploy(oracle, {'from': deployer})
    # # mcUSD - cUSD
    # ubeswap_oracle.addPair(
    #         '0x64dEFa3544c695db8c535D289d843a189aa26b98', 
    #         '0x765DE816845861e75A25fCA122bb6898B8B1282a',
    #         {'from': deployer})
    # CELO - cUSD
    # ubeswap_oracle.addPair(
    #         '0x471EcE3750Da237f93B8E339c536989b8978a438', 
    #         '0x765DE816845861e75A25fCA122bb6898B8B1282a',
    #         {'from': deployer})

    # cUSD
    data = oracle.getCELOPx('0x765DE816845861e75A25fCA122bb6898B8B1282a')
    print(data)
    print(1 / (data / (2**112)))

    # CELO
    data = oracle.getCELOPx('0x471EcE3750Da237f93B8E339c536989b8978a438')
    print(data)
    print(1 / (data / (2**112)))

    # CELO-cUSD
    data = lp_oracle.getCELOPx('0x1e593f1fe7b61c53874b54ec0c59fd0d5eb8621e')
    print(data)
    print(data / (2**112))
