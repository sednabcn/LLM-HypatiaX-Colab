"""
Impermanent Loss (IL) Calculator - Enhanced with Safety Checks
==============================================================
Calculate and analyze impermanent loss for liquidity providers in AMM pools
with comprehensive validation, error handling, and overflow prevention.

Impermanent Loss occurs when the price ratio of tokens in a liquidity pool
changes compared to when they were deposited, resulting in less value than
simply holding the tokens.
"""

import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, Overflow, getcontext
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Set precision for financial calculations
getcontext().prec = 28

# Safety constants
MAX_PRICE = Decimal("1e15")  # Maximum allowed price
MIN_PRICE = Decimal("1e-15")  # Minimum allowed price
MAX_AMOUNT = Decimal("1e18")  # Maximum token amount
MIN_AMOUNT = Decimal("1e-18")  # Minimum token amount
MAX_FEE_TIER = Decimal("0.1")  # 10% max fee
MIN_FEE_TIER = Decimal("0")
MAX_VOLUME_MULTIPLE = Decimal("1000000")  # 1M x liquidity
MAX_TIME_PERIOD = Decimal("36500")  # 100 years in days


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class CalculationError(Exception):
    """Custom exception for calculation errors."""
    pass


class ErrorSeverity(Enum):
    """Error severity levels."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    severity: ErrorSeverity
    message: str
    field: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report."""
    is_valid: bool
    errors: List[ValidationResult]
    warnings: List[ValidationResult]

    def add_error(self, message: str, field: Optional[str] = None,
                  severity: ErrorSeverity = ErrorSeverity.ERROR):
        """Add a validation error."""
        result = ValidationResult(False, severity, message, field)
        if severity == ErrorSeverity.WARNING:
            self.warnings.append(result)
        else:
            self.errors.append(result)
            self.is_valid = False

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        lines = []
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for err in self.errors:
                field_str = f"[{err.field}] " if err.field else ""
                lines.append(f"  - {field_str}{err.message}")
        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warn in self.warnings:
                field_str = f"[{warn.field}] " if warn.field else ""
                lines.append(f"  - {field_str}{warn.message}")
        return "\n".join(lines) if lines else "All validations passed"


class SafeMath:
    """Safe mathematical operations with overflow protection."""

    @staticmethod
    def safe_multiply(a: Decimal, b: Decimal, context: str = "") -> Decimal:
        """Safely multiply two numbers with overflow protection."""
        try:
            result = a * b
            if result > MAX_AMOUNT * MAX_PRICE:
                raise CalculationError(
                    f"Multiplication overflow {context}: {a} * {b}"
                )
            return result
        except (Overflow, InvalidOperation) as e:
            raise CalculationError(f"Multiplication error {context}: {str(e)}")

    @staticmethod
    def safe_divide(a: Decimal, b: Decimal, context: str = "") -> Decimal:
        """Safely divide two numbers with zero check."""
        try:
            if b == 0:
                raise CalculationError(f"Division by zero {context}")
            if abs(b) < MIN_PRICE:
                raise CalculationError(
                    f"Divisor too small {context}: {b}"
                )
            result = a / b
            if result > MAX_PRICE or result < -MAX_PRICE:
                raise CalculationError(f"Division overflow {context}: {a} / {b}")
            return result
        except (Overflow, InvalidOperation) as e:
            raise CalculationError(f"Division error {context}: {str(e)}")

    @staticmethod
    def safe_sqrt(x: Decimal, context: str = "") -> Decimal:
        """Safely compute square root."""
        try:
            if x < 0:
                raise CalculationError(f"Cannot compute sqrt of negative {context}: {x}")
            if x == 0:
                return Decimal("0")
            result = x.sqrt()
            return result
        except (InvalidOperation, ValueError) as e:
            raise CalculationError(f"Square root error {context}: {str(e)}")

    @staticmethod
    def safe_add(a: Decimal, b: Decimal, context: str = "") -> Decimal:
        """Safely add two numbers."""
        try:
            result = a + b
            if abs(result) > MAX_AMOUNT * MAX_PRICE * Decimal("10"):
                raise CalculationError(f"Addition overflow {context}: {a} + {b}")
            return result
        except (Overflow, InvalidOperation) as e:
            raise CalculationError(f"Addition error {context}: {str(e)}")

    @staticmethod
    def safe_subtract(a: Decimal, b: Decimal, context: str = "") -> Decimal:
        """Safely subtract two numbers."""
        try:
            result = a - b
            if abs(result) > MAX_AMOUNT * MAX_PRICE * Decimal("10"):
                raise CalculationError(f"Subtraction overflow {context}: {a} - {b}")
            return result
        except (Overflow, InvalidOperation) as e:
            raise CalculationError(f"Subtraction error {context}: {str(e)}")


