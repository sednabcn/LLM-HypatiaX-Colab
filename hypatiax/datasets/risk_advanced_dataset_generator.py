import numpy as np
from scipy import stats
from src.hybrid_system import HybridDiscoverySystem
import os

def generate_advanced_risk(n_samples=150, noise_level=0.001):
    """
    Generate advanced risk management formulas with realistic parameters.
    
    Args:
        n_samples: Number of samples per formula
        noise_level: Noise level for realistic data
    """
    system = HybridDiscoverySystem(domain='risk')
    
    print("="*60)
    print("Generating Advanced Risk Management Dataset")
    print("="*60)
    
    # Formula 1: VaR with Cornish-Fisher Adjustment (Non-Normal Returns)
    print("\n[1/10] VaR with Cornish-Fisher Adjustment...")
    mu = np.random.uniform(-0.1, 0.1, n_samples)
    sigma = np.random.uniform(0.1, 0.5, n_samples)
    skewness = np.random.uniform(-1.5, 1.5, n_samples)
    kurtosis = np.random.uniform(0, 3, n_samples)  # Excess kurtosis
    
    X = np.column_stack([mu, sigma, skewness, kurtosis])
    
    # Cornish-Fisher expansion for 95% VaR
    z = 1.645  # 95% percentile
    z_cf = z + (z**2 - 1) * skewness / 6 + \
           (z**3 - 3*z) * kurtosis / 24 - \
           (2*z**3 - 5*z) * skewness**2 / 36
    var_cf = mu - z_cf * sigma
    var_cf += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=var_cf,
        variable_names=['mu', 'sigma', 'skewness', 'kurtosis'],
        variable_descriptions={
            'mu': 'Expected return',
            'sigma': 'Volatility',
            'skewness': 'Distribution skewness',
            'kurtosis': 'Excess kurtosis'
        },
        variable_units={'mu': 'percent', 'sigma': 'percent', 
                       'skewness': 'dimensionless', 'kurtosis': 'dimensionless'},
        description="VaR at 95% with Cornish-Fisher adjustment for non-normal returns"
    )
    
    # Formula 2: Expected Shortfall (CVaR) - Parametric
    print("[2/10] Expected Shortfall (CVaR)...")
    mu_es = np.random.uniform(-0.1, 0.1, n_samples)
    sigma_es = np.random.uniform(0.1, 0.5, n_samples)
    alpha = 0.95  # 95% confidence level
    
    X = np.column_stack([mu_es, sigma_es])
    
    # CVaR formula for normal distribution
    z_alpha = stats.norm.ppf(alpha)
    pdf_z = stats.norm.pdf(z_alpha)
    es = mu_es - sigma_es * pdf_z / (1 - alpha)
    es += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=es,
        variable_names=['mu', 'sigma'],
        variable_descriptions={
            'mu': 'Expected return',
            'sigma': 'Volatility'
        },
        variable_units={'mu': 'percent', 'sigma': 'percent'},
        description="Expected Shortfall (CVaR) at 95% confidence"
    )
    
    # Formula 3: Modified VaR for t-Distribution
    print("[3/10] Modified VaR for Heavy-Tailed Returns...")
    mu_t = np.random.uniform(-0.1, 0.1, n_samples)
    sigma_t = np.random.uniform(0.1, 0.5, n_samples)
    df = np.random.uniform(3, 10, n_samples)  # Degrees of freedom
    
    X = np.column_stack([mu_t, sigma_t, df])
    
    # VaR using t-distribution
    t_quantile = np.array([stats.t.ppf(0.05, d) for d in df])
    var_t = mu_t + t_quantile * sigma_t * np.sqrt((df - 2) / df)
    var_t += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=var_t,
        variable_names=['mu', 'sigma', 'df'],
        variable_descriptions={
            'mu': 'Expected return',
            'sigma': 'Volatility',
            'df': 'Degrees of freedom (t-distribution)'
        },
        variable_units={'mu': 'percent', 'sigma': 'percent', 'df': 'dimensionless'},
        description="Modified VaR using Student's t-distribution (heavy tails)"
    )
    
    # Formula 4: Portfolio VaR (Two Assets)
    print("[4/10] Two-Asset Portfolio VaR...")
    w1 = np.random.uniform(0, 1, n_samples)
    w2 = 1 - w1  # Weights sum to 1
    sigma1 = np.random.uniform(0.1, 0.4, n_samples)
    sigma2 = np.random.uniform(0.1, 0.4, n_samples)
    rho = np.random.uniform(-0.5, 0.9, n_samples)  # Correlation
    
    X = np.column_stack([w1, w2, sigma1, sigma2, rho])
    
    # Portfolio standard deviation
    portfolio_vol = np.sqrt(
        w1**2 * sigma1**2 + 
        w2**2 * sigma2**2 + 
        2 * w1 * w2 * sigma1 * sigma2 * rho
    )
    # 95% VaR (assuming zero mean for simplicity)
    portfolio_var = -1.645 * portfolio_vol
    portfolio_var += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=portfolio_var,
        variable_names=['w1', 'w2', 'sigma1', 'sigma2', 'rho'],
        variable_descriptions={
            'w1': 'Weight of asset 1',
            'w2': 'Weight of asset 2',
            'sigma1': 'Volatility of asset 1',
            'sigma2': 'Volatility of asset 2',
            'rho': 'Correlation between assets'
        },
        variable_units={'w1': 'percent', 'w2': 'percent', 'sigma1': 'percent', 
                       'sigma2': 'percent', 'rho': 'dimensionless'},
        description="Two-asset portfolio VaR with correlation"
    )
    
    # Formula 5: Diversification Benefit
    print("[5/10] Portfolio Diversification Benefit...")
    sigma_1 = np.random.uniform(0.15, 0.4, n_samples)
    sigma_2 = np.random.uniform(0.15, 0.4, n_samples)
    weight_1 = np.random.uniform(0.3, 0.7, n_samples)
    weight_2 = 1 - weight_1
    correlation = np.random.uniform(-0.3, 0.9, n_samples)
    
    X = np.column_stack([sigma_1, sigma_2, weight_1, weight_2, correlation])
    
    # Diversification benefit = sum of individual VaRs - portfolio VaR
    individual_var_sum = weight_1 * sigma_1 + weight_2 * sigma_2
    portfolio_vol_div = np.sqrt(
        weight_1**2 * sigma_1**2 + 
        weight_2**2 * sigma_2**2 + 
        2 * weight_1 * weight_2 * sigma_1 * sigma_2 * correlation
    )
    div_benefit = individual_var_sum - portfolio_vol_div
    div_benefit += np.random.normal(0, noise_level * 0.1, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=div_benefit,
        variable_names=['sigma1', 'sigma2', 'w1', 'w2', 'correlation'],
        variable_descriptions={
            'sigma1': 'Volatility of asset 1',
            'sigma2': 'Volatility of asset 2',
            'w1': 'Weight of asset 1',
            'w2': 'Weight of asset 2',
            'correlation': 'Correlation coefficient'
        },
        variable_units={'sigma1': 'percent', 'sigma2': 'percent', 
                       'w1': 'percent', 'w2': 'percent', 'correlation': 'dimensionless'},
        description="Portfolio diversification benefit (risk reduction)"
    )
    
    # Formula 6: Marginal VaR (Risk Contribution)
    print("[6/10] Marginal VaR (Risk Contribution)...")
    portfolio_var_val = np.random.uniform(10000, 100000, n_samples)
    asset_weight = np.random.uniform(0.1, 0.5, n_samples)
    asset_beta = np.random.uniform(0.5, 2.0, n_samples)  # Asset's portfolio beta
    
    X = np.column_stack([portfolio_var_val, asset_weight, asset_beta])
    
    # Marginal VaR = Portfolio VaR * beta
    marginal_var = portfolio_var_val * asset_beta
    marginal_var += np.random.normal(0, noise_level * 1000, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=marginal_var,
        variable_names=['portfolio_var', 'weight', 'beta'],
        variable_descriptions={
            'portfolio_var': 'Portfolio VaR',
            'weight': 'Asset weight in portfolio',
            'beta': 'Asset beta to portfolio'
        },
        variable_units={'portfolio_var': 'USD', 'weight': 'percent', 'beta': 'dimensionless'},
        description="Marginal VaR - risk contribution of individual asset"
    )
    
    # Formula 7: Component VaR (Total Risk Contribution)
    print("[7/10] Component VaR...")
    portfolio_var_comp = np.random.uniform(10000, 100000, n_samples)
    weight = np.random.uniform(0.1, 0.5, n_samples)
    beta_comp = np.random.uniform(0.5, 2.0, n_samples)
    
    X = np.column_stack([portfolio_var_comp, weight, beta_comp])
    
    # Component VaR = weight * marginal VaR = weight * portfolio_var * beta
    component_var = weight * portfolio_var_comp * beta_comp
    component_var += np.random.normal(0, noise_level * 1000, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=component_var,
        variable_names=['portfolio_var', 'weight', 'beta'],
        variable_descriptions={
            'portfolio_var': 'Portfolio VaR',
            'weight': 'Asset weight',
            'beta': 'Asset beta to portfolio'
        },
        variable_units={'portfolio_var': 'USD', 'weight': 'percent', 'beta': 'dimensionless'},
        description="Component VaR - total contribution to portfolio risk"
    )
    
    # Formula 8: Tail Risk Ratio
    print("[8/10] Tail Risk Ratio...")
    cvar_val = np.random.uniform(5, 20, n_samples)  # CVaR percentage
    var_val = np.random.uniform(3, 15, n_samples)   # VaR percentage
    # Ensure CVaR > VaR (it should be)
    cvar_val = np.maximum(cvar_val, var_val * 1.1)
    
    X = np.column_stack([cvar_val, var_val])
    
    # Tail risk ratio = CVaR / VaR (measures tail heaviness)
    tail_ratio = cvar_val / var_val
    tail_ratio += np.random.normal(0, noise_level * 0.1, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=tail_ratio,
        variable_names=['cvar', 'var'],
        variable_descriptions={
            'cvar': 'Expected Shortfall (CVaR)',
            'var': 'Value at Risk (VaR)'
        },
        variable_units={'cvar': 'percent', 'var': 'percent'},
        description="Tail Risk Ratio - measures severity of tail events"
    )
    
    # Formula 9: Risk-Adjusted Return on Capital (RAROC)
    print("[9/10] Risk-Adjusted Return on Capital...")
    expected_return = np.random.uniform(0.05, 0.25, n_samples)
    expected_loss = np.random.uniform(0.01, 0.05, n_samples)
    economic_capital = np.random.uniform(10000, 100000, n_samples)
    
    X = np.column_stack([expected_return, expected_loss, economic_capital])
    
    # RAROC = (Expected Return - Expected Loss) / Economic Capital
    raroc = (expected_return - expected_loss)
    raroc += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=raroc,
        variable_names=['return', 'loss', 'capital'],
        variable_descriptions={
            'return': 'Expected return',
            'loss': 'Expected loss',
            'capital': 'Economic capital (risk measure)'
        },
        variable_units={'return': 'percent', 'loss': 'percent', 'capital': 'USD'},
        description="Risk-Adjusted Return on Capital (RAROC)"
    )
    
    # Formula 10: Maximum Drawdown Duration
    print("[10/10] Expected Maximum Drawdown...")
    volatility_dd = np.random.uniform(0.1, 0.5, n_samples)
    sharpe_ratio = np.random.uniform(0.5, 2.0, n_samples)
    time_horizon = np.random.uniform(1, 10, n_samples)  # Years
    
    X = np.column_stack([volatility_dd, sharpe_ratio, time_horizon])
    
    # Expected max drawdown approximation
    # Based on Brownian motion: E[MDD] ≈ 0.63 * vol * sqrt(T) / Sharpe
    expected_mdd = 0.63 * volatility_dd * np.sqrt(time_horizon) / (sharpe_ratio + 0.1)
    expected_mdd += np.random.normal(0, noise_level * 0.1, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=expected_mdd,
        variable_names=['volatility', 'sharpe', 'horizon'],
        variable_descriptions={
            'volatility': 'Return volatility',
            'sharpe': 'Sharpe ratio',
            'horizon': 'Time horizon'
        },
        variable_units={'volatility': 'percent', 'sharpe': 'dimensionless', 'horizon': 'years'},
        description="Expected maximum drawdown over time horizon"
    )
    
    # Save results
    os.makedirs('data', exist_ok=True)
    system.save_results('data/risk_advanced.json')
    
    # Summary
    valid = sum(1 for r in system.results if r['validation']['valid'])
    print("\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Samples per formula: {n_samples}")
    print(f"  Noise level: {noise_level}")
    print(f"  Output: data/risk_advanced.json")
    print("="*60)
    
    return system

