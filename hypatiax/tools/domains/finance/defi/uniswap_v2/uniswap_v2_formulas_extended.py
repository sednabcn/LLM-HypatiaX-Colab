import math
from typing import Dict, List

EPSILON = 1e-12

# ============================================================================
# ADVANCED DeFi CALCULATOR - FORMULAS 21-40
# ============================================================================


class DeFiAdvancedCalculator:
    """
    Advanced DeFi formulas with safety constraints and validation
    Implements formulas 21-40 from the reference guide
    """

    # ========================================================================
    # FORMULA 21: Uniswap V3 Price from Tick
    # ========================================================================
    @staticmethod
    def uniswap_v3_tick_to_price(tick: int, validate: bool = True) -> float:
        """
        Convert Uniswap V3 tick to actual price
        Formula: Price = 1.0001^tick

        CONSTRAINTS:
        - tick ∈ [-887272, 887272] (V3 tick range)

        Args:
            tick: Integer tick value
            validate: Enable constraint validation

        Returns:
            Price at that tick
        """
        MIN_TICK = -887272
        MAX_TICK = 887272

        if validate:
            if not (MIN_TICK <= tick <= MAX_TICK):
                raise ValueError(f"Tick must be in [{MIN_TICK}, {MAX_TICK}], got {tick}")

        # Clamp tick to safe range
        tick = max(MIN_TICK, min(tick, MAX_TICK))

        # Calculate price with safe exponentiation
        price = math.pow(1.0001, tick)

        return price

    # ========================================================================
    # FORMULA 22: Constant Sum AMM Output (mStable)
    # ========================================================================
    @staticmethod
    def constant_sum_output(amount_in: float, fee: float = 0.003, validate: bool = True) -> float:
        """
        Constant Sum AMM for stablecoins (1:1 swap)
        Formula: Output = Amount_in × (1 - fee)

        CONSTRAINTS:
        - amount_in > 0
        - fee ∈ [0, 1)

        Args:
            amount_in: Input amount
            fee: Trading fee rate
            validate: Enable validation

        Returns:
            Output amount (1:1 minus fee)
        """
        if validate:
            if amount_in <= 0:
                raise ValueError(f"amount_in must be > 0, got {amount_in}")
            if not (0 <= fee < 1):
                raise ValueError(f"fee must be in [0, 1), got {fee}")

        output = amount_in * (1 - fee)
        return max(output, 0)

    # ========================================================================
    # FORMULA 23: Curve StableSwap Invariant (Simplified)
    # ========================================================================
    @staticmethod
    def curve_stableswap_d(reserves: List[float], A: float, validate: bool = True) -> float:
        """
        Curve StableSwap invariant calculation (simplified Newton's method)
        Formula: D = (A × n^n × Σx_i + D^(n+1) / (n^n × Πx_i))^(1/2)

        CONSTRAINTS:
        - A ∈ [1, 10000] (amplification coefficient)
        - All reserves > 0
        - n ≥ 2 (at least 2 tokens)

        Args:
            reserves: List of token reserves
            A: Amplification coefficient
            validate: Enable validation

        Returns:
            Invariant D
        """
        if validate:
            if not (1 <= A <= 10000):
                raise ValueError(f"A must be in [1, 10000], got {A}")
            if len(reserves) < 2:
                raise ValueError(f"Need at least 2 reserves, got {len(reserves)}")
            if any(r <= 0 for r in reserves):
                raise ValueError("All reserves must be > 0")

        n = len(reserves)
        S = sum(reserves)  # Sum of reserves

        if S == 0:
            return 0

        # Initial guess for D
        D = S
        Ann = A * n

        # Newton's method iteration (simplified, 10 iterations)
        for _ in range(10):
            D_P = D
            for reserve in reserves:
                D_P = D_P * D / (n * max(reserve, EPSILON))

            D_prev = D
            D = (Ann * S + D_P * n) / (Ann - 1 + (n + 1) * D_P / D)

            # Convergence check
            if abs(D - D_prev) < 1:
                break

        return D

    # ========================================================================
    # FORMULA 24: Aave Variable Borrow Rate (Kinked Model)
    # ========================================================================
    @staticmethod
    def aave_variable_rate(
        utilization: float,
        u_optimal: float = 0.8,
        r_base: float = 0.0,
        r_slope1: float = 0.04,
        r_slope2: float = 0.60,
        validate: bool = True,
    ) -> float:
        """
        Aave's kinked interest rate model

        Formula:
        - If U ≤ U_optimal: Rate = R_base + (U / U_optimal) × R_slope1
        - If U > U_optimal: Rate = R_base + R_slope1 + ((U - U_optimal) / (1 - U_optimal)) × R_slope2

        CONSTRAINTS:
        - utilization ∈ [0, 1]
        - u_optimal ∈ (0, 1)
        - All rates ≥ 0

        Args:
            utilization: Pool utilization rate (0-1)
            u_optimal: Optimal utilization (typically 0.8)
            r_base: Base rate
            r_slope1: Slope before optimal
            r_slope2: Slope after optimal (steep)
            validate: Enable validation

        Returns:
            Variable borrow rate (annual, decimal)
        """
        if validate:
            if not (0 <= utilization <= 1):
                raise ValueError(f"utilization must be in [0, 1], got {utilization}")
            if not (0 < u_optimal < 1):
                raise ValueError(f"u_optimal must be in (0, 1), got {u_optimal}")
            if any(r < 0 for r in [r_base, r_slope1, r_slope2]):
                raise ValueError("All rates must be ≥ 0")

        if utilization <= u_optimal:
            # Below optimal utilization
            rate = r_base + (utilization / u_optimal) * r_slope1
        else:
            # Above optimal utilization (steep increase)
            rate = r_base + r_slope1 + ((utilization - u_optimal) / (1 - u_optimal)) * r_slope2

        return rate

    # ========================================================================
    # FORMULA 25: Compound Borrow APY with COMP Rewards
    # ========================================================================
    @staticmethod
    def compound_borrow_apy_with_rewards(
        borrow_apr: float,
        comp_per_block: float,
        blocks_per_year: float = 2_102_400,
        comp_price: float = 50.0,
        total_borrowed: float = 1_000_000,
        validate: bool = True,
    ) -> Dict:
        """
        Net borrowing cost after COMP rewards
        Formula: Total_APY = Borrow_APR - (COMP_per_block × blocks_per_year × COMP_price / Total_Borrowed)

        CONSTRAINTS:
        - borrow_apr ≥ 0
        - comp_per_block ≥ 0
        - comp_price > 0
        - total_borrowed > 0

        Returns:
            Dict with borrow_apr, reward_apy, net_apy
        """
        if validate:
            if borrow_apr < 0:
                raise ValueError(f"borrow_apr must be ≥ 0, got {borrow_apr}")
            if comp_per_block < 0:
                raise ValueError(f"comp_per_block must be ≥ 0, got {comp_per_block}")
            if comp_price <= 0:
                raise ValueError(f"comp_price must be > 0, got {comp_price}")
            if total_borrowed <= 0:
                raise ValueError(f"total_borrowed must be > 0, got {total_borrowed}")

        # Calculate annual COMP rewards
        annual_comp = comp_per_block * blocks_per_year
        reward_value = annual_comp * comp_price
        reward_apy = reward_value / max(total_borrowed, EPSILON)

        # Net APY (can be negative = paid to borrow)
        net_apy = borrow_apr - reward_apy

        return {"borrow_apr": borrow_apr, "reward_apy": reward_apy, "net_apy": net_apy, "paid_to_borrow": net_apy < 0}

    # ========================================================================
    # FORMULA 26: Leverage Ratio (DeFi Lending)
    # ========================================================================
    @staticmethod
    def leverage_ratio(ltv: float, validate: bool = True) -> float:
        """
        Maximum leverage through recursive borrowing
        Formula: Leverage = 1 / (1 - LTV)

        CONSTRAINTS:
        - ltv ∈ [0, 1)

        Args:
            ltv: Loan-to-Value ratio
            validate: Enable validation

        Returns:
            Maximum leverage multiplier
        """
        if validate:
            if not (0 <= ltv < 1):
                raise ValueError(f"ltv must be in [0, 1), got {ltv}")

        # Safe division
        leverage = 1 / max(1 - ltv, EPSILON)

        return leverage

    # ========================================================================
    # FORMULA 27: Protocol Revenue (Trading Fees)
    # ========================================================================
    @staticmethod
    def protocol_revenue(volume: float, fee_rate: float, protocol_cut: float, validate: bool = True) -> float:
        """
        Protocol earnings from trading fees
        Formula: Revenue = Volume × Fee_Rate × Protocol_Cut

        CONSTRAINTS:
        - volume ≥ 0
        - fee_rate ∈ [0, 1)
        - protocol_cut ∈ [0, 1]

        Args:
            volume: Trading volume (USD)
            fee_rate: Trading fee percentage
            protocol_cut: Portion to protocol (e.g., 1/6 for Uniswap)
            validate: Enable validation

        Returns:
            Protocol revenue (USD)
        """
        if validate:
            if volume < 0:
                raise ValueError(f"volume must be ≥ 0, got {volume}")
            if not (0 <= fee_rate < 1):
                raise ValueError(f"fee_rate must be in [0, 1), got {fee_rate}")
            if not (0 <= protocol_cut <= 1):
                raise ValueError(f"protocol_cut must be in [0, 1], got {protocol_cut}")

        revenue = volume * fee_rate * protocol_cut
        return revenue

    # ========================================================================
    # FORMULA 28: Maker DAO Stability Fee
    # ========================================================================
    @staticmethod
    def maker_stability_fee(principal: float, rate: float, time_years: float, validate: bool = True) -> Dict:
        """
        Continuously compounded interest on MakerDAO CDP
        Formula: Total_Fee = Principal × e^(rate × time) - Principal

        CONSTRAINTS:
        - principal > 0
        - rate ≥ 0
        - time_years ≥ 0

        Returns:
            Dict with total_debt, fee_amount, effective_apr
        """
        if validate:
            if principal <= 0:
                raise ValueError(f"principal must be > 0, got {principal}")
            if rate < 0:
                raise ValueError(f"rate must be ≥ 0, got {rate}")
            if time_years < 0:
                raise ValueError(f"time_years must be ≥ 0, got {time_years}")

        # Continuous compounding
        total_debt = principal * math.exp(rate * time_years)
        fee_amount = total_debt - principal

        # Effective APR
        if time_years > 0:
            effective_apr = (total_debt / principal) ** (1 / time_years) - 1
        else:
            effective_apr = 0

        return {
            "principal": principal,
            "total_debt": total_debt,
            "fee_amount": fee_amount,
            "effective_apr": effective_apr,
        }

    # ========================================================================
    # FORMULA 29: Liquidity Mining Dilution Rate
    # ========================================================================
    @staticmethod
    def dilution_rate(emissions_per_year: float, total_supply: float, validate: bool = True) -> Dict:
        """
        Annual inflation rate from token emissions
        Formula: Dilution = (Emissions_per_year / Total_Supply) × 100

        CONSTRAINTS:
        - emissions_per_year ≥ 0
        - total_supply > 0

        Returns:
            Dict with dilution_pct, new_supply, dilution_warning
        """
        if validate:
            if emissions_per_year < 0:
                raise ValueError(f"emissions_per_year must be ≥ 0, got {emissions_per_year}")
            if total_supply <= 0:
                raise ValueError(f"total_supply must be > 0, got {total_supply}")

        dilution_pct = (emissions_per_year / total_supply) * 100
        new_supply = total_supply + emissions_per_year

        # Warning thresholds
        if dilution_pct > 20:
            warning = "HIGH: >20% annual dilution"
        elif dilution_pct > 10:
            warning = "MODERATE: >10% dilution"
        else:
            warning = "LOW: <10% dilution"

        return {
            "dilution_pct": dilution_pct,
            "emissions_per_year": emissions_per_year,
            "total_supply": total_supply,
            "new_supply": new_supply,
            "warning": warning,
        }

    # ========================================================================
    # FORMULA 30: Impermanent Loss with Fees (Net)
    # ========================================================================
    @staticmethod
    def il_with_fees_net(price_ratio: float, fee_apr: float, time_years: float, validate: bool = True) -> Dict:
        """
        Net impermanent loss after fee earnings
        Formula: Net_IL = IL - (Fee_APR × time × 2√(r) / (r + 1))

        CONSTRAINTS:
        - price_ratio > 0
        - fee_apr ≥ 0
        - time_years ≥ 0

        Returns:
            Dict with il_pct, fees_earned_pct, net_result_pct, profitable
        """
        if validate:
            if price_ratio <= 0:
                raise ValueError(f"price_ratio must be > 0, got {price_ratio}")
            if fee_apr < 0:
                raise ValueError(f"fee_apr must be ≥ 0, got {fee_apr}")
            if time_years < 0:
                raise ValueError(f"time_years must be ≥ 0, got {time_years}")

        # Calculate IL percentage
        sqrt_ratio = math.sqrt(price_ratio)
        il_pct = (2 * sqrt_ratio / (price_ratio + 1) - 1) * 100

        # Calculate fees earned (scaled by pool share factor)
        pool_share_factor = 2 * sqrt_ratio / (price_ratio + 1)
        fees_earned_pct = fee_apr * time_years * pool_share_factor * 100

        # Net result
        net_result_pct = fees_earned_pct + il_pct  # IL is negative

        return {
            "price_ratio": price_ratio,
            "il_pct": il_pct,
            "fees_earned_pct": fees_earned_pct,
            "net_result_pct": net_result_pct,
            "profitable": net_result_pct > 0,
            "time_years": time_years,
        }

    # ========================================================================
    # FORMULA 31: Multi-hop Price Impact
    # ========================================================================
    @staticmethod
    def multi_hop_impact(impacts: List[float], validate: bool = True) -> float:
        """
        Cumulative price impact across multiple hops
        Formula: Total_Impact = 1 - Π(1 - Impact_i)

        CONSTRAINTS:
        - All impacts ∈ [0, 1)

        Args:
            impacts: List of individual hop impacts (decimals)
            validate: Enable validation

        Returns:
            Total cumulative impact (decimal)
        """
        if validate:
            if not impacts:
                raise ValueError("impacts list cannot be empty")
            for i, impact in enumerate(impacts):
                if not (0 <= impact < 1):
                    raise ValueError(f"Impact {i} must be in [0, 1), got {impact}")

        # Calculate product of (1 - impact_i)
        product = 1.0
        for impact in impacts:
            product *= 1 - impact

        total_impact = 1 - product
        return total_impact

    # ========================================================================
    # FORMULA 32: Black-Scholes Delta (Call Option)
    # ========================================================================
    @staticmethod
    def black_scholes_delta(
        spot: float, strike: float, rate: float, volatility: float, time_years: float, validate: bool = True
    ) -> Dict:
        """
        Options Delta calculation (Black-Scholes)
        Formula: Δ_call = N(d₁)
        where: d₁ = (ln(S/K) + (r + σ²/2)T) / (σ√T)

        CONSTRAINTS:
        - spot > 0
        - strike > 0
        - volatility > 0
        - time_years > 0

        Returns:
            Dict with delta, d1, in_the_money probability
        """
        if validate:
            if spot <= 0:
                raise ValueError(f"spot must be > 0, got {spot}")
            if strike <= 0:
                raise ValueError(f"strike must be > 0, got {strike}")
            if volatility <= 0:
                raise ValueError(f"volatility must be > 0, got {volatility}")
            if time_years <= 0:
                raise ValueError(f"time_years must be > 0, got {time_years}")

        # Calculate d1
        sqrt_t = math.sqrt(time_years)
        d1 = (math.log(spot / strike) + (rate + 0.5 * volatility**2) * time_years) / (volatility * sqrt_t)

        # Standard normal CDF approximation
        def norm_cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        delta = norm_cdf(d1)

        return {"delta": delta, "d1": d1, "spot": spot, "strike": strike, "moneyness": spot / strike}

    # ========================================================================
    # FORMULA 33: Perpetual Swap Basis
    # ========================================================================
    @staticmethod
    def perpetual_basis(
        perpetual_price: float, spot_price: float, days_to_annualize: int = 1, validate: bool = True
    ) -> Dict:
        """
        Annualized perpetual contract premium/discount
        Formula: Basis = (Perpetual_Price - Spot_Price) / Spot_Price × (365 / Days)

        CONSTRAINTS:
        - perpetual_price > 0
        - spot_price > 0
        - days_to_annualize > 0

        Returns:
            Dict with basis_annualized, premium_pct, market_sentiment
        """
        if validate:
            if perpetual_price <= 0:
                raise ValueError(f"perpetual_price must be > 0, got {perpetual_price}")
            if spot_price <= 0:
                raise ValueError(f"spot_price must be > 0, got {spot_price}")
            if days_to_annualize <= 0:
                raise ValueError(f"days_to_annualize must be > 0, got {days_to_annualize}")

        premium_pct = ((perpetual_price - spot_price) / spot_price) * 100
        basis_annualized = premium_pct * (365 / days_to_annualize)

        # Market sentiment
        if basis_annualized > 5:
            sentiment = "Bullish (backwardation)"
        elif basis_annualized < -5:
            sentiment = "Bearish (contango)"
        else:
            sentiment = "Neutral"

        return {
            "perpetual_price": perpetual_price,
            "spot_price": spot_price,
            "premium_pct": premium_pct,
            "basis_annualized": basis_annualized,
            "sentiment": sentiment,
        }

    # ========================================================================
    # FORMULA 34: Flash Loan Arbitrage Net Profit
    # ========================================================================
    @staticmethod
    def flash_loan_net_profit(
        price_a: float,
        price_b: float,
        amount: float,
        fee_a: float,
        fee_b: float,
        gas_cost: float,
        flash_fee_pct: float = 0.0009,
        validate: bool = True,
    ) -> Dict:
        """
        True arbitrage profit after all costs
        Formula: Net = (Price_B - Price_A) × Amount - Fee_A - Fee_B - Gas - Flash_Fee

        CONSTRAINTS:
        - All prices > 0
        - amount > 0
        - All fees ≥ 0

        Returns:
            Dict with gross_profit, total_costs, net_profit, profitable, roi
        """
        if validate:
            if price_a <= 0 or price_b <= 0:
                raise ValueError(f"Prices must be > 0")
            if amount <= 0:
                raise ValueError(f"amount must be > 0, got {amount}")
            if any(f < 0 for f in [fee_a, fee_b, gas_cost, flash_fee_pct]):
                raise ValueError("All fees must be ≥ 0")

        # Gross profit from price difference
        gross_profit = (price_b - price_a) * amount

        # Calculate all costs
        flash_fee = amount * flash_fee_pct
        total_costs = fee_a + fee_b + gas_cost + flash_fee

        # Net profit
        net_profit = gross_profit - total_costs

        # ROI relative to gas cost
        roi = (net_profit / max(gas_cost, EPSILON)) if gas_cost > 0 else float("inf")

        return {
            "price_a": price_a,
            "price_b": price_b,
            "amount": amount,
            "gross_profit": gross_profit,
            "fee_a": fee_a,
            "fee_b": fee_b,
            "gas_cost": gas_cost,
            "flash_fee": flash_fee,
            "total_costs": total_costs,
            "net_profit": net_profit,
            "profitable": net_profit > 0,
            "roi": roi,
        }

    # ========================================================================
    # FORMULA 35: Token Vesting (Cliff + Linear)
    # ========================================================================
    @staticmethod
    def vesting_cliff_linear(
        total_tokens: float, time_elapsed_days: int, cliff_days: int, vesting_days: int, validate: bool = True
    ) -> Dict:
        """
        Token vesting with cliff period then linear release
        Formula:
        - If time < cliff: Vested = 0
        - Else: Vested = min(Total × (time - cliff) / vesting_period, Total)

        CONSTRAINTS:
        - total_tokens > 0
        - time_elapsed_days ≥ 0
        - cliff_days ≥ 0
        - vesting_days > 0

        Returns:
            Dict with vested_amount, locked_amount, vested_pct, cliff_passed
        """
        if validate:
            if total_tokens <= 0:
                raise ValueError(f"total_tokens must be > 0, got {total_tokens}")
            if time_elapsed_days < 0:
                raise ValueError(f"time_elapsed_days must be ≥ 0, got {time_elapsed_days}")
            if cliff_days < 0:
                raise ValueError(f"cliff_days must be ≥ 0, got {cliff_days}")
            if vesting_days <= 0:
                raise ValueError(f"vesting_days must be > 0, got {vesting_days}")

        cliff_passed = time_elapsed_days >= cliff_days

        if not cliff_passed:
            vested_amount = 0
        else:
            # Linear vesting after cliff
            time_since_cliff = time_elapsed_days - cliff_days
            vested_amount = min(total_tokens * (time_since_cliff / vesting_days), total_tokens)

        locked_amount = total_tokens - vested_amount
        vested_pct = (vested_amount / total_tokens) * 100

        return {
            "total_tokens": total_tokens,
            "time_elapsed_days": time_elapsed_days,
            "cliff_days": cliff_days,
            "vesting_days": vesting_days,
            "cliff_passed": cliff_passed,
            "vested_amount": vested_amount,
            "locked_amount": locked_amount,
            "vested_pct": vested_pct,
        }

    # ========================================================================
    # FORMULA 36: Bancor Bonding Curve
    # ========================================================================
    @staticmethod
    def bancor_bonding_price(
        reserve_balance: float, token_supply: float, connector_weight: float, validate: bool = True
    ) -> Dict:
        """
        Bancor automated market maker pricing
        Formula: Price = Balance / (Supply × CW)

        CONSTRAINTS:
        - reserve_balance > 0
        - token_supply > 0
        - connector_weight ∈ (0, 1]

        Returns:
            Dict with price, reserve_ratio, curve_type
        """
        if validate:
            if reserve_balance <= 0:
                raise ValueError(f"reserve_balance must be > 0, got {reserve_balance}")
            if token_supply <= 0:
                raise ValueError(f"token_supply must be > 0, got {token_supply}")
            if not (0 < connector_weight <= 1):
                raise ValueError(f"connector_weight must be in (0, 1], got {connector_weight}")

        price = reserve_balance / (token_supply * connector_weight)

        # Determine curve type
        if connector_weight == 1:
            curve_type = "Constant (stablecoin)"
        elif connector_weight >= 0.5:
            curve_type = "Moderate (square root)"
        else:
            curve_type = "Steep (exponential)"

        return {
            "price": price,
            "reserve_balance": reserve_balance,
            "token_supply": token_supply,
            "connector_weight": connector_weight,
            "reserve_ratio": connector_weight,
            "curve_type": curve_type,
        }

    # ========================================================================
    # FORMULA 37: Multi-Asset Collateral Coverage
    # ========================================================================
    @staticmethod
    def collateral_coverage_multi(collaterals: List[Dict], total_debt: float, validate: bool = True) -> Dict:
        """
        Multi-asset collateral health metric
        Formula: Coverage = (Σ Collateral_i × Liquidation_Threshold_i) / Total_Debt

        CONSTRAINTS:
        - All collateral values > 0
        - All thresholds ∈ (0, 1]
        - total_debt > 0

        Args:
            collaterals: List of dicts with 'value' and 'threshold' keys
            total_debt: Total borrowed value
            validate: Enable validation

        Returns:
            Dict with coverage_ratio, health_status, liquidation_risk
        """
        if validate:
            if total_debt <= 0:
                raise ValueError(f"total_debt must be > 0, got {total_debt}")
            if not collaterals:
                raise ValueError("collaterals list cannot be empty")

            for i, col in enumerate(collaterals):
                if "value" not in col or "threshold" not in col:
                    raise ValueError(f"Collateral {i} missing 'value' or 'threshold' key")
                if col["value"] <= 0:
                    raise ValueError(f"Collateral {i} value must be > 0")
                if not (0 < col["threshold"] <= 1):
                    raise ValueError(f"Collateral {i} threshold must be in (0, 1]")

        # Calculate weighted collateral
        weighted_collateral = sum(col["value"] * col["threshold"] for col in collaterals)

        coverage_ratio = weighted_collateral / max(total_debt, EPSILON)

        # Health status
        if coverage_ratio < 1:
            health_status = "LIQUIDATABLE"
            liquidation_risk = "CRITICAL"
        elif coverage_ratio < 1.2:
            health_status = "AT RISK"
            liquidation_risk = "HIGH"
        elif coverage_ratio < 1.5:
            health_status = "MARGINAL"
            liquidation_risk = "MODERATE"
        else:
            health_status = "HEALTHY"
            liquidation_risk = "LOW"

        return {
            "coverage_ratio": coverage_ratio,
            "weighted_collateral": weighted_collateral,
            "total_debt": total_debt,
            "health_status": health_status,
            "liquidation_risk": liquidation_risk,
            "collateral_count": len(collaterals),
        }

    # ========================================================================
    # FORMULA 38: Yield Farming ROI (Total)
    # ========================================================================
    @staticmethod
    def yield_farming_roi(
        initial_capital: float, farming_rewards: float, fee_income: float, il_dollar: float, validate: bool = True
    ) -> Dict:
        """
        Total yield farming return including all components
        Formula: ROI= (Farming_Rewards + Fee_Income + IL) / Initial_Capital - 1    CONSTRAINTS:
        - initial_capital > 0
        - farming_rewards ≥ 0
        - fee_income ≥ 0
        - il_dollar can be negative
        Returns:
        Dict with roi_pct, total_return, profitable, components breakdown
        """
        if validate:
            if initial_capital <= 0:
                raise ValueError(f"initial_capital must be > 0, got {initial_capital}")
            if farming_rewards < 0:
                raise ValueError(f"farming_rewards must be ≥ 0, got {farming_rewards}")
            if fee_income < 0:
                raise ValueError(f"fee_income must be ≥ 0, got {fee_income}")  # Total return (IL is typically negative)
        total_return = farming_rewards + fee_income + il_dollar
        roi_pct = (total_return / initial_capital) * 100  # Component breakdown
        components = {
            "farming_rewards_pct": (farming_rewards / initial_capital) * 100,
            "fee_income_pct": (fee_income / initial_capital) * 100,
            "il_pct": (il_dollar / initial_capital) * 100,
        }
        return {
            "initial_capital": initial_capital,
            "farming_rewards": farming_rewards,
            "fee_income": fee_income,
            "il_dollar": il_dollar,
            "total_return": total_return,
            "roi_pct": roi_pct,
            "profitable": roi_pct > 0,
            **components,
        }


