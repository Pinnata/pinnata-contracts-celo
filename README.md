# Alpha Homora v2 🧙‍♂️

## Alfajores Addresses 

celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'

cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'

ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'

  HomoraBank deployed at: 0x8772D538785f9dc2a8b1356D4550320E93f4A616

  CoreOracle deployed at: 0x0286530271720D1B4538e92c7Cc0922D68A053f2

 ProxyOracle deployed at: 0x4cf091fd046B6f21Dd5bdf490Fb274315e77f028

  UniswapV2Oracle deployed at: 0xda6Cb2cB539257108780e3eE728b0005DedD3152

  UbeswapV1Oracle deployed at: 0xe425a51a129FDeE65bcc2F7b477634E2724c007e

  ERC20KP3ROracle deployed at: 0xde98f3348C35DB4E2F1757C511e0960c8797Db4D

  WERC20 deployed at: 0x219F5B0BCBCb2B86068DC97BbdF1b4672d19Aa2c

  UniswapV2SpellV1 deployed at: 0x9F9C8Fe9BC1f28370d947bce6a264aFa4feD5Ec8

  celo   SafeBox deployed at: 0x970e26ff0b86145b919e4a54B8a25e4677b0beBC

  cusd   SafeBox deployed at: 0x461ca72eF491B00b0Ac6f6f9Fe30359ef187a6D9

  cube   SafeBox deployed at: 0x8FaADa58C2605f7884340EF36eD4C48eEC9e7D2C


Comptroller: 0x115308bBCBd3917033EcE55aC35C92a279A7055D
dCELO: 0xB01BCdB6e90C216Ee2Cb15bF97B97283c70932d6
dcUSD: 0x0A59FBA6810D5208b26CE294f5Eb2D121673D782
dUBE: 0x60403187a1850688deE07C8BdeBE4355Ced1d081

TL;DR. Here's what V2 will support:

- Multi assets lending and borrowing (with huge leverage for stablecoin farming!)
- More farming pools beyond just Uniswap (think Balancer, Curve, etc)
- Can keep the farming assets and not just dumping
- No more EOA only = more composability
- You can bring your own LP tokens too = more flexibility
- Native flashloan support

## Protocol Summary

Alpha Homora v2 is an upgrade from Alpha Homora v1, a leveraged yield-farming product. Here are some key features:

<!-- - In v2, vaults (e.g. ibETH) no longer exist. The protocol instead integrates with existing lending protocol. Whenever a user wants to borrow funds (on leverage) to yield farm, Alpha Homora will borrow from the lending protocol. -->

- In v2, other assets are borrow-able (not only ETH like in v1), including stablecoins like USDT, USDC, DAI.
- In v2, users may also borrow supported LP tokens to farm more.
- Users can also bring their own LP tokens and add on to their positions.
- Each "spell" defines how the protocol interacts with farming pools, e.g. Uniswap spell, Sushiswap spell, Curve spell.
  - Spell functions include e.g. `addLiquidity`, `removeLiquidity`.
  - This is different from v1, where each pool has its own spell (goblin).
- Reward tokens e.g. UNI, SUSHI were sold and reinvested to users' positions in v1. Instead, users can now claim reward tokens.
- Adjustable positions - users can adjust their existing positions by supply more assets, borrow more assets, or repay some debts.
  - As long as the collateral credit >= borrow credit. Otherwise, the position is at liquidation risk.

## Protocol Components

- HomoraBank
  - Store each position's collateral tokens (in the form of wrapped LP tokens)
  - Users can execute "spells", e.g. opening a new position, closing/adjusting existing position.
- Caster
  - Intermediate contract that just calls another contract function (low-level call) with provided data (instead of bank), to prevent attack.
  - Doesn't store any funds
- Spells (e.g. Uniswap/Sushiswap/Curve/...)
  - Define how to interact with each pool
  - Execute `borrow`/`repay` assets by interacting with the bank, which will then interact with the lending protocol.

### Component Interaction Flow

1. User -> HomoraBank.
   User calls `execute` to HomoraBank, specifying which spell and function to use, e.g. `addLiquidity` using Uniswap spell.
2. HomoraBank -> Caster.
   Forward low-level spell call to Caster (doesn't hold funds), to prevent attacks.
3. Caster -> Spell.
   Caster does low-level call to Spell.
4. Spell may call HomoraBank to e.g. `doBorrow` funds, `doTransmit` funds from users (so users can approve only the bank, not each spell), `doRepay` debt. Funds are then sent to Spell, to execute pool interaction.
5. Spells -> Pools.
   Spells interact with Pools (e.g. optimally swap before supplying to Uniswap, or removing liquidity from the pool and pay back some debts).
6. (Optional) Stake LP tokens in wrapper contracts (e.g. WMasterChef for Sushi, WLiquidityGauge for Curve, WStakingRewards for Uniswap + Balancer).
7. Spell may put collateral back to HomoraBank.
   If the spell funtion called is e.g. to open a new position, then the LP tokens will be stored in HomoraBank.

## Example Execution

### AddLiquidity

1. User calls `execute(0, USDT, WETH, data)` on HomoraBank contract. `data` encodes UniswapSpell function call with arguments (including how much of each asset to supply, to borrow, and slippage control settings).
2. HomoraBank forwards data call to Caster.
3. Caster does low-level call (with `data`, which encodes `addLiquidity` function call with arguments) to UniswapSpell.
4. UniswapSpell executes `addLiquidityWERC20`
   - `doTransmit` desired amount of assets the user wants to supply
   - `doBorrow` from the lending protocol
   - Optimally swap assets and add liquidity to Uniswap pool
   - Wrap LP tokens to wrapper WERC20 (to get ERC1155)
   - `doPutCollateral` wrapped tokens back to HomoraBank
   - Refund leftover assets to the user.

> For **Uniswap** pools with staking rewards, use `addLiquidityWStakingRewards` function.
> For **Sushiswap** pools with staking in masterchef, use `addLiqudityWMasterChef` function.
> For **Balancer** pools with staking rewards, use `addLiquidityWStakingRewards` function.
> For all **Curve** pools, use `addLiquidity[N]` (where `N` is the number of underlying tokens). The spell will auto put in Curve's liquidity gauge.

## Oracle

Prices are determined in ETH.

- For regular assets, asset prices can be derived from Uniswap pool (with WETH), or Keep3r.
- For LP tokens, asset prices will determine the optimal reserve proportion of the underlying assets, which are then used to compute the value of LP tokens. See `UniswapV2Oracle.sol` for example implementation.