def generate_stress_testing(n_samples=120, noise_level=0.01):
    """
    Generate stress testing formulas for various market scenarios.
    
    Args:
        n_samples: Number of samples per formula
        noise_level: Noise level for realistic data
    """
    system = HybridDiscoverySystem(domain='risk')
    
    print("\n" + "="*60)
    print("Generating Stress Testing Scenarios")
    print("="*60)
    
    # Formula 1: Market Crash Scenario
    print("\n[1/5] Market Crash Stress Test...")
    base_portfolio_value = np.random.uniform(100000, 10000000, n_samples)
    market_beta = np.random.uniform(0.5, 2.0, n_samples)
    market_crash_pct = np.random.uniform(-0.3, -0.10, n_samples)  # -30% to -10%
    diversification = np.random.uniform(0.5, 0.95, n_samples)  # 0.5 = poorly diversified
    
    X = np.column_stack([base_portfolio_value, market_beta, market_crash_pct, diversification])
    
    # Stressed loss = portfolio × beta × crash × (1 - diversification benefit)
    stressed_loss = base_portfolio_value * market_beta * abs(market_crash_pct) * (2 - diversification)
    stressed_loss += np.random.normal(0, noise_level * base_portfolio_value.mean() * 0.01, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=stressed_loss,
        variable_names=['portfolio_value', 'beta', 'crash_pct', 'diversification'],
        variable_descriptions={
            'portfolio_value': 'Base portfolio value',
            'beta': 'Market beta',
            'crash_pct': 'Market crash percentage',
            'diversification': 'Diversification score (0-1)'
        },
        variable_units={'portfolio_value': 'USD', 'beta': 'dimensionless', 
                       'crash_pct': 'percent', 'diversification': 'dimensionless'},
        description="Market crash stress test - portfolio loss under severe market decline"
    )
    
    # Formula 2: Interest Rate Shock
    print("[2/5] Interest Rate Shock Stress Test...")
    bond_portfolio = np.random.uniform(50000, 5000000, n_samples)
    duration = np.random.uniform(2, 15, n_samples)  # Modified duration
    rate_shock = np.random.uniform(0.01, 0.05, n_samples)  # 100-500 bps increase
    convexity = np.random.uniform(20, 200, n_samples)
    
    X = np.column_stack([bond_portfolio, duration, rate_shock, convexity])
    
    # Bond price change = -Duration × ΔR + 0.5 × Convexity × (ΔR)²
    price_change_pct = -duration * rate_shock + 0.5 * convexity * rate_shock**2
    portfolio_loss = bond_portfolio * abs(price_change_pct)
    portfolio_loss += np.random.normal(0, noise_level * bond_portfolio.mean() * 0.01, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=portfolio_loss,
        variable_names=['portfolio', 'duration', 'rate_shock', 'convexity'],
        variable_descriptions={
            'portfolio': 'Bond portfolio value',
            'duration': 'Modified duration',
            'rate_shock': 'Interest rate increase',
            'convexity': 'Portfolio convexity'
        },
        variable_units={'portfolio': 'USD', 'duration': 'years', 
                       'rate_shock': 'percent', 'convexity': 'dimensionless'},
        description="Interest rate shock - bond portfolio loss from rate increases"
    )
    
    # Formula 3: Volatility Spike
    print("[3/5] Volatility Spike Stress Test...")
    option_portfolio = np.random.uniform(10000, 1000000, n_samples)
    vega = np.random.uniform(100, 10000, n_samples)  # Vega exposure
    vol_increase = np.random.uniform(0.05, 0.30, n_samples)  # Vol spike 5-30%
    gamma = np.random.uniform(-1000, 1000, n_samples)  # Gamma exposure
    
    X = np.column_stack([option_portfolio, vega, vol_increase, gamma])
    
    # P&L = Vega × ΔVol - |Gamma| × (ΔVol)² (gamma loss from hedging)
    pnl = vega * vol_increase - abs(gamma) * vol_increase**2 * 100
    pnl += np.random.normal(0, noise_level * 1000, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=pnl,
        variable_names=['portfolio', 'vega', 'vol_increase', 'gamma'],
        variable_descriptions={
            'portfolio': 'Option portfolio value',
            'vega': 'Vega exposure (P&L per 1% vol)',
            'vol_increase': 'Volatility increase',
            'gamma': 'Gamma exposure'
        },
        variable_units={'portfolio': 'USD', 'vega': 'USD/percent', 
                       'vol_increase': 'percent', 'gamma': 'dimensionless'},
        description="Volatility spike - option portfolio P&L from vol increase"
    )
    
    # Formula 4: Liquidity Crisis
    print("[4/5] Liquidity Crisis Stress Test...")
    portfolio_size = np.random.uniform(100000, 5000000, n_samples)
    daily_volume = np.random.uniform(1000000, 50000000, n_samples)
    liquidity_ratio = portfolio_size / daily_volume  # Days to liquidate
    bid_ask_spread = np.random.uniform(0.001, 0.05, n_samples)  # 0.1% to 5%
    
    X = np.column_stack([portfolio_size, daily_volume, bid_ask_spread])
    
    # Liquidation cost = portfolio × spread × sqrt(liquidity_ratio) (market impact)
    liquidation_cost = portfolio_size * bid_ask_spread * np.sqrt(liquidity_ratio * 10)
    liquidation_cost = np.clip(liquidation_cost, 0, portfolio_size * 0.5)  # Max 50% cost
    liquidation_cost += np.random.normal(0, noise_level * portfolio_size.mean() * 0.001, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=liquidation_cost,
        variable_names=['portfolio_size', 'daily_volume', 'spread'],
        variable_descriptions={
            'portfolio_size': 'Portfolio size to liquidate',
            'daily_volume': 'Market daily volume',
            'spread': 'Bid-ask spread'
        },
        variable_units={'portfolio_size': 'USD', 'daily_volume': 'USD', 'spread': 'percent'},
        description="Liquidity crisis - cost to liquidate portfolio in stressed market"
    )
    
    # Formula 5: Correlation Breakdown
    print("[5/5] Correlation Breakdown Stress Test...")
    asset1_exposure = np.random.uniform(100000, 2000000, n_samples)
    asset2_exposure = np.random.uniform(100000, 2000000, n_samples)
    normal_correlation = np.random.uniform(0.3, 0.7, n_samples)
    stress_correlation = np.random.uniform(0.85, 0.99, n_samples)  # Crisis correlation
    volatility_mult = np.random.uniform(1.5, 3.0, n_samples)
    
    X = np.column_stack([asset1_exposure, asset2_exposure, normal_correlation, 
                        stress_correlation, volatility_mult])
    
    # Diversification loss when correlation goes to 1
    normal_vol = np.sqrt(asset1_exposure + asset2_exposure + 
                        2 * np.sqrt(asset1_exposure * asset2_exposure) * normal_correlation)
    stress_vol = np.sqrt(asset1_exposure + asset2_exposure + 
                        2 * np.sqrt(asset1_exposure * asset2_exposure) * stress_correlation)
    correlation_impact = (stress_vol - normal_vol) * volatility_mult
    correlation_impact += np.random.normal(0, noise_level * 1000, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=correlation_impact,
        variable_names=['asset1', 'asset2', 'normal_corr', 'stress_corr', 'vol_mult'],
        variable_descriptions={
            'asset1': 'Asset 1 exposure',
            'asset2': 'Asset 2 exposure',
            'normal_corr': 'Normal correlation',
            'stress_corr': 'Stressed correlation',
            'vol_mult': 'Volatility multiplier in crisis'
        },
        variable_units={'asset1': 'USD', 'asset2': 'USD', 'normal_corr': 'dimensionless',
                       'stress_corr': 'dimensionless', 'vol_mult': 'dimensionless'},
        description="Correlation breakdown - additional risk when correlations go to 1"
    )
    
    # Save results
    os.makedirs('data', exist_ok=True)
    system.save_results('data/risk_stress.json')
    
    valid = sum(1 for r in system.results if r['validation']['valid'])
    print("\n" + "="*60)
    print(f"STRESS TESTING SUMMARY:")
    print(f"  Total scenarios: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Output: data/risk_stress.json")
    print("="*60)
    
    return system


