# Alpha Homora v2 🧙‍♂️

## Alfajores Addresses 
HomoraBank: 0x0460878568C92D877f5544a2F3a1523E6c2bB1CA
CoreOracle deployed at: 0x384f6e069aC3726E1894A30D0d46021c5f5E8acA
ProxyOracle deployed at: 0x31ac8Ac2BC3025de9aA9f3EC5dC9db2dc1B5A6E3
UniswapV2Oracle deployed at: 0x03d2e511D4D78771e0019a3026CDc000D8087994
UbeswapV1Oracle deployed at: 0x2E0df20185a79D1c4198EEa8979bd3B56C846546
ERC20KP3ROracle deployed at: 0xaE80862EAea20e82df0BC3d09459733A4ccc0ce9
WERC20 deployed at: 0x38E04E9c49844aF8123da9475576cdD1195e0916
UniswapV2SpellV1 deployed at: 0xe53ef2fC19F8e905F372432834eED212C692A8F9
celo SafeBox deployed at: 0x47c91f227d04B19E43604F3141779f91feD4f8ad
cusd SafeBox deployed at: 0x2FF09993ebA7292fb93d3F2F87ec498B5c361c64
ube SafeBox deployed at: 0x7a2477b1B274715D5fC7f386366f2D7Db8f5ACe9
Comptroller: 0x115308bBCBd3917033EcE55aC35C92a279A7055D
dCELO: 0x9Ce844b3A315FE2CBB22b88B3Eb0921dD7a2e018
dcUSD: 0xE5283EAE77252275e6207AC25AAF7A0A4004EEFe
dUBE: 0x6850Ee9921fD9FF2419a59Cf7417B0e18EE0A4Bc

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