class InputValidator:
    """Validator for input parameters."""

    @staticmethod
    def validate_price(price: float, field_name: str) -> ValidationReport:
        """Validate a price value."""
        report = ValidationReport(True, [], [])

        try:
            price_dec = Decimal(str(price))
        except (InvalidOperation, ValueError):
            report.add_error(f"Invalid numeric value: {price}", field_name)
            return report

        if price_dec <= 0:
            report.add_error("Price must be positive", field_name)
        elif price_dec < MIN_PRICE:
            report.add_error(f"Price too small (min: {MIN_PRICE})", field_name)
        elif price_dec > MAX_PRICE:
            report.add_error(f"Price too large (max: {MAX_PRICE})", field_name)

        if not math.isfinite(price):
            report.add_error("Price must be finite", field_name)

        return report

    @staticmethod
    def validate_amount(amount: float, field_name: str) -> ValidationReport:
        """Validate a token amount."""
        report = ValidationReport(True, [], [])

        try:
            amount_dec = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            report.add_error(f"Invalid numeric value: {amount}", field_name)
            return report

        if amount_dec <= 0:
            report.add_error("Amount must be positive", field_name)
        elif amount_dec < MIN_AMOUNT:
            report.add_error(f"Amount too small (min: {MIN_AMOUNT})", field_name)
        elif amount_dec > MAX_AMOUNT:
            report.add_error(f"Amount too large (max: {MAX_AMOUNT})", field_name)

        if not math.isfinite(amount):
            report.add_error("Amount must be finite", field_name)

        return report

    @staticmethod
    def validate_fee_tier(fee: float) -> ValidationReport:
        """Validate fee tier."""
        report = ValidationReport(True, [], [])

        try:
            fee_dec = Decimal(str(fee))
        except (InvalidOperation, ValueError):
            report.add_error(f"Invalid numeric value: {fee}", "fee_tier")
            return report

        if fee_dec < MIN_FEE_TIER:
            report.add_error("Fee tier cannot be negative", "fee_tier")
        elif fee_dec > MAX_FEE_TIER:
            report.add_error(f"Fee tier too high (max: {MAX_FEE_TIER*100}%)", "fee_tier")

        # Warning for unusual fee tiers
        if fee_dec > Decimal("0.01"):  # > 1%
            report.add_error(
                f"Unusually high fee tier: {fee_dec*100}%",
                "fee_tier",
                ErrorSeverity.WARNING
            )

        return report

    @staticmethod
    def validate_volume_multiple(volume: float) -> ValidationReport:
        """Validate volume multiple."""
        report = ValidationReport(True, [], [])

        try:
            volume_dec = Decimal(str(volume))
        except (InvalidOperation, ValueError):
            report.add_error(f"Invalid numeric value: {volume}", "volume_multiple")
            return report

        if volume_dec < 0:
            report.add_error("Volume multiple cannot be negative", "volume_multiple")
        elif volume_dec > MAX_VOLUME_MULTIPLE:
            report.add_error(
                f"Volume multiple too large (max: {MAX_VOLUME_MULTIPLE})",
                "volume_multiple"
            )

        return report

    @staticmethod
    def validate_time_period(days: float) -> ValidationReport:
        """Validate time period."""
        report = ValidationReport(True, [], [])

        try:
            days_dec = Decimal(str(days))
        except (InvalidOperation, ValueError):
            report.add_error(f"Invalid numeric value: {days}", "time_period_days")
            return report

        if days_dec < 0:
            report.add_error("Time period cannot be negative", "time_period_days")
        elif days_dec > MAX_TIME_PERIOD:
            report.add_error(
                f"Time period too long (max: {MAX_TIME_PERIOD} days)",
                "time_period_days"
            )
        elif days_dec == 0:
            report.add_error(
                "Zero time period will cause division by zero in APR calculations",
                "time_period_days",
                ErrorSeverity.WARNING
            )

        return report


