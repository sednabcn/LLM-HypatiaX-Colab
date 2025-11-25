# UNISWAP V4: COMPREHENSIVE EXPLANATION

## 📋 Table of Contents
1. [What is Uniswap V4?](#what-is-uniswap-v4)
2. [Key Innovations](#key-innovations)
3. [What Changed from V3](#what-changed-from-v3)
4. [What DIDN'T Change](#what-didnt-change)
5. [Technical Deep Dive](#technical-deep-dive)
6. [Use Cases](#use-cases)
7. [Code Examples](#code-examples)

---

## What is Uniswap V4?

Uniswap V4 is the **fourth iteration** of the Uniswap decentralized exchange protocol, launched in January 2025. It's not a complete redesign but rather an **architectural upgrade** that keeps V3's proven concentrated liquidity model while adding powerful new features.

### The Big Idea

**V4 = V3's Math + Hooks + Gas Optimization**

Think of V4 as V3 with:
- 🪝 **Hooks** - Custom plugins for any use case
- 🎯 **Singleton** - All pools in one contract
- ⚡ **Flash Accounting** - Net settlement only
- 💎 **Native ETH** - No wrapping needed
- 📊 **Dynamic Fees** - Unlimited fee tiers

---

## Key Innovations

### 1. 🪝 HOOKS (The Game Changer)

**What are hooks?**
Hooks are smart contracts that execute custom logic at specific points in a pool's lifecycle:

```
Pool Lifecycle Events:
├─ beforeInitialize / afterInitialize
├─ beforeSwap / afterSwap  
├─ beforeAddLiquidity / afterAddLiquidity
├─ beforeRemoveLiquidity / afterRemoveLiquidity
└─ beforeDonate / afterDonate
```

**Why hooks matter:**
- 🎨 **Unlimited Customization** - Add ANY logic without forking
- 🔧 **Modular Design** - Mix and match hooks
- 🚀 **Rapid Innovation** - New features without protocol changes

**Hook Examples:**
- **Dynamic Fees** - Adjust fees based on volatility
- **TWAMM** - Time-weighted AMM for large orders
- **Limit Orders** - On-chain limit orders
- **MEV Protection** - Prevent sandwich attacks
- **KYC/Compliance** - Restrict access
- **Volatility Oracles** - Price feeds
- **Auto-compounding** - Reinvest fees automatically

### 2. 🎯 SINGLETON ARCHITECTURE

**V3 Problem:**
- Each pool = Separate contract
- Creating pool = Deploy contract (~2M gas)
- Multi-hop swap = Transfer tokens between contracts

**V4 Solution:**
- ALL pools in ONE contract (PoolManager)
- Creating pool = State update (~20k gas)
- **99% gas savings** on pool creation!

```
V3: Pool A | Pool B | Pool C | Pool D  (separate contracts)
V4: [Pool A, Pool B, Pool C, Pool D]  (one singleton)
```

### 3. ⚡ FLASH ACCOUNTING

**The Magic of EIP-1153 Transient Storage**

**V3 Problem:**
Multi-hop swap (USDC → ETH → WBTC) requires:
1. Transfer USDC to Pool 1
2. Transfer ETH from Pool 1 to Pool 2
3. Transfer WBTC from Pool 2 to user

**V4 Solution:**
1. Track delta: +USDC
2. Track delta: +ETH, -ETH  (cancels out!)
3. Track delta: +WBTC
4. **Only settle net:** USDC in, WBTC out

**Result:** Massive gas savings on multi-hop swaps!

### 4. 💎 NATIVE ETH SUPPORT

**V3:** Must wrap ETH → WETH (costs gas)
**V4:** Use ETH directly (~15% gas savings)

### 5. 📊 DYNAMIC FEES

**V3:** Limited to 4 tiers (0.01%, 0.05%, 0.3%, 1%)
**V4:** **ANY fee tier** + hooks can modify fees dynamically

Example: Fee adjusts based on volatility
- Low volatility = 0.05% fee
- High volatility = 1% fee (protect LPs)

---

## What Changed from V3

| Feature | V3 | V4 |
|---------|----|----|
| **Architecture** | Multiple contracts | Singleton contract |
| **Pool Creation** | ~2M gas | ~20k gas (99% cheaper!) |
| **Multi-hop Swaps** | Transfer every step | Flash accounting (net only) |
| **ETH Support** | Must wrap to WETH | Native ETH |
| **Fee Tiers** | Fixed (4 options) | Unlimited + dynamic |
| **Customization** | Fork required | Hooks (no fork needed) |
| **Position Management** | Standard | Same + hook callbacks |

---

## What DIDN'T Change

### ✅ CRITICAL: V4 Uses V3's Math!

**THESE ARE IDENTICAL:**
1. **Concentrated Liquidity** - Same formula
2. **Tick System** - Same tick spacing
3. **Position NFTs** - Same structure
4. **IL Calculation** - Same math
5. **Liquidity Formula** - Same as V3
6. **Token Amounts** - Same calculation

```python
# THIS IS THE SAME IN V3 AND V4:
position_value = amount0 * current_price + amount1
il_dollar = pool_value - hodl_value

# Liquidity calculation (SAME)
L = amount0 * sqrt(P) * sqrt(Pb) / (sqrt(Pb) - sqrt(P))
```

### Why Keep V3's Math?

✅ **Proven model** - V3 has $5B+ TVL
✅ **Battle-tested** - 3+ years in production
✅ **Well-understood** - Extensive research and tooling
✅ **Capital efficient** - Best in class

---

## Technical Deep Dive

### Concentrated Liquidity (Same as V3)

Liquidity providers choose a price range [Pa, Pb]:

```
Full Range (V2):      ░░░░░░░░░░░░░░░░░░░░░░░░░
Concentrated (V3/V4): ────────████████─────────
                              Pa     Pb
```

**Formulas (IDENTICAL in V3 and V4):**

```
If P < Pa:  (all token0)
  amount0 = L * (√Pb - √Pa) / (√Pa * √Pb)
  amount1 = 0

If P > Pb:  (all token1)
  amount0 = 0
  amount1 = L * (√Pb - √Pa)

If Pa ≤ P ≤ Pb:  (both tokens)
  amount0 = L * (√Pb - √P) / (√P * √Pb)
  amount1 = L * (√P - √Pa)
```

### Hook System

**Hook Permissions (bit flags):**
```solidity
uint16 permissions = 
    BEFORE_SWAP_FLAG |
    AFTER_SWAP_FLAG |
    BEFORE_ADD_LIQUIDITY_FLAG;
```

**Hook Address Encoding:**
Hook address encodes permissions in its prefix:
```
0x8000... = BEFORE_SWAP enabled
0x4000... = AFTER_SWAP enabled
```

**Hook Execution Flow:**
```
User calls swap()
    ↓
PoolManager.unlock()
    ↓
beforeSwap(hookData) → Hook Contract
    ↓
Perform swap (core logic)
    ↓
afterSwap(amount_out) → Hook Contract
    ↓
PoolManager.lock() (settle deltas)
```

### Flash Accounting Deep Dive

**EIP-1153 Transient Storage:**
- Data exists only during transaction
- Cleared at end of transaction
- ~100 gas (vs ~20,000 for SSTORE)

**Delta Tracking:**
```python
# Initialize deltas
deltas = {'ETH': 0, 'USDC': 0, 'WBTC': 0}

# Swap 1: USDC → ETH
deltas['USDC'] += 1000
deltas['ETH'] -= 0.5

# Swap 2: ETH → WBTC
deltas['ETH'] += 0.5  # Cancels out!
deltas['WBTC'] -= 0.02

# Final settlement (only net changes)
transfer_in(USDC, 1000)
transfer_out(WBTC, 0.02)
# ETH never moved! (internal only)
```

---

## Use Cases

### 1. Dynamic Fee Pools
```python
# Hook adjusts fee based on volatility
def beforeSwap(amount_in, price):
    volatility = calculate_volatility()
    fee_multiplier = 1.0 + (volatility * 2.0)
    return fee_multiplier
```

### 2. TWAMM (Time-Weighted AMM)
- Execute large orders over time
- Minimize price impact
- Protect against MEV

### 3. On-Chain Limit Orders
```python
# Hook executes limit order when price reached
def beforeSwap(price):
    if price >= limit_price:
        execute_order()
```

### 4. MEV Protection
- Delay execution
- Batch transactions
- Fair ordering

### 5. Loyalty Programs
```python
# Hook rewards frequent traders
def afterSwap(user, amount):
    points[user] += calculate_points(amount)
```

### 6. Auto-Compounding
- Reinvest fees automatically
- No manual claiming needed
- Higher APY

### 7. Compliance/KYC
```python
# Hook restricts access
def beforeSwap(user):
    if not is_verified(user):
        revert("KYC required")
```

---

## Code Examples

### Creating a V4 Pool

```python
# V4 uses singleton
pool_manager = UniswapV4Singleton()

# Create pool with hook
pool_key = PoolKey(
    token0="ETH",
    token1="USDC",
    fee=3000,  # 0.3%
    tick_spacing=60,
    hook_address="0x1234...5678"  # Dynamic fee hook
)

pool_manager.initialize_pool(pool_key, initial_price=2000)
# Gas: ~20k (vs 2M in V3!)
```

### Minting Position (Same as V3!)

```python
# Position math is IDENTICAL to V3
position = pool_manager.mint_position(
    pool_key=pool_key,
    price_current=2000,
    tick_lower=price_to_tick(1900),
    tick_upper=price_to_tick(2100),
    amount0_desired=1.0,  # 1 ETH
    amount1_desired=2000  # 2000 USDC
)
```

### Calculating IL (Same as V3!)

```python
# IL formula is IDENTICAL to V3
pool_value = amount0 * current_price + amount1
hodl_value = initial_amount0 * current_price + initial_amount1
il_dollar = pool_value - hodl_value
il_percent = (il_dollar / hodl_value) * 100
```

### Multi-Hop Swap with Flash Accounting

```python
# V4 advantage: Only settle net balances
swap_path = [
    (pool_usdc_eth, 1000),  # 1000 USDC → ETH
    (pool_eth_wbtc, all_eth) # All ETH → WBTC
]

# Deltas tracked internally
# Only final amounts transferred!
result = pool_manager.multi_hop_swap(swap_path)
```

---

## Performance Comparison

### Gas Costs

| Operation | V3 | V4 | Savings |
|-----------|----|----|---------|
| **Create Pool** | ~2M | ~20k | 99% |
| **Single Swap** | ~110k | ~105k | 5% |
| **Multi-hop (3 pools)** | ~180k | ~120k | 33% |
| **ETH Swap** | ~130k | ~110k | 15% |
| **Position Management** | ~150k | ~145k | 3% |

### Economic Benefits

**For a $10k position over 30 days:**

```
V3:
├─ Fees: $150 (0.3% static)
├─ Gas costs: $50
└─ Net: $100

V4:
├─ Fees: $200 (0.4% average via hook)
├─ Gas costs: $25 (50% savings)
└─ Net: $175 (75% better!)
```

---

## Migration Guide: V3 → V4

### What to Keep
✅ Your position sizing strategy
✅ Your range selection approach
✅ Your IL understanding
✅ Your fee tier choices

### What to Add
🆕 Choose appropriate hooks
🆕 Enable dynamic fees if beneficial
🆕 Take advantage of native ETH
🆕 Use flash accounting for complex strategies

### Code Migration

```python
# V3 Code
v3_pool = UniswapV3Factory.createPool(
    tokenA, tokenB, fee=3000
)

# V4 Code (minimal changes!)
v4_pool_key = PoolKey(
    token0=tokenA,
    token1=tokenB,
    fee=3000,
    tick_spacing=60,
    hook_address=None  # Or add hook!
)
v4_pool_manager.initialize_pool(v4_pool_key, price)
```

---

## Best Practices

### 1. Hook Selection
- ✅ Use established, audited hooks
- ✅ Understand hook permissions
- ⚠️ Be cautious with untrusted hooks
- ❌ Never use unaudited hooks with large amounts

### 2. Fee Optimization
- Dynamic fees can increase earnings 20-50%
- But adds complexity
- Test thoroughly before production

### 3. Gas Optimization
- Multi-hop routes benefit most from V4
- Native ETH saves 15% on gas
- Batch operations when possible

### 4. Position Management
- Same strategies as V3 work in V4
- Monitor hook behavior
- Rebalance based on hook logic

---

## Common Misconceptions

### ❌ "V4 changes the liquidity model"
**✅ FALSE:** V4 uses V3's concentrated liquidity

### ❌ "IL calculation is different in V4"
**✅ FALSE:** IL formula is identical to V3

### ❌ "Hooks are required"
**✅ FALSE:** You can use V4 exactly like V3 (no hooks)

### ❌ "V4 is more complex"
**✅ PARTIALLY TRUE:** 
- Core math is same
- Hooks add optional complexity
- You choose complexity level

---

## Summary

### The Formula

```
V4 = V3's Proven Math + Modern Infrastructure + Unlimited Customization
```

### Key Takeaways

1. **Same Core Math** - V3's concentrated liquidity
2. **Better Gas** - 99% cheaper pools, flash accounting
3. **More Flexible** - Hooks enable anything
4. **Still Simple** - Can ignore hooks and use like V3
5. **Production Ready** - Launched Jan 2025, growing TVL

### When to Use V4

✅ **Always for new deployments**
✅ **When you need customization** (hooks)
✅ **For gas-sensitive operations**
✅ **Multi-hop routing**

### When to Stay on V3

⚠️ **Existing positions** (if working well)
⚠️ **If unsure about hooks** (learn first)
⚠️ **Maximum simplicity** needed

---

## Resources

- **Whitepaper:** https://github.com/Uniswap/v4-core/blob/main/docs/whitepaper/whitepaper-v4.pdf
- **Documentation:** https://docs.uniswap.org/contracts/v4/overview
- **Hook Examples:** https://github.com/fewwwww/awesome-uniswap-hooks
- **Code:** https://github.com/Uniswap/v4-core

---

## Conclusion

Uniswap V4 is **evolutionary, not revolutionary**. It takes V3's proven concentrated liquidity model and adds:

- 🪝 **Hooks** for unlimited customization
- ⚡ **Flash accounting** for gas savings
- 🎯 **Singleton** for efficiency
- 💎 **Native ETH** for convenience

The **core math remains unchanged**, so all your V3 knowledge transfers directly. You can start simple (no hooks) and add complexity as needed.

**Bottom line:** V4 gives you V3's power + modern infrastructure + unlimited customization, all while maintaining the same proven formulas that made V3 successful.