def generate_margin_formulas(n_samples=120, noise_level=100):
    """
    Generate margin and leverage requirement formulas.
    
    Args:
        n_samples: Number of samples per formula
        noise_level: Noise level for realistic data
    """
    system = HybridDiscoverySystem(domain='risk')
    
    print("\n" + "="*60)
    print("Generating Margin & Leverage Formulas")
    print("="*60)
    
    # Formula 1: Initial Margin Requirement
    print("\n[1/5] Initial Margin Requirement...")
    position_size = np.random.uniform(10000, 1000000, n_samples)
    leverage = np.random.uniform(2, 20, n_samples)
    volatility = np.random.uniform(0.1, 2.0, n_samples)
    liquidity_factor = np.random.uniform(1.0, 1.5, n_samples)  # 1.0 = highly liquid
    
    X = np.column_stack([position_size, leverage, volatility, liquidity_factor])
    
    # Initial margin = position / leverage × (1 + vol_adjustment) × liquidity_factor
    base_margin = position_size / leverage
    vol_adjustment = 0.5 * volatility  # Higher vol = higher margin
    initial_margin = base_margin * (1 + vol_adjustment) * liquidity_factor
    initial_margin += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=initial_margin,
        variable_names=['position', 'leverage', 'volatility', 'liquidity'],
        variable_descriptions={
            'position': 'Position notional value',
            'leverage': 'Leverage ratio',
            'volatility': 'Asset volatility',
            'liquidity': 'Liquidity adjustment factor'
        },
        variable_units={'position': 'USD', 'leverage': 'x', 
                       'volatility': 'percent', 'liquidity': 'dimensionless'},
        description="Initial margin requirement with volatility and liquidity adjustments"
    )
    
    # Formula 2: Maintenance Margin
    print("[2/5] Maintenance Margin Requirement...")
    position_value = np.random.uniform(10000, 1000000, n_samples)
    leverage_maint = np.random.uniform(2, 20, n_samples)
    margin_ratio = np.random.uniform(0.25, 0.50, n_samples)  # 25-50% of initial
    
    X = np.column_stack([position_value, leverage_maint, margin_ratio])
    
    # Maintenance margin = initial margin × maintenance ratio
    initial_req = position_value / leverage_maint
    maintenance_margin = initial_req * margin_ratio
    maintenance_margin += np.random.normal(0, noise_level * 0.5, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=maintenance_margin,
        variable_names=['position', 'leverage', 'maint_ratio'],
        variable_descriptions={
            'position': 'Position value',
            'leverage': 'Leverage ratio',
            'maint_ratio': 'Maintenance margin ratio'
        },
        variable_units={'position': 'USD', 'leverage': 'x', 'maint_ratio': 'percent'},
        description="Maintenance margin - minimum equity to avoid margin call"
    )
    
    # Formula 3: Margin Call Level
    print("[3/5] Margin Call Level...")
    entry_price = np.random.uniform(100, 10000, n_samples)
    leverage_mc = np.random.uniform(2, 20, n_samples)
    maint_margin_pct = np.random.uniform(0.03, 0.10, n_samples)  # 3-10%
    position_direction = np.random.choice([-1, 1], n_samples)  # -1 short, 1 long
    
    X = np.column_stack([entry_price, leverage_mc, maint_margin_pct])
    
    # Long: margin_call_price = entry × (1 - 1/leverage + maint_margin)
    # Short: margin_call_price = entry × (1 + 1/leverage - maint_margin)
    margin_call_price = np.where(
        position_direction == 1,
        entry_price * (1 - 1/leverage_mc + maint_margin_pct),
        entry_price * (1 + 1/leverage_mc - maint_margin_pct)
    )
    margin_call_price += np.random.normal(0, noise_level * 0.01, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=margin_call_price,
        variable_names=['entry_price', 'leverage', 'maint_margin'],
        variable_descriptions={
            'entry_price': 'Entry price',
            'leverage': 'Leverage ratio',
            'maint_margin': 'Maintenance margin %'
        },
        variable_units={'entry_price': 'USD', 'leverage': 'x', 'maint_margin': 'percent'},
        description="Margin call price - level that triggers margin call"
    )
    
    # Formula 4: Maximum Leverage Given Risk Tolerance
    print("[4/5] Maximum Safe Leverage...")
    account_equity = np.random.uniform(10000, 500000, n_samples)
    risk_tolerance = np.random.uniform(0.01, 0.05, n_samples)  # 1-5% account risk
    stop_loss_distance = np.random.uniform(0.02, 0.10, n_samples)  # 2-10% stop
    
    X = np.column_stack([account_equity, risk_tolerance, stop_loss_distance])
    
    # Max leverage = risk_tolerance / stop_loss_distance
    max_leverage = risk_tolerance / stop_loss_distance
    max_leverage = np.clip(max_leverage, 1, 50)  # Reasonable bounds
    max_leverage += np.random.normal(0, noise_level * 0.01, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=max_leverage,
        variable_names=['equity', 'risk_tolerance', 'stop_distance'],
        variable_descriptions={
            'equity': 'Account equity',
            'risk_tolerance': 'Maximum risk per trade (% of equity)',
            'stop_distance': 'Stop loss distance (%)'
        },
        variable_units={'equity': 'USD', 'risk_tolerance': 'percent', 'stop_distance': 'percent'},
        description="Maximum safe leverage based on risk management"
    )
    
    # Formula 5: Position Size with Kelly Criterion
    print("[5/5] Optimal Position Size (Kelly)...")
    win_rate = np.random.uniform(0.4, 0.7, n_samples)
    avg_win = np.random.uniform(0.02, 0.10, n_samples)
    avg_loss = np.random.uniform(0.01, 0.05, n_samples)
    available_capital = np.random.uniform(10000, 500000, n_samples)
    
    X = np.column_stack([win_rate, avg_win, avg_loss, available_capital])
    
    # Kelly % = W - (1-W)/(R) where W=win_rate, R=avg_win/avg_loss
    win_loss_ratio = avg_win / avg_loss
    kelly_pct = win_rate - (1 - win_rate) / win_loss_ratio
    kelly_pct = np.clip(kelly_pct, 0, 0.25)  # Cap at 25% (fractional Kelly)
    position_size = available_capital * kelly_pct
    position_size += np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X, y=position_size,
        variable_names=['win_rate', 'avg_win', 'avg_loss', 'capital'],
        variable_descriptions={
            'win_rate': 'Historical win rate',
            'avg_win': 'Average win size',
            'avg_loss': 'Average loss size',
            'capital': 'Available capital'
        },
        variable_units={'win_rate': 'percent', 'avg_win': 'percent', 
                       'avg_loss': 'percent', 'capital': 'USD'},
        description="Optimal position size using Kelly Criterion"
    )
    
    # Save results
    os.makedirs('data', exist_ok=True)
    system.save_results('data/risk_margin.json')
    
    valid = sum(1 for r in system.results if r['validation']['valid'])
    print("\n" + "="*60)
    print(f"MARGIN & LEVERAGE SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Output: data/risk_margin.json")
    print("="*60)
    
    return system