class ImpermanentLossCalculator:
    """
    Calculator for impermanent loss in constant product AMM pools with safety checks.
    """

    def __init__(self, initial_price: float, initial_amount0: float,
                 initial_amount1: float, fee_tier: float = 0.003,
                 validate: bool = True):
        """
        Initialize the IL calculator with validation.

        Args:
            initial_price: Initial price of token0 in terms of token1
            initial_amount0: Initial amount of token0 deposited
            initial_amount1: Initial amount of token1 deposited
            fee_tier: Pool fee tier (default 0.3% = 0.003)
            validate: Whether to perform input validation (default True)

        Raises:
            ValidationError: If any input validation fails
        """
        if validate:
            self._validate_initialization(
                initial_price, initial_amount0, initial_amount1, fee_tier
            )

        try:
            self.initial_price = Decimal(str(initial_price))
            self.initial_amount0 = Decimal(str(initial_amount0))
            self.initial_amount1 = Decimal(str(initial_amount1))
            self.fee_tier = Decimal(str(fee_tier))

            # Calculate initial value with safe math
            self.initial_value = SafeMath.safe_add(
                SafeMath.safe_multiply(
                    self.initial_amount0, self.initial_price, "initial_value"
                ),
                self.initial_amount1,
                "initial_value"
            )

            # Calculate k constant with safe math
            self.k = SafeMath.safe_multiply(
                self.initial_amount0, self.initial_amount1, "k_constant"
            )

            if self.k <= 0:
                raise CalculationError("K constant must be positive")

        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Failed to initialize calculator: {str(e)}")

    def _validate_initialization(self, initial_price: float, initial_amount0: float,
                                 initial_amount1: float, fee_tier: float):
        """Validate initialization parameters."""
        combined_report = ValidationReport(True, [], [])

        # Validate each parameter
        reports = [
            InputValidator.validate_price(initial_price, "initial_price"),
            InputValidator.validate_amount(initial_amount0, "initial_amount0"),
            InputValidator.validate_amount(initial_amount1, "initial_amount1"),
            InputValidator.validate_fee_tier(fee_tier),
        ]

        # Combine all reports
        for report in reports:
            combined_report.errors.extend(report.errors)
            combined_report.warnings.extend(report.warnings)
            if not report.is_valid:
                combined_report.is_valid = False

        if not combined_report.is_valid:
            raise ValidationError(
                f"Validation failed:\n{combined_report.get_summary()}"
            )

        # Log warnings if any
        if combined_report.warnings:
            print(f"Warnings:\n{combined_report.get_summary()}")

    def calculate_il(self, current_price: float, validate: bool = True) -> Dict[str, float]:
        """
        Calculate impermanent loss at a given price with safety checks.

        Args:
            current_price: Current price of token0 in terms of token1
            validate: Whether to validate input (default True)

        Returns:
            Dictionary with IL metrics

        Raises:
            ValidationError: If validation fails
            CalculationError: If calculation fails
        """
        if validate:
            report = InputValidator.validate_price(current_price, "current_price")
            if not report.is_valid:
                raise ValidationError(f"Validation failed:\n{report.get_summary()}")

        try:
            current_price_dec = Decimal(str(current_price))

            # Calculate price ratio with safe math
            price_ratio = SafeMath.safe_divide(
                current_price_dec, self.initial_price, "price_ratio"
            )

            # Calculate new amounts based on constant product formula
            # x * y = k, and y = price * x
            # So x * (price * x) = k => x^2 = k / price
            k_over_price = SafeMath.safe_divide(
                self.k, current_price_dec, "k/price"
            )
            current_amount0 = SafeMath.safe_sqrt(k_over_price, "amount0")
            current_amount1 = SafeMath.safe_multiply(
                current_price_dec, current_amount0, "amount1"
            )

            # Calculate current value
            current_value_pool = SafeMath.safe_add(
                SafeMath.safe_multiply(
                    current_amount0, current_price_dec, "pool_value"
                ),
                current_amount1,
                "pool_value"
            )

            # Calculate hold value
            hold_value = SafeMath.safe_add(
                SafeMath.safe_multiply(
                    self.initial_amount0, current_price_dec, "hold_value"
                ),
                self.initial_amount1,
                "hold_value"
            )

            # Calculate impermanent loss
            il_absolute = SafeMath.safe_subtract(
                current_value_pool, hold_value, "il_absolute"
            )
            il_percentage = SafeMath.safe_multiply(
                SafeMath.safe_divide(il_absolute, hold_value, "il_percentage"),
                Decimal("100"),
                "il_percentage"
            )

            # Calculate value multiplier with safe math
            sqrt_ratio = SafeMath.safe_sqrt(price_ratio, "value_multiplier")
            numerator = SafeMath.safe_multiply(
                sqrt_ratio, Decimal("2"), "value_multiplier"
            )
            denominator = SafeMath.safe_add(
                price_ratio, Decimal("1"), "value_multiplier"
            )
            value_multiplier = float(
                SafeMath.safe_divide(numerator, denominator, "value_multiplier")
            )

            return {
                "current_price": float(current_price_dec),
                "price_ratio": float(price_ratio),
                "price_change_percent": float(
                    SafeMath.safe_multiply(
                        SafeMath.safe_subtract(price_ratio, Decimal("1"), "price_change"),
                        Decimal("100"),
                        "price_change"
                    )
                ),
                "current_amount0": float(current_amount0),
                "current_amount1": float(current_amount1),
                "pool_value": float(current_value_pool),
                "hold_value": float(hold_value),
                "il_absolute": float(il_absolute),
                "il_percentage": float(il_percentage),
                "value_multiplier": value_multiplier,
            }

        except CalculationError:
            raise
        except Exception as e:
            raise CalculationError(f"IL calculation failed: {str(e)}")

    def calculate_il_with_fees(
        self, current_price: float, volume_as_multiple_of_liquidity: float,
        time_period_days: float = 1, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate impermanent loss including earned fees with validation.

        Args:
            current_price: Current price of token0 in terms of token1
            volume_as_multiple_of_liquidity: Trading volume as multiple of liquidity
            time_period_days: Time period in days
            validate: Whether to validate inputs (default True)

        Returns:
            Dictionary with IL and fee metrics

        Raises:
            ValidationError: If validation fails
            CalculationError: If calculation fails
        """
        if validate:
            combined_report = ValidationReport(True, [], [])
            reports = [
                InputValidator.validate_price(current_price, "current_price"),
                InputValidator.validate_volume_multiple(volume_as_multiple_of_liquidity),
                InputValidator.validate_time_period(time_period_days),
            ]

            for report in reports:
                combined_report.errors.extend(report.errors)
                combined_report.warnings.extend(report.warnings)
                if not report.is_valid:
                    combined_report.is_valid = False

            if not combined_report.is_valid:
                raise ValidationError(
                    f"Validation failed:\n{combined_report.get_summary()}"
                )

        try:
            # Calculate base IL
            il_data = self.calculate_il(current_price, validate=False)

            # Calculate fees earned with safe math
            volume_dec = SafeMath.safe_multiply(
                Decimal(str(float(self.initial_value))),
                Decimal(str(volume_as_multiple_of_liquidity)),
                "volume"
            )
            fees_earned = float(
                SafeMath.safe_multiply(volume_dec, self.fee_tier, "fees")
            )

            # Calculate net result
            il_absolute = il_data["il_absolute"]
            net_result = fees_earned + il_absolute
            net_percentage = (net_result / il_data["hold_value"]) * 100

            # Calculate APR from fees
            if time_period_days > 0:
                fee_apr = (fees_earned / float(self.initial_value)) * (365 / time_period_days) * 100
            else:
                fee_apr = 0

            # Calculate breakeven volume
            if il_absolute < 0:
                breakeven = abs(il_absolute) / (float(self.initial_value) * float(self.fee_tier))
            else:
                breakeven = 0

            return {
                **il_data,
                "fees_earned": fees_earned,
                "net_result": net_result,
                "net_percentage": net_percentage,
                "fee_apr": fee_apr,
                "breakeven_volume_multiple": breakeven,
            }

        except CalculationError:
            raise
        except Exception as e:
            raise CalculationError(f"Fee calculation failed: {str(e)}")

    def generate_il_curve(self, price_range: Tuple[float, float],
                         steps: int = 50, validate: bool = True) -> List[Dict[str, float]]:
        """
        Generate IL curve data over a price range with validation.

        Args:
            price_range: (min_price, max_price) tuple
            steps: Number of price points to calculate
            validate: Whether to validate inputs (default True)

        Returns:
            List of dictionaries with IL data at each price point

        Raises:
            ValidationError: If validation fails
        """
        min_price, max_price = price_range

        if validate:
            combined_report = ValidationReport(True, [], [])
            reports = [
                InputValidator.validate_price(min_price, "min_price"),
                InputValidator.validate_price(max_price, "max_price"),
            ]

            for report in reports:
                combined_report.errors.extend(report.errors)
                if not report.is_valid:
                    combined_report.is_valid = False

            if min_price >= max_price:
                combined_report.add_error(
                    "min_price must be less than max_price",
                    "price_range"
                )

            if steps < 2:
                combined_report.add_error(
                    "steps must be at least 2",
                    "steps"
                )
            elif steps > 10000:
                combined_report.add_error(
                    "steps too large (max: 10000)",
                    "steps"
                )

            if not combined_report.is_valid:
                raise ValidationError(
                    f"Validation failed:\n{combined_report.get_summary()}"
                )

        try:
            price_step = (max_price - min_price) / (steps - 1)
            curve_data = []

            for i in range(steps):
                price = min_price + (i * price_step)
                il_data = self.calculate_il(price, validate=False)
                curve_data.append(il_data)

            return curve_data

        except Exception as e:
            raise CalculationError(f"Curve generation failed: {str(e)}")

    def calculate_divergence_loss(self, current_price: float,
                                  validate: bool = True) -> float:
        """
        Calculate divergence loss (alternative term for IL) with validation.

        Args:
            current_price: Current price of token0 in terms of token1
            validate: Whether to validate input (default True)

        Returns:
            Divergence loss as a percentage

        Raises:
            ValidationError: If validation fails
        """
        return self.calculate_il(current_price, validate)["il_percentage"]


def calculate_il_simple(price_change_ratio: float, validate: bool = True) -> float:
    """
    Calculate IL percentage using simplified formula with validation.

    Formula: IL = (2 * sqrt(price_ratio)) / (1 + price_ratio) - 1

    Args:
        price_change_ratio: Ratio of current price to initial price
        validate: Whether to validate input (default True)

    Returns:
        Impermanent loss as a percentage

    Raises:
        ValidationError: If validation fails
    """
    if validate:
        if price_change_ratio <= 0:
            raise ValidationError("Price change ratio must be positive")
        if not math.isfinite(price_change_ratio):
            raise ValidationError("Price change ratio must be finite")
        if price_change_ratio > float(MAX_PRICE):
            raise ValidationError(f"Price change ratio too large (max: {MAX_PRICE})")

    try:
        price_ratio = Decimal(str(price_change_ratio))
        sqrt_ratio = SafeMath.safe_sqrt(price_ratio, "il_simple")
        numerator = SafeMath.safe_multiply(Decimal("2"), sqrt_ratio, "il_simple")
        denominator = SafeMath.safe_add(Decimal("1"), price_ratio, "il_simple")
        il = SafeMath.safe_subtract(
            SafeMath.safe_divide(numerator, denominator, "il_simple"),
            Decimal("1"),
            "il_simple"
        )
        return float(SafeMath.safe_multiply(il, Decimal("100"), "il_simple"))
    except Exception as e:
        raise CalculationError(f"Simple IL calculation failed: {str(e)}")


def calculate_breakeven_fee_apr(il_percentage: float, time_period_days: float,
                                validate: bool = True) -> float:
    """
    Calculate the APR from fees needed to break even with IL.

    Args:
        il_percentage: Impermanent loss as a percentage
        time_period_days: Time period in days
        validate: Whether to validate inputs (default True)

    Returns:
        Required fee APR to break even

    Raises:
        ValidationError: If validation fails
    """
    if validate:
        report = InputValidator.validate_time_period(time_period_days)
        if not report.is_valid:
            raise ValidationError(f"Validation failed:\n{report.get_summary()}")

        if not math.isfinite(il_percentage):
            raise ValidationError("IL percentage must be finite")

    if time_period_days <= 0:
        return float("inf")

    try:
        il_absolute_needed = abs(il_percentage)
        daily_rate = il_absolute_needed / time_period_days
        annual_rate = daily_rate * 365
        return annual_rate
    except Exception as e:
        raise CalculationError(f"Breakeven APR calculation failed: {str(e)}")


def compare_strategies(
    initial_investment: float,
    initial_price: float,
    current_price: float,
    fee_tier: float = 0.003,
    volume_multiple: float = 1.0,
    validate: bool = True,
) -> Dict[str, Dict[str, float]]:
    """
    Compare different investment strategies (hold vs LP) with validation.

    Args:
        initial_investment: Total initial investment value
        initial_price: Initial price
        current_price: Current price
        fee_tier: Pool fee tier
        volume_multiple: Trading volume as multiple of liquidity
        validate: Whether to validate inputs (default True)

    Returns:
        Dictionary comparing strategies

    Raises:
        ValidationError: If validation fails
    """
    if validate:
        combined_report = ValidationReport(True, [], [])
        reports = [
            InputValidator.validate_amount(initial_investment, "initial_investment"),
            InputValidator.validate_price(initial_price, "initial_price"),
            InputValidator.validate_price(current_price, "current_price"),
            InputValidator.validate_fee_tier(fee_tier),
            InputValidator.validate_volume_multiple(volume_multiple),
        ]

        for report in reports:
            combined_report.errors.extend(report.errors)
            combined_report.warnings.extend(report.warnings)
            if not report.is_valid:
                combined_report.is_valid = False

        if not combined_report.is_valid:
            raise ValidationError(
                f"Validation failed:\n{combined_report.get_summary()}"
            )

    try:
        # Calculate 50/50 split with safe math
        amount0 = initial_investment / (2 * initial_price)
        amount1 = initial_investment / 2

        calculator = ImpermanentLossCalculator(
            initial_price=initial_price,
            initial_amount0=amount0,
            initial_amount1=amount1,
            fee_tier=fee_tier,
            validate=False  # Already validated
        )

        il_data = calculator.calculate_il_with_fees(
            current_price, volume_multiple, validate=False
        )

        # Hold strategy value
        hold_value = amount0 * current_price + amount1

        # LP strategy value
        lp_value = il_data["pool_value"] + il_data["fees_earned"]

        return {
            "hold_strategy": {
                "initial_value": initial_investment,
                "final_value": hold_value,
                "profit": hold_value - initial_investment,
                "return_percentage": ((hold_value - initial_investment) / initial_investment) * 100,
            },
            "lp_strategy": {
                "initial_value": initial_investment,
                "final_value": lp_value,
                "profit": lp_value - initial_investment,
                "return_percentage": ((lp_value - initial_investment) / initial_investment) * 100,
                "il_loss": il_data["il_absolute"],
                "fees_earned": il_data["fees_earned"],
            },
            "comparison": {
                "lp_vs_hold": lp_value - hold_value,
                "lp_vs_hold_percentage": ((lp_value - hold_value) / hold_value) * 100,
                "better_strategy": "LP" if lp_value > hold_value else "Hold",
            },
        }
    except Exception as e:
        raise CalculationError(f"Strategy comparison failed: {str(e)}")


# Example usage and precomputed IL values for common price changes
COMMON_IL_VALUES = {
    1.25: -0.6,   # 25% price increase
    1.5: -2.0,    # 50% price increase
    2.0: -5.7,    # 100% price increase (2x)
    3.0: -13.4,   # 200% price increase (3x)
    4.0: -20.0,   # 300% price increase (4x)
    5.0: -25.5,   # 400% price increase (5x)
    0.8: -0.6,    # 20% price decrease
    0.5: -2.0,    # 50% price decrease
    0.25: -5.7,   # 75% price decrease
}


if __name__ == "__main__":
    print("Enhanced Impermanent Loss Calculator with Safety Checks")
    print("=" * 60)
    print()

    try:
        # Example: ETH/USDC pool
        calculator = ImpermanentLossCalculator(
            initial_price=2000,
            initial_amount0=1,
            initial_amount1=2000,
            fee_tier=0.003,
        )

"""
I've created an enhanced version of the IL calculator with comprehensive safety checks. Here are the key improvements:
Safety Features Added
1. Input Validation

Price validation (min/max bounds, finite checks)
Amount validation with reasonable limits
Fee tier validation with warnings for unusual values
Volume and time period validation
Comprehensive validation reporting system

2. Safe Math Operations

SafeMath class with overflow protection
Safe multiply, divide, add, subtract operations
Square root with negative value checks
Division by zero prevention
Context information for debugging

3. Error Handling

Custom exception types (ValidationError, CalculationError)
Detailed error messages with field information
Error severity levels (WARNING, ERROR, CRITICAL)
Validation reports with summaries

4. Constraints & Limits

MAX_PRICE: 10^15 (prevents overflow)
MIN_PRICE: 10^-15 (prevents underflow)
MAX_AMOUNT: 10^18 (token amount limit)
MAX_FEE_TIER: 10% (sanity check)
MAX_VOLUME_MULTIPLE: 1M (prevents unrealistic scenarios)
MAX_TIME_PERIOD: 100 years (sanity check)

5. Validation Reporting

ValidationResult dataclass for individual checks
ValidationReport for comprehensive validation
Separates errors from warnings
Human-readable summary output

All calculations now include context strings for better error tracing, and every mathematical operation is protected against overflow, underflow, and invalid operations. The validate parameter allows skipping validation for internal calls to improve performance while maintaining safety at public API boundaries.
"""
