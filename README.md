# Dahlia v1 contracts

```
++++++++++++              +++++        ++++       ++++   ++++           ++++++++++++        ++++++  
++++++++++++++++       +++++++++++     ++++       ++++   ++++           ++++++++++++     ++++++++++++
++++          ++++   ++++       ++++   ++++       ++++   ++++               ++++       ++++        ++++
++++          ++++   +++++++++++++++   +++++++++++++++   ++++               ++++       ++++++++++++++++
++++          ++++   +++++++++++++++   +++++++++++++++   ++++               ++++       ++++++++++++++++
++++          ++++   ++++       ++++   ++++       ++++   ++++               ++++       ++++        ++++
++++++++++++++++     ++++       ++++   ++++       ++++   ++++++++++++   ++++++++++++   ++++        ++++
++++++++++++.        ++++       ++++   ++++       ++++   ++++++++++++   ++++++++++++   ++++        ++++
```

TL;DR. Here's what v1 will support:

- Multi assets lending and borrowing (with huge leverage for stablecoin farming!)
- More farming pools beyond just Ubeswap (think Mobius, Curve, etc)
- Can keep the farming assets and not just dumping
- No more EOA only = more composability
- You can bring your own LP tokens too = more flexibility
- Native flashloan support

## Protocol Summary

Dahlia v1 is a leveraged yield-farming product. Here are some key features:

<!-- - In v1, the protocol instead integrates with the Foutain of Youth, an exisiting lending protocol on Celo. Whenever a user wants to borrow funds (on leverage) to yield farm, Dahlia will borrow from the lending protocol. -->

- In v1, assets that are borrow-able are Celo and stablecoins like cUSD, USDC (from Ethereum), etc.
- In v1, users may also borrow supported LP tokens to farm more.
- Users can also bring their own LP tokens and add on to their positions.
- Each "spell" defines how the protocol interacts with farming pools, e.g. Uniswap spell, Sushiswap spell, Curve spell.
  - Spell functions include e.g. `addLiquidity`, `removeLiquidity`.
  - This is different from v1, where each pool has its own spell (goblin).
- Users can now claim reward tokens e.g. UBE, MOBI 
- Adjustable positions - users can adjust their existing positions by supply more assets, borrow more assets, or repay some debts.
  - As long as the collateral credit >= borrow credit. Otherwise, the position is at liquidation risk.

## Protocol Components

- DahliaBank
  - Store each position's collateral tokens (in the form of wrapped LP tokens)
  - Users can execute "spells", e.g. opening a new position, closing/adjusting existing position.
- Caster
  - Intermediate contract that just calls another contract function (low-level call) with provided data (instead of bank), to prevent attack.
  - Doesn't store any funds
- Spells (e.g. Ubeswap/Sushiswap/Mobius/Curve)
  - Define how to interact with each pool
  - Execute `borrow`/`repay` assets by interacting with the bank, which will then interact with the lending protocol.

### Component Interaction Flow

1. User -> DahliaBank.
   User calls `execute` to DahliaBank, specifying which spell and function to use, e.g. `addLiquidity` using Uniswap spell.
2. HomoraBank -> Caster.
   Forward low-level spell call to Caster (doesn't hold funds), to prevent attacks.
3. Caster -> Spell.
   Caster does low-level call to Spell.
4. Spell may call DahliaBank to e.g. `doBorrow` funds, `doTransmit` funds from users (so users can approve only the bank, not each spell), `doRepay` debt. Funds are then sent to Spell, to execute pool interaction.
5. Spells -> Pools.
   Spells interact with Pools (e.g. optimally swap before supplying to Ubeswap, or removing liquidity from the pool and pay back some debts).
6. (Optional) Stake LP tokens in wrapper contracts (e.g. WMasterChef for Ubeswap, WLiquidityGauge for Mobius, WStakingRewards for Symmetric).
7. Spell may put collateral back to DahliaBank.
   If the spell funtion called is e.g. to open a new position, then the LP tokens will be stored in DahliaBank.

## Example Execution

### AddLiquidity

1. User calls `execute(0, cUSD, Celo, data)` on DahliaBank contract. `data` encodes "UniswapSpell" --this is for ubeswap-- function call with arguments (including how much of each asset to supply, to borrow, and slippage control settings).
2. DahliaBank forwards data call to Caster.
3. Caster does low-level call (with `data`, which encodes `addLiquidity` function call with arguments) to UniswapSpell.
4. UniswapSpell executes `addLiquidityWERC20`
   - `doTransmit` desired amount of assets the user wants to supply
   - `doBorrow` from the lending protocol
   - Optimally swap assets and add liquidity to Uniswap pool
   - Wrap LP tokens to wrapper WERC20 (to get ERC1155)
   - `doPutCollateral` wrapped tokens back to HomoraBank
   - Refund leftover assets to the user.

> For **Ubeswap** pools with staking in masterchef, use `addLiqudityWMasterChef` function.
> For **SushiSwap** pools with staking in masterchef, use `addLiqudityWMasterChef` function.
> For **Symmetric** pools with staking rewards, use `addLiquidityWStakingRewards` function.
> For all **Mobius** pools, use `addLiquidity[N]` (where `N` is the number of underlying tokens). The spell will auto put in Mobius's liquidity gauge.
> For all **Curve** pools, use `addLiquidity[N]` (where `N` is the number of underlying tokens). The spell will auto put in Curve's liquidity gauge.


## Oracle

Prices are taking from SortedOracles contract and only avialable for cUSD, cEUR, Celo.

- For regular assets, asset prices can be derived from Ubeswap pool (with UBE) and are secured through a TWAP contract.
- For LP tokens, asset prices will determine the optimal reserve proportion of the underlying assets, which are then used to compute the value of LP tokens. See `UniswapV2Oracle.sol` for example implementation.


0x1bAbC24Ce769FB93DF2A312f66373a62D4115bd4
0x5162d7A8c3aE7e49AAeE31Bd0BF18F89b2626182
0xCbfb4C355D75993B2Be90e3876050b65fda7352d