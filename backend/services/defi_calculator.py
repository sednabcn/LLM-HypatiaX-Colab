from typing import Dict


class DeFiCalculator:
    """DeFi formulas calculator for Uniswap V2 pools"""

    @staticmethod
    def calculate_il_percentage(current_price: float, initial_price: float) -> float:
        """Calculate impermanent loss percentage"""
        if initial_price == 0:
            return 0
        ratio = current_price / initial_price
        il = (2 * (ratio**0.5) / (ratio + 1) - 1) * 100
        return round(il, 4)

    @staticmethod
    def calculate_quality_score(
        daily_volume_usd: float,
        fee_rate: float,
        position_value: float,
        pool_tvl: float,
        il_dollar: float,
        days_elapsed: int,
    ) -> Dict:
        """Calculate pool quality score"""

        # Calculate daily fees
        pool_share = position_value / pool_tvl if pool_tvl > 0 else 0
        daily_fees = daily_volume_usd * fee_rate * pool_share

        # Calculate daily IL rate
        daily_il_rate = abs(il_dollar) / days_elapsed if days_elapsed > 0 else 0

        # Quality score
        quality_score = daily_fees / daily_il_rate if daily_il_rate > 0 else float("inf")

        # Classify tier
        if quality_score > 1.0:
            tier = "GOOD"
        elif quality_score >= 0.5:
            tier = "MODERATE"
        else:
            tier = "POOR"

        return {
            "daily_fees": round(daily_fees, 2),
            "daily_il_rate": round(daily_il_rate, 2),
            "quality_score": round(quality_score, 3) if quality_score != float("inf") else "inf",
            "quality_tier": tier,
        }

    @staticmethod
    def calculate_position_analytics(
        initial_token_a: float,
        initial_token_b: float,
        initial_price: float,
        current_price: float,
        days_elapsed: int,
        daily_volume: float,
        pool_tvl: float,
        fee_rate: float = 0.003,
    ) -> Dict:
        """Complete position analysis"""

        # IL calculation
        il_percent = DeFiCalculator.calculate_il_percentage(current_price, initial_price)

        # Position value
        position_value = initial_token_a * current_price + initial_token_b
        il_dollar = position_value * (il_percent / 100)

        # Quality score
        quality = DeFiCalculator.calculate_quality_score(
            daily_volume, fee_rate, position_value, pool_tvl, il_dollar, days_elapsed
        )

        # Net result
        total_fees = quality["daily_fees"] * days_elapsed
        net_result = total_fees - abs(il_dollar)

        # Breakeven
        breakeven_days = abs(il_dollar) / quality["daily_fees"] if quality["daily_fees"] > 0 else float("inf")

        return {
            "il_percent": il_percent,
            "il_dollar": round(il_dollar, 2),
            "position_value": round(position_value, 2),
            "daily_fees": quality["daily_fees"],
            "total_fees": round(total_fees, 2),
            "net_result": round(net_result, 2),
            "quality_score": quality["quality_score"],
            "quality_tier": quality["quality_tier"],
            "breakeven_days": round(breakeven_days, 2) if breakeven_days != float("inf") else "inf",
            "profitable": net_result > 0,
        }
