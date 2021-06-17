# Alpha Homora v2 🧙‍♂️

## Alfajores Addresses 
HomoraBank: 0x05c9E9fBE4093f3F2f88328F559f82FF606238fD
UniswapV2Spell: 0xFf7C1C15De3eCcF25F2Ae98cdb4aC7aBaBE161D6
Comptroller: 0x56383495CdC75B07A1dee50Ede5EC28Ad014c134
PriceOracle: 0xB1F856123812C650E2DD76F5618eDa386CB1B8F6
dCELO: 0x5e3A00F9DaB4b241780Fbc11529Db14e1C8D2f1D
dcUSD: 0x136dE673A9d27301aBa3390B5CFF4d56Bc11d799
dcEUR: 0xFcb4DAe85306d73285a2084884D7734cb507D374
Celo SafeBox: 0x8743E3ae32eD5864813d19b1469FdF901ACAbE9b
cUSD SafeBox: 0xceB8F9fC011235937f5bEE012eBB7727391Cd6c8
cEUR SafeBox: 0x49c13A1569d2eeA45d68732a99d09ce748C2719c

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