if __name__ == "__main__":
    # Generate all three datasets
    print("\n" + "="*70)
    print(" "*20 + "ADVANCED RISK DATASET GENERATION")
    print("="*70)
    
    # Phase 1: Advanced Risk Metrics
    print("\n" + "PHASE 1: Advanced Risk Metrics".center(70))
    print("-"*70)
    system1 = generate_advanced_risk(n_samples=150, noise_level=0.001)
    
    # Phase 2: Stress Testing
    print("\n" + "PHASE 2: Stress Testing Scenarios".center(70))
    print("-"*70)
    system2 = generate_stress_testing(n_samples=120, noise_level=0.01)
    
    # Phase 3: Margin & Leverage
    print("\n" + "PHASE 3: Margin & Leverage Formulas".center(70))
    print("-"*70)
    system3 = generate_margin_formulas(n_samples=120, noise_level=100)
    
    # Final Summary
    print("\n" + "="*70)
    print(" "*20 + "GENERATION COMPLETE")
    print("="*70)
    print(f"\nGenerated Files:")
    print(f"  1. data/risk_advanced.json  - 10 advanced risk metrics")
    print(f"  2. data/risk_stress.json    - 5 stress test scenarios")
    print(f"  3. data/risk_margin.json    - 5 margin/leverage formulas")
    print(f"\nTotal: 20 formulas across 3 risk domains")
    print("\nTo validate:")
    print("  python datasets/validation/validate_dataset.py --pattern 'risk_*.json'")
    print("="*70)