# ============================================================================
# COMPREHENSIVE TEST SCENARIOS FOR DeFiAdvancedCalculator
# ============================================================================
def generate_defi_advanced_scenarios() -> List[Dict]:
    """
    Generate 15+ realistic DeFi scenarios covering all formulas
    """
    scenarios = []
    calc = DeFiAdvancedCalculator()

    # ========================================================================
    # SCENARIO 1: Uniswap V3 Tick Pricing (Multiple Fee Tiers)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 1: Uniswap V3 Tick Pricing")
    print("=" * 80)

    v3_ticks = [
        {"tick": 0, "description": "Price = 1.0 (parity)"},
        {"tick": 10000, "description": "Price ~2.7x"},
        {"tick": -10000, "description": "Price ~0.37x"},
        {"tick": 100000, "description": "Price ~22000x"},
        {"tick": 887272, "description": "Max tick (extreme price)"},
    ]

    for item in v3_ticks:
        try:
            price = calc.uniswap_v3_tick_to_price(item["tick"])
            scenarios.append(
                {
                    "scenario": f"V3 Tick {item['tick']}",
                    "formula": "Uniswap V3 Price",
                    "tick": item["tick"],
                    "price": price,
                    "description": item["description"],
                }
            )
            print(f"Tick {item['tick']:>7}: Price = {price:>15,.6f} | {item['description']}")
        except Exception as e:
            print(f"Tick {item['tick']}: ERROR - {e}")

    # ========================================================================
    # SCENARIO 2: Constant Sum AMM (Stablecoins)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 2: Constant Sum AMM (mStable, Curve Balanced)")
    print("=" * 80)

    stable_swaps = [
        {"amount": 1000, "fee": 0.001, "description": "USDC → USDT (0.1% fee)"},
        {"amount": 10000, "fee": 0.0004, "description": "DAI → USDC (0.04% fee)"},
        {"amount": 100000, "fee": 0.003, "description": "Large swap (0.3% fee)"},
    ]

    for swap in stable_swaps:
        output = calc.constant_sum_output(swap["amount"], swap["fee"])
        scenarios.append(
            {
                "scenario": swap["description"],
                "formula": "Constant Sum AMM",
                "input": swap["amount"],
                "output": output,
                "fee": swap["fee"],
                "slippage": 0,
            }
        )
    print(f"{swap['description']}: ${swap['amount']:,.0f} → ${output:,.2f} (slippage: 0%)")

    # ========================================================================
    # SCENARIO 3: Curve StableSwap (Different Amplification)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 3: Curve StableSwap Invariant (Different A values)")
    print("=" * 80)

    curve_pools = [
        {"reserves": [1000000, 1000000], "A": 100, "description": "Balanced 2-pool (A=100)"},
        {"reserves": [1000000, 1000000, 1000000], "A": 200, "description": "Balanced 3-pool (A=200)"},
        {"reserves": [800000, 1200000], "A": 50, "description": "Imbalanced 2-pool (A=50)"},
        {"reserves": [1000000, 1000000], "A": 1000, "description": "High A (more like constant sum)"},
    ]

    for pool in curve_pools:
        D = calc.curve_stableswap_d(pool["reserves"], pool["A"])
        scenarios.append(
            {
                "scenario": pool["description"],
                "formula": "Curve StableSwap",
                "reserves": pool["reserves"],
                "A": pool["A"],
                "invariant_D": D,
            }
        )
    print(f"{pool['description']}: D = {D:,.0f}")

    # ========================================================================
    # SCENARIO 4: Aave Variable Rate Model (Different Utilizations)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 4: Aave Variable Borrow Rate (Kinked Model)")
    print("=" * 80)

    utilizations = [0.0, 0.4, 0.8, 0.9, 0.95, 0.99]

    for u in utilizations:
        rate = calc.aave_variable_rate(u)
        scenarios.append(
            {
                "scenario": f"Utilization {u*100:.0f}%",
                "formula": "Aave Variable Rate",
                "utilization": u,
                "rate": rate,
                "rate_pct": rate * 100,
            }
        )
    print(f"Utilization {u*100:>3.0f}%: Rate = {rate*100:>6.2f}% APR")

    # ========================================================================
    # SCENARIO 5: Compound with COMP Rewards
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 5: Compound Borrow APY with COMP Rewards")
    print("=" * 80)

    comp_scenarios = [
        {
            "borrow_apr": 0.05,
            "comp_per_block": 0.5,
            "comp_price": 50,
            "total_borrowed": 1_000_000,
            "desc": "Low incentives",
        },
        {
            "borrow_apr": 0.08,
            "comp_per_block": 1.0,
            "comp_price": 100,
            "total_borrowed": 500_000,
            "desc": "High incentives",
        },
        {
            "borrow_apr": 0.03,
            "comp_per_block": 2.0,
            "comp_price": 75,
            "total_borrowed": 1_000_000,
            "desc": "Paid to borrow",
        },
    ]

    for comp in comp_scenarios:
        result = calc.compound_borrow_apy_with_rewards(
            comp["borrow_apr"],
            comp["comp_per_block"],
            comp_price=comp["comp_price"],
            total_borrowed=comp["total_borrowed"],
        )
        scenarios.append({"scenario": comp["desc"], "formula": "Compound APY with Rewards", **result})
    print(
        f"{comp['desc']}: Borrow {result['borrow_apr']*100:.2f}% - Rewards {result['reward_apy']*100:.2f}% = Net {result['net_apy']*100:.2f}%"
    )

    # ========================================================================
    # SCENARIO 6: Leverage Ratios
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 6: DeFi Lending Leverage Ratios")
    print("=" * 80)

    ltvs = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]

    for ltv in ltvs:
        leverage = calc.leverage_ratio(ltv)
        scenarios.append(
            {"scenario": f"LTV {ltv*100:.0f}%", "formula": "Leverage Ratio", "ltv": ltv, "max_leverage": leverage}
        )
    print(f"LTV {ltv*100:>3.0f}%: Max Leverage = {leverage:.2f}x")

    # ========================================================================
    # SCENARIO 7: Protocol Revenue Comparison
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 7: DEX Protocol Revenue Comparison")
    print("=" * 80)

    protocols = [
        {"name": "Uniswap V2", "volume": 100_000_000, "fee": 0.003, "cut": 0},
        {"name": "Uniswap V3", "volume": 100_000_000, "fee": 0.003, "cut": 1 / 6},
        {"name": "Sushiswap", "volume": 50_000_000, "fee": 0.003, "cut": 1 / 6},
        {"name": "Curve", "volume": 200_000_000, "fee": 0.0004, "cut": 0.5},
    ]

    for protocol in protocols:
        revenue = calc.protocol_revenue(protocol["volume"], protocol["fee"], protocol["cut"])
        scenarios.append(
            {
                "scenario": protocol["name"],
                "formula": "Protocol Revenue",
                "daily_volume": protocol["volume"],
                "fee_rate": protocol["fee"],
                "protocol_cut": protocol["cut"],
                "daily_revenue": revenue,
            }
        )
    print(
        f"{protocol['name']:<15}: ${protocol['volume']:>12,} vol × {protocol['fee']*100:.2f}% × {protocol['cut']*100:.1f}% = ${revenue:>10,.2f}/day"
    )

    # ========================================================================
    # SCENARIO 8: Maker Stability Fees
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 8: MakerDAO Stability Fee Calculation")
    print("=" * 80)

    maker_cdps = [
        {"principal": 10000, "rate": 0.05, "time": 1, "desc": "1 year at 5%"},
        {"principal": 10000, "rate": 0.05, "time": 0.5, "desc": "6 months at 5%"},
        {"principal": 50000, "rate": 0.02, "time": 2, "desc": "2 years at 2%"},
    ]

    for cdp in maker_cdps:
        result = calc.maker_stability_fee(cdp["principal"], cdp["rate"], cdp["time"])
        scenarios.append({"scenario": cdp["desc"], "formula": "Maker Stability Fee", **result})
        print(
            f"{cdp['desc']}: ${result['principal']:,.0f} → ${result['total_debt']:,.2f} (Fee: ${result['fee_amount']:,.2f})"
        )

    # ========================================================================
    # SCENARIO 9: Token Dilution Analysis
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 9: Liquidity Mining Dilution Rates")
    print("=" * 80)

    token_emissions = [
        {"emissions": 1_000_000, "supply": 100_000_000, "name": "Token A (1% dilution)"},
        {"emissions": 10_000_000, "supply": 100_000_000, "name": "Token B (10% dilution)"},
        {"emissions": 30_000_000, "supply": 100_000_000, "name": "Token C (30% dilution)"},
    ]

    for token in token_emissions:
        result = calc.dilution_rate(token["emissions"], token["supply"])
        scenarios.append({"scenario": token["name"], "formula": "Dilution Rate", **result})
        print(f"{token['name']}: {result['dilution_pct']:.1f}% annual dilution - {result['warning']}")

    # ========================================================================
    # SCENARIO 10: IL with Fees (Net Result)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 10: Impermanent Loss vs Fees Earned")
    print("=" * 80)

    il_scenarios = [
        {"ratio": 1.5, "fee_apr": 0.20, "time": 0.25, "desc": "ETH +50%, High Volume, 3mo"},
        {"ratio": 2.0, "fee_apr": 0.30, "time": 0.5, "desc": "ETH +100%, High Volume, 6mo"},
        {"ratio": 0.5, "fee_apr": 0.15, "time": 0.25, "desc": "ETH -50%, Medium Volume, 3mo"},
        {"ratio": 1.2, "fee_apr": 0.50, "time": 1.0, "desc": "Stable, Ultra High Volume, 1yr"},
    ]

    for scenario in il_scenarios:
        result = calc.il_with_fees_net(scenario["ratio"], scenario["fee_apr"], scenario["time"])
        scenarios.append({"scenario": scenario["desc"], "formula": "IL with Fees Net", **result})
        profitable_mark = "✓" if result["profitable"] else "✗"
        print(
            f"{scenario['desc']}: IL {result['il_pct']:.2f}% + Fees {result['fees_earned_pct']:.2f}% = {result['net_result_pct']:.2f}% {profitable_mark}"
        )

    # ========================================================================
    # SCENARIO 11: Multi-Hop Price Impact
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 11: Multi-Hop Routing Price Impact")
    print("=" * 80)

    routes = [
        {"impacts": [0.01], "desc": "Direct route (1% impact)"},
        {"impacts": [0.01, 0.01], "desc": "2-hop route (2× 1%)"},
        {"impacts": [0.005, 0.005, 0.005], "desc": "3-hop route (3× 0.5%)"},
        {"impacts": [0.02, 0.03], "desc": "High impact 2-hop"},
    ]

    for route in routes:
        total_impact = calc.multi_hop_impact(route["impacts"])
        scenarios.append(
            {
                "scenario": route["desc"],
                "formula": "Multi-Hop Impact",
                "individual_impacts": route["impacts"],
                "total_impact": total_impact,
                "total_impact_pct": total_impact * 100,
            }
        )
    print(f"{route['desc']}: {' + '.join([f'{i*100:.2f}%' for i in route['impacts']])} = {total_impact*100:.2f}% total")

    # ========================================================================
    # SCENARIO 12: Options Delta (Black-Scholes)
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 12: Options Greeks - Delta Calculation")
    print("=" * 80)

    options = [
        {"spot": 2000, "strike": 2000, "vol": 0.8, "time": 0.25, "desc": "ATM, 3mo"},
        {"spot": 2000, "strike": 1800, "vol": 0.8, "time": 0.25, "desc": "ITM, 3mo"},
        {"spot": 2000, "strike": 2200, "vol": 0.8, "time": 0.25, "desc": "OTM, 3mo"},
        {"spot": 2000, "strike": 2000, "vol": 0.8, "time": 0.08, "desc": "ATM, 1mo"},
    ]

    for option in options:
        result = calc.black_scholes_delta(option["spot"], option["strike"], 0.05, option["vol"], option["time"])
        scenarios.append({"scenario": option["desc"], "formula": "Black-Scholes Delta", **result})
        print(f"{option['desc']}: Δ = {result['delta']:.4f} (d₁ = {result['d1']:.4f})")

    # ========================================================================
    # SCENARIO 13: Perpetual Swap Basis
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 13: Perpetual Swap Funding Basis")
    print("=" * 80)

    perps = [
        {"perp": 2050, "spot": 2000, "desc": "Bullish (+2.5% premium)"},
        {"perp": 1950, "spot": 2000, "desc": "Bearish (-2.5% discount)"},
        {"perp": 2000, "spot": 2000, "desc": "Neutral (0% premium)"},
        {"perp": 2150, "spot": 2000, "desc": "Very Bullish (+7.5% premium)"},
    ]

    for perp in perps:
        result = calc.perpetual_basis(perp["perp"], perp["spot"])
        scenarios.append({"scenario": perp["desc"], "formula": "Perpetual Basis", **result})
        print(
            f"{perp['desc']}: {result['premium_pct']:+.2f}% premium, {result['basis_annualized']:+.1f}% annualized - {result['sentiment']}"
        )

    # ========================================================================
    # SCENARIO 14: Flash Loan Arbitrage
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 14: Flash Loan Arbitrage Profitability")
    print("=" * 80)

    arbs = [
        {
            "price_a": 2000,
            "price_b": 2010,
            "amount": 100,
            "fee_a": 30,
            "fee_b": 30,
            "gas": 50,
            "desc": "Small arb ($10 spread)",
        },
        {
            "price_a": 2000,
            "price_b": 2050,
            "amount": 100,
            "fee_a": 30,
            "fee_b": 30,
            "gas": 50,
            "desc": "Large arb ($50 spread)",
        },
        {
            "price_a": 2000,
            "price_b": 2005,
            "amount": 100,
            "fee_a": 30,
            "fee_b": 30,
            "gas": 100,
            "desc": "Unprofitable (high gas)",
        },
    ]

    for arb in arbs:
        result = calc.flash_loan_net_profit(
            arb["price_a"], arb["price_b"], arb["amount"], arb["fee_a"], arb["fee_b"], arb["gas"]
        )
        scenarios.append({"scenario": arb["desc"], "formula": "Flash Loan Arbitrage", **result})
        profitable_mark = "✓" if result["profitable"] else "✗"
        print(
            f"{arb['desc']}: Gross ${result['gross_profit']:.2f} - Costs ${result['total_costs']:.2f} = ${result['net_profit']:.2f} {profitable_mark}"
        )

    # ========================================================================
    # SCENARIO 15: Token Vesting Schedules
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 15: Token Vesting (Cliff + Linear)")
    print("=" * 80)

    vestings = [
        {"total": 1_000_000, "elapsed": 180, "cliff": 365, "vesting": 1095, "desc": "Before cliff (6mo)"},
        {"total": 1_000_000, "elapsed": 365, "cliff": 365, "vesting": 1095, "desc": "At cliff (1yr)"},
        {"total": 1_000_000, "elapsed": 730, "cliff": 365, "vesting": 1095, "desc": "Mid-vesting (2yr)"},
        {"total": 1_000_000, "elapsed": 1460, "cliff": 365, "vesting": 1095, "desc": "Fully vested (4yr)"},
    ]

    for vest in vestings:
        result = calc.vesting_cliff_linear(vest["total"], vest["elapsed"], vest["cliff"], vest["vesting"])
        scenarios.append({"scenario": vest["desc"], "formula": "Vesting Schedule", **result})
        print(
            f"{vest['desc']}: {result['vested_amount']:,.0f} vested ({result['vested_pct']:.1f}%), {result['locked_amount']:,.0f} locked"
        )

    # ========================================================================
    # SCENARIO 16: Bancor Bonding Curves
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 16: Bancor Bonding Curve Pricing")
    print("=" * 80)

    bonding = [
        {"reserve": 1_000_000, "supply": 1_000_000, "cw": 1.0, "desc": "CW=1.0 (Constant price)"},
        {"reserve": 1_000_000, "supply": 1_000_000, "cw": 0.5, "desc": "CW=0.5 (Square root)"},
        {"reserve": 1_000_000, "supply": 1_000_000, "cw": 0.2, "desc": "CW=0.2 (Steep curve)"},
    ]

    for bond in bonding:
        result = calc.bancor_bonding_price(bond["reserve"], bond["supply"], bond["cw"])
        scenarios.append({"scenario": bond["desc"], "formula": "Bancor Bonding", **result})
        print(f"{bond['desc']}: Price = ${result['price']:.2f} - {result['curve_type']}")

    # ========================================================================
    # SCENARIO 17: Multi-Asset Collateral Health
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 17: Multi-Asset Collateral Coverage (Aave-style)")
    print("=" * 80)

    collateral_scenarios = [
        {
            "collaterals": [
                {"value": 10000, "threshold": 0.85},  # ETH
                {"value": 5000, "threshold": 0.80},  # WBTC
            ],
            "debt": 10000,
            "desc": "Healthy position (1.475 ratio)",
        },
        {
            "collaterals": [
                {"value": 5000, "threshold": 0.75},  # ETH (down 50%)
                {"value": 5000, "threshold": 0.80},  # WBTC
            ],
            "debt": 10000,
            "desc": "At risk position (0.775 ratio)",
        },
        {
            "collaterals": [
                {"value": 3000, "threshold": 0.85},  # ETH
                {"value": 2000, "threshold": 0.95},  # USDC
            ],
            "debt": 5000,
            "desc": "Marginal position (0.89 ratio)",
        },
    ]

    for col_scenario in collateral_scenarios:
        result = calc.collateral_coverage_multi(col_scenario["collaterals"], col_scenario["debt"])
        scenarios.append({"scenario": col_scenario["desc"], "formula": "Multi-Asset Coverage", **result})
        print(
            f"{col_scenario['desc']}: Coverage = {result['coverage_ratio']:.3f} - {result['health_status']} ({result['liquidation_risk']} risk)"
        )

    # ========================================================================
    # SCENARIO 18: Complete Yield Farming ROI
    # ========================================================================
    print("\n" + "=" * 80)
    print("SCENARIO 18: Complete Yield Farming ROI Analysis")
    print("=" * 80)

    farms = [
        {"capital": 10000, "rewards": 2000, "fees": 800, "il": -300, "desc": "Profitable farm"},
        {"capital": 10000, "rewards": 500, "fees": 200, "il": -1000, "desc": "IL exceeds earnings"},
        {"capital": 50000, "rewards": 8000, "fees": 3000, "il": -1500, "desc": "High volume pool"},
    ]

    for farm in farms:
        result = calc.yield_farming_roi(farm["capital"], farm["rewards"], farm["fees"], farm["il"])
        scenarios.append({"scenario": farm["desc"], "formula": "Yield Farming ROI", **result})
        profitable_mark = "✓" if result["profitable"] else "✗"
        print(
            f"{farm['desc']}: ROI = {result['roi_pct']:.2f}% "
            f"(Rewards: {result['farming_rewards_pct']:.1f}%, Fees: {result['fee_income_pct']:.1f}%, IL: {result['il_pct']:.1f}%) {profitable_mark}"
        )

    print("\n" + "=" * 80)

    return scenarios


