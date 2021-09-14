# Dahlia v1

TL;DR. Here's what V1 will support:

- Multi assets lending and borrowing (with huge leverage for stablecoin farming!)
- More farming pools beyond just Ubeswap (think Balancer, Curve, etc)
- Can keep the farming assets and not just dumping
- No more EOA only = more composability
- You can bring your own LP tokens too = more flexibility

## Protocol Summary

Dahlia v1 is a leveraged yield-farming product. Here are some key features:

<!-- - In v1, The protocol  integrates with Foutain of Youth. Whenever a user wants to borrow funds (on leverage) to yield farm, Alpha Homora will borrow from the lending protocol. -->

- In v1, other assets are borrow-able (not only ETH like in v1), including stablecoins like USDT, USDC, DAI.
- In v1, users may also borrow supported LP tokens to farm more.
- Users can also bring their own LP tokens and add on to their positions.
- Each "spell" defines how the protocol interacts with farming pools, e.g. Uniswap spell, Sushiswap spell, Curve spell.
  - Spell functions include e.g. `addLiquidity`, `removeLiquidity`.
  - This is different from v1, where each pool has its own spell (goblin).
- Reward tokens e.g. UBE, SUSHI were sold and reinvested to users' positions in v1. Instead, users can now claim reward tokens.
- Adjustable positions - users can adjust their existing positions by supply more assets, borrow more assets, or repay some debts.
  - As long as the collateral credit >= borrow credit. Otherwise, the position is at liquidation risk.

## Protocol Components

- DahliaBank
  - Store each position's collateral tokens (in the form of wrapped LP tokens)
  - Users can execute "spells", e.g. opening a new position, closing/adjusting existing position.
- Caster
  - Intermediate contract that just calls another contract function (low-level call) with provided data (instead of bank), to prevent attack.
  - Doesn't store any funds
- Spells (e.g. Uniswap/Sushiswap/Curve/...)
  - Define how to interact with each pool
  - Execute `borrow`/`repay` assets by interacting with the bank, which will then interact with the lending protocol.
- Foubtain of Youth
  - Fork of cream finance with whitelisting feature 
  - For determining interest rate

### Component Interaction Flow

1. User -> DahliaBank.
   User calls `execute` to HomoraBank, specifying which spell and function to use, e.g. `addLiquidity` using Uniswap spell.
2. DahliaBank -> Caster.
   Forward low-level spell call to Caster (doesn't hold funds), to prevent attacks.
3. Caster -> Spell.
   Caster does low-level call to Spell.
4. Spell may call DahliaBank to e.g. `doBorrow` funds, `doTransmit` funds from users (so users can approve only the bank, not each spell), `doRepay` debt. Funds are then sent to Spell, to execute pool interaction.
5. Spells -> Pools.
   Spells interact with Pools (e.g. optimally swap before supplying to ubeswap, or removing liquidity from the pool and pay back some debts).
6. (Optional) Stake LP tokens in wrapper contracts (e.g. WMasterChef for Sushi, WLiquidityGauge for Curve, WStakingRewards for Uniswap + Balancer).
7. Spell may put collateral back to DahliaBank.
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

> For **Ubeswap** pools with staking rewards, use `addLiqudityWMasterChef` function.
> For **Sushiswap** pools with staking in masterchef, use `addLiqudityWMasterChef` function.
> For **Symmetric** pools with staking rewards, use `addLiquidityWStakingRewards` function.
> For all **Mobius** pools, use `addLiquidity[N]` (where `N` is the number of underlying tokens). The spell will auto put in Curve's liquidity gauge.
> For all **Curve** pools, use `addLiquidity[N]` (where `N` is the number of underlying tokens). The spell will auto put in Curve's liquidity gauge.

## Oracle

Prices are determined in mcUSD.

- For regular assets, asset prices can be derived from TWAP oracle.
- For LP tokens, asset prices will determine the optimal reserve proportion of the underlying assets, which are then used to compute the value of LP tokens. See `UniswapV2Oracle.sol` for example implementation.