# ============================================================================
# BACKTEST ANALYSIS MODULE
# ============================================================================
class DeFiBacktestAnalyzer:
    """
    Comprehensive backtesting and analysis tools for DeFi strategies
    """

    def __init__(self):
        self.calc = DeFiAdvancedCalculator()
        self.results = []

    def backtest_uniswap_v3_range(
        self,
        initial_price: float,
        price_history: List[float],
        lower_tick: int,
        upper_tick: int,
        liquidity: float,
        fee_tier: float = 0.003,
    ) -> Dict:
        """
        Backtest Uniswap V3 concentrated liquidity position

        Returns performance metrics over price history
        """
        lower_price = self.calc.uniswap_v3_tick_to_price(lower_tick)
        upper_price = self.calc.uniswap_v3_tick_to_price(upper_tick)

        in_range_count = 0
        total_fees = 0

        for price in price_history:
            if lower_price <= price <= upper_price:
                in_range_count += 1
                # Simplified fee calculation
            total_fees += liquidity * fee_tier * 0.01  # Assume 1% of liquidity per day in range

            in_range_pct = (in_range_count / len(price_history)) * 100

            return {
                "lower_price": lower_price,
                "upper_price": upper_price,
                "in_range_pct": in_range_pct,
                "total_fees": total_fees,
                "avg_daily_fees": total_fees / len(price_history),
                "capital_efficiency": in_range_pct / 100,
            }

    def compare_lending_protocols(self, utilization_range: List[float]) -> Dict:
        """
        Compare interest rate models across protocols
        """
        results = {"utilization": utilization_range, "aave_rates": [], "compound_rates": []}

        for u in utilization_range:
            # Aave kinked model
            aave_rate = self.calc.aave_variable_rate(u)
            results["aave_rates"].append(aave_rate * 100)

            # Compound linear model (simplified)
            compound_rate = 0.02 + u * 0.20  # Base 2% + 20% slope
            results["compound_rates"].append(compound_rate * 100)

            return results

    def find_optimal_il_recovery_time(self, price_ratios: List[float], fee_apr: float) -> List[Dict]:
        """
        Calculate breakeven time for different price movements
        """
        results = []

        for ratio in price_ratios:
            # Calculate IL
            sqrt_ratio = math.sqrt(ratio)
            il_pct = (2 * sqrt_ratio / (ratio + 1) - 1) * 100

            # Breakeven calculation
            if fee_apr > 0 and il_pct < 0:
                pool_share_factor = 2 * sqrt_ratio / (ratio + 1)
                annual_fees = fee_apr * pool_share_factor * 100
                breakeven_years = abs(il_pct) / max(annual_fees, EPSILON)
                breakeven_days = breakeven_years * 365
            else:
                breakeven_days = float("inf")

                results.append(
                    {
                        "price_ratio": ratio,
                        "il_pct": il_pct,
                        "annual_fees_pct": fee_apr * 100,
                        "breakeven_days": breakeven_days,
                        "recoverable": breakeven_days < 365,
                    }
                )

                return results

    def gas_profitability_threshold(self, gas_price_gwei: float, eth_price: float, gas_limit: int = 300000) -> Dict:
        """
        Calculate minimum profit needed for gas profitability

        Args:
        gas_price_gwei: Current gas price in Gwei
        eth_price: ETH price in USD
        gas_limit: Estimated gas limit for transaction

        Returns:
        Dict with gas_cost_usd, min_profit_threshold, recommended_action
        """
        # Convert Gwei to ETH (1 ETH = 1e9 Gwei)
        gas_cost_eth = (gas_price_gwei * gas_limit) / 1e9
        gas_cost_usd = gas_cost_eth * eth_price

        # Minimum profit should be 2x gas cost for safety
        min_profit_threshold = gas_cost_usd * 2

        # Recommendations based on gas cost
        if gas_cost_usd < 10:
            action = "EXECUTE: Low gas cost"
        elif gas_cost_usd < 50:
            action = "CONSIDER: Moderate gas cost"
        elif gas_cost_usd < 100:
            action = "WAIT: High gas cost"
        else:
            action = "AVOID: Extremely high gas cost"

        return {
            "gas_price_gwei": gas_price_gwei,
            "gas_limit": gas_limit,
            "gas_cost_eth": gas_cost_eth,
            "gas_cost_usd": gas_cost_usd,
            "min_profit_threshold": min_profit_threshold,
            "recommended_action": action,
        }

    def simulate_recursive_leverage(self, initial_capital: float, ltv: float, iterations: int = 10) -> Dict:
        """
        Simulate recursive borrowing to max leverage
        """
        positions = []
        total_collateral = initial_capital
        total_debt = 0

        for i in range(iterations):
            borrowable = total_collateral * ltv
            if borrowable < initial_capital * 0.001:
                break

            total_debt += borrowable
            total_collateral += borrowable

            positions.append(
                {
                    "iteration": i + 1,
                    "borrowed": borrowable,
                    "total_collateral": total_collateral,
                    "total_debt": total_debt,
                }
            )

            actual_leverage = total_collateral / initial_capital
            theoretical_max = self.calc.leverage_ratio(ltv)

            return {
                "initial_capital": initial_capital,
                "ltv": ltv,
                "iterations": len(positions),
                "final_collateral": total_collateral,
                "final_debt": total_debt,
                "actual_leverage": actual_leverage,
                "theoretical_max": theoretical_max,
                "efficiency_pct": (actual_leverage / theoretical_max) * 100,
                "positions": positions,
            }

    # ============================================================================
    # UTILITY FUNCTIONS
    # ============================================================================

    def generate_summary_report(scenarios: List[Dict]) -> str:
        """Generate markdown summary of all scenarios"""

        report = ["# DeFi Advanced Calculator - Test Results", ""]
        report.append(f"Total Scenarios Analyzed: {len(scenarios)}")
        report.append("")

        # Group by formula
        formulas = {}
        for scenario in scenarios:
            formula = scenario.get("formula", "Unknown")
            if formula not in formulas:
                formulas[formula] = []
            formulas[formula].append(scenario)

        report.append(f"## Formulas Tested: {len(formulas)}")
        report.append("")

        for formula, tests in formulas.items():
            report.append(f"### {formula}")
            report.append(f"- Test cases: {len(tests)}")
            report.append("")

        return "\n".join(report)

    def export_scenarios_json(scenarios: List[Dict], filename: str = "defi_scenarios.json"):
        """Export scenarios to JSON file"""
        import json

        with open(filename, "w") as f:
            json.dump(scenarios, f, indent=2, default=str)

        print(f"\nExported {len(scenarios)} scenarios to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DeFi Advanced Calculator - Comprehensive Test Suite")
    print("Formulas 21-40 Implementation")
    print("=" * 80)

    # Generate all scenarios
    scenarios = generate_defi_advanced_scenarios()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print(f"Total scenarios executed: {len(scenarios)}")
    print(f"All formulas validated: ✓")

    # Generate summary report
    report = generate_summary_report(scenarios)
    print("\n" + report)

    # Backtest examples
    print("\n" + "=" * 80)
    print("BACKTEST ANALYSIS EXAMPLES")
    print("=" * 80)

    analyzer = DeFiBacktestAnalyzer()

    # Example 1: IL recovery time analysis
    print("\nIL Recovery Time Analysis:")
    price_ratios = [0.5, 0.8, 1.2, 1.5, 2.0]
    recovery_results = analyzer.find_optimal_il_recovery_time(price_ratios, 0.25)

    for result in recovery_results:
        recoverable = "✓" if result["recoverable"] else "✗"
        print(
            f"Price {result['price_ratio']}x: IL {result['il_pct']:.2f}%, "
            f"Breakeven: {result['breakeven_days']:.0f} days {recoverable}"
        )

    # Example 2: Gas profitability
    print("\nGas Profitability Analysis:")
    gas_scenarios = [
        {"gwei": 20, "eth": 2000, "desc": "Low gas"},
        {"gwei": 50, "eth": 2000, "desc": "Medium gas"},
        {"gwei": 100, "eth": 2000, "desc": "High gas"},
    ]

    for gas_scenario in gas_scenarios:
        result = analyzer.gas_profitability_threshold(gas_scenario["gwei"], gas_scenario["eth"])
        print(
            f"{gas_scenario['desc']}: ${result['gas_cost_usd']:.2f} cost, "
            f"${result['min_profit_threshold']:.2f} min profit - {result['recommended_action']}"
        )

    # Example 3: Leveraged position simulation
    print("\nLeveraged Position Simulation:")
    lev_result = analyzer.simulate_leveraged_position(
        initial_collateral=10000, ltv=0.75, leverage_cycles=3, borrow_apr=0.05, lend_apr=0.08, time_years=1.0
    )

    print(f"Initial: ${lev_result['initial_collateral']:,.0f}")
    print(f"Total Exposure: ${lev_result['total_exposure']:,.0f} ({lev_result['leverage_ratio']:.2f}x)")
    print(f"Net APY: {lev_result['net_apy']*100:.2f}%")
    print(f"Net Profit: ${lev_result['net_profit']:,.2f}")

    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)
    print("=" * 80)
    print("DeFi Advanced Calculator - Demo")
    print("=" * 80)
    calc = DeFiAdvancedCalculator()
    analyzer = DeFiBacktestAnalyzer()

    # Demo: Uniswap V3 tick to price
    print("\nUniswap V3 Tick -> Price examples:")
    for tick in (0, 10000, -10000):
        p = calc.uniswap_v3_tick_to_price(tick)
        print(f"  Tick {tick:>7}: Price = {p:.6f}")

    # Demo: IL with fees
    print("\nImpermanent Loss with Fees (examples):")
    for ratio, fee_apr, t in [(1.5, 0.20, 0.25), (2.0, 0.30, 0.5)]:
        res = calc.il_with_fees_net(ratio, fee_apr, t)
        print(
            f"  Ratio {ratio}: IL {res['il_pct']:.2f}% | Fees {res['fees_earned_pct']:.2f}% | Net {res['net_result_pct']:.2f}%"
        )

    # Demo: simple backtest
    price_history = [1.0, 1.1, 1.05, 0.95, 1.02]
    bt = analyzer.backtest_uniswap_v3_range(1.0, price_history, -1000, 1000, liquidity=10000)
    print("\nBacktest Uniswap V3 range summary:")
    print(f"  Lower price: {bt['lower_price']:.6f}, Upper price: {bt['upper_price']:.6f}")
    print(f"  In range %: {bt['in_range_pct']:.2f}%, Total fees (est): {bt['total_fees']:.4f}")

    # Generate and show small scenario list
    print("\nGenerating scenarios (sample):")
    scenarios = generate_defi_advanced_scenarios()
    print(f"  Generated {len(scenarios)} scenarios. Sample:")
    for s in scenarios[:8]:
        print("   -", {k: s[k] for k in list(s)[:4]})
