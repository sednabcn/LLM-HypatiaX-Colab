import numpy as np
from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
import os
from scipy import stats

def generate_risk_formulas(n_samples=200, noise_level=0.01):
    """
    Generate comprehensive risk management dataset with 20 formulas.
    
    Args:
        n_samples: Number of samples per formula
        noise_level: Standard deviation of added noise
    """
    system = HybridDiscoverySystem(domain='risk')
    
    # Formula 1: VaR 95%
    print("Generating VaR 95% dataset...")
    mu = np.random.uniform(-0.1, 0.15, n_samples)
    sigma = np.random.uniform(0.05, 0.5, n_samples)
    t = np.random.uniform(1, 252, n_samples)
    X_var = np.column_stack([mu, sigma, t])
    var_95 = mu - 1.96 * sigma * np.sqrt(t) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_var, y=var_95,
        variable_names=['mu', 'sigma', 't'],
        variable_descriptions={'mu': 'Expected return', 'sigma': 'Volatility', 't': 'Time horizon'},
        variable_units={'mu': 'percent', 'sigma': 'percent', 't': 'dimensionless'},
        description="Value at Risk at 95% confidence level"
    )
    
    # Formula 2: Sharpe Ratio
    print("Generating Sharpe Ratio dataset...")
    returns = np.random.uniform(-0.1, 0.3, n_samples)
    risk_free = np.random.uniform(0.01, 0.05, n_samples)
    vol = np.random.uniform(0.05, 0.3, n_samples)
    X_sharpe = np.column_stack([returns, risk_free, vol])
    sharpe = (returns - risk_free) / vol + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_sharpe, y=sharpe,
        variable_names=['returns', 'risk_free', 'volatility'],
        variable_descriptions={'returns': 'Portfolio returns', 'risk_free': 'Risk-free rate', 'volatility': 'Return volatility'},
        variable_units={'returns': 'percent', 'risk_free': 'percent', 'volatility': 'percent'},
        description="Sharpe ratio - risk-adjusted return measure"
    )
    
    # Formula 3: CVaR 95%
    print("Generating CVaR 95% dataset...")
    mu_cvar = np.random.uniform(-0.1, 0.15, n_samples)
    sigma_cvar = np.random.uniform(0.05, 0.5, n_samples)
    t_cvar = np.random.uniform(1, 252, n_samples)
    X_cvar = np.column_stack([mu_cvar, sigma_cvar, t_cvar])
    phi_inv = stats.norm.pdf(1.96) / (1 - 0.95)
    cvar_95 = mu_cvar - phi_inv * sigma_cvar * np.sqrt(t_cvar) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_cvar, y=cvar_95,
        variable_names=['mu', 'sigma', 't'],
        variable_descriptions={'mu': 'Expected return', 'sigma': 'Volatility', 't': 'Time horizon'},
        variable_units={'mu': 'percent', 'sigma': 'percent', 't': 'dimensionless'},
        description="Conditional VaR (Expected Shortfall) at 95%"
    )
    
    # Formula 4: Beta
    print("Generating Beta dataset...")
    cov_im = np.random.uniform(-0.1, 0.3, n_samples)
    var_m = np.random.uniform(0.01, 0.2, n_samples)
    X_beta = np.column_stack([cov_im, var_m])
    risk_beta = cov_im / var_m + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_beta, y=risk_beta,
        variable_names=['cov_im', 'var_m'],
        variable_descriptions={'cov_im': 'Covariance between asset and market', 'var_m': 'Market variance'},
        variable_units={'cov_im': 'percent^2', 'var_m': 'percent^2'},
        description="Beta - measure of systematic risk"
    )
    
    # Formula 5: Sortino Ratio
    print("Generating Sortino Ratio dataset...")
    returns_sort = np.random.uniform(-0.1, 0.3, n_samples)
    target_return = np.random.uniform(0, 0.05, n_samples)
    downside_dev = np.random.uniform(0.05, 0.25, n_samples)
    X_sortino = np.column_stack([returns_sort, target_return, downside_dev])
    sortino = (returns_sort - target_return) / downside_dev + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_sortino, y=sortino,
        variable_names=['returns', 'target', 'downside_dev'],
        variable_descriptions={'returns': 'Portfolio returns', 'target': 'Target return', 'downside_dev': 'Downside deviation'},
        variable_units={'returns': 'percent', 'target': 'percent', 'downside_dev': 'percent'},
        description="Sortino ratio - downside risk-adjusted return"
    )
    
    # Formula 6: Information Ratio
    print("Generating Information Ratio dataset...")
    active_return = np.random.uniform(-0.05, 0.15, n_samples)
    tracking_error = np.random.uniform(0.02, 0.15, n_samples)
    X_ir = np.column_stack([active_return, tracking_error])
    info_ratio = active_return / tracking_error + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_ir, y=info_ratio,
        variable_names=['active_return', 'tracking_error'],
        variable_descriptions={'active_return': 'Portfolio return minus benchmark', 'tracking_error': 'Std dev of active returns'},
        variable_units={'active_return': 'percent', 'tracking_error': 'percent'},
        description="Information ratio - active management skill"
    )
    
    # Formula 7: Maximum Drawdown
    print("Generating Maximum Drawdown dataset...")
    peak_value = np.random.uniform(100, 1000, n_samples)
    trough_value = peak_value * np.random.uniform(0.5, 0.95, n_samples)
    X_mdd = np.column_stack([peak_value, trough_value])
    max_dd = (trough_value - peak_value) / peak_value + np.random.normal(0, noise_level/10, n_samples)
    
    system.discover_validate_interpret(
        X=X_mdd, y=max_dd,
        variable_names=['peak', 'trough'],
        variable_descriptions={'peak': 'Peak portfolio value', 'trough': 'Trough portfolio value'},
        variable_units={'peak': 'currency', 'trough': 'currency'},
        description="Maximum Drawdown - largest peak-to-trough decline"
    )
    
    # Formula 8: Treynor Ratio
    print("Generating Treynor Ratio dataset...")
    returns_trey = np.random.uniform(-0.1, 0.3, n_samples)
    risk_free_trey = np.random.uniform(0.01, 0.05, n_samples)
    beta_trey = np.random.uniform(0.5, 2.0, n_samples)
    X_treynor = np.column_stack([returns_trey, risk_free_trey, beta_trey])
    treynor = (returns_trey - risk_free_trey) / beta_trey + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_treynor, y=treynor,
        variable_names=['returns', 'risk_free', 'risk_beta'],
        variable_descriptions={'returns': 'Portfolio returns', 'risk_free': 'Risk-free rate', 'risk_beta': 'Systematic risk (beta)'},
        variable_units={'returns': 'percent', 'risk_free': 'percent', 'risk_beta': 'dimensionless'},
        description="Treynor ratio - return per unit of systematic risk"
    )
    
    # Formula 9: Calmar Ratio
    print("Generating Calmar Ratio dataset...")
    annual_return = np.random.uniform(-0.1, 0.3, n_samples)
    max_drawdown = np.random.uniform(0.05, 0.5, n_samples)
    X_calmar = np.column_stack([annual_return, max_drawdown])
    calmar = annual_return / max_drawdown + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_calmar, y=calmar,
        variable_names=['annual_return', 'max_drawdown'],
        variable_descriptions={'annual_return': 'Annualized return', 'max_drawdown': 'Maximum drawdown'},
        variable_units={'annual_return': 'percent', 'max_drawdown': 'percent'},
        description="Calmar ratio - return relative to maximum drawdown"
    )
    
    # Formula 10: Omega Ratio (simplified)
    print("Generating Omega Ratio dataset...")
    gains = np.random.uniform(0, 0.3, n_samples)
    losses = np.random.uniform(0, 0.2, n_samples)
    X_omega = np.column_stack([gains, losses])
    omega = (gains + 0.01) / (losses + 0.01) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_omega, y=omega,
        variable_names=['gains', 'losses'],
        variable_descriptions={'gains': 'Expected gains above threshold', 'losses': 'Expected losses below threshold'},
        variable_units={'gains': 'percent', 'losses': 'percent'},
        description="Omega ratio - probability weighted gains vs losses"
    )
    
    # Formula 11: VaR 99%
    print("Generating VaR 99% dataset...")
    mu_99 = np.random.uniform(-0.1, 0.15, n_samples)
    sigma_99 = np.random.uniform(0.05, 0.5, n_samples)
    t_99 = np.random.uniform(1, 252, n_samples)
    X_var99 = np.column_stack([mu_99, sigma_99, t_99])
    var_99 = mu_99 - 2.576 * sigma_99 * np.sqrt(t_99) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_var99, y=var_99,
        variable_names=['mu', 'sigma', 't'],
        variable_descriptions={'mu': 'Expected return', 'sigma': 'Volatility', 't': 'Time horizon'},
        variable_units={'mu': 'percent', 'sigma': 'percent', 't': 'dimensionless'},
        description="Value at Risk at 99% confidence level"
    )
    
    # Formula 12: Modified Sharpe Ratio
    print("Generating Modified Sharpe Ratio dataset...")
    ret_mod = np.random.uniform(-0.1, 0.3, n_samples)
    rf_mod = np.random.uniform(0.01, 0.05, n_samples)
    mod_vol = np.random.uniform(0.05, 0.3, n_samples)
    skew = np.random.uniform(-0.5, 0.5, n_samples)
    X_modsharpe = np.column_stack([ret_mod, rf_mod, mod_vol, skew])
    mod_sharpe = (ret_mod - rf_mod) / (mod_vol * (1 + skew/6)) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_modsharpe, y=mod_sharpe,
        variable_names=['returns', 'risk_free', 'volatility', 'skewness'],
        variable_descriptions={'returns': 'Portfolio returns', 'risk_free': 'Risk-free rate', 'volatility': 'Volatility', 'skewness': 'Return skewness'},
        variable_units={'returns': 'percent', 'risk_free': 'percent', 'volatility': 'percent', 'skewness': 'dimensionless'},
        description="Modified Sharpe ratio adjusting for skewness"
    )
    
    # Formula 13: Ulcer Index
    print("Generating Ulcer Index dataset...")
    dd_squared_sum = np.random.uniform(0.01, 0.5, n_samples)
    periods = np.random.uniform(10, 252, n_samples)
    X_ulcer = np.column_stack([dd_squared_sum, periods])
    ulcer = np.sqrt(dd_squared_sum / periods) + np.random.normal(0, noise_level/10, n_samples)
    
    system.discover_validate_interpret(
        X=X_ulcer, y=ulcer,
        variable_names=['dd_squared_sum', 'periods'],
        variable_descriptions={'dd_squared_sum': 'Sum of squared drawdowns', 'periods': 'Number of periods'},
        variable_units={'dd_squared_sum': 'percent^2', 'periods': 'dimensionless'},
        description="Ulcer Index - downside volatility measure"
    )
    
    # Formula 14: Martin Ratio
    print("Generating Martin Ratio dataset...")
    ret_martin = np.random.uniform(-0.1, 0.3, n_samples)
    ulcer_martin = np.random.uniform(0.05, 0.3, n_samples)
    X_martin = np.column_stack([ret_martin, ulcer_martin])
    martin = ret_martin / ulcer_martin + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_martin, y=martin,
        variable_names=['returns', 'ulcer_index'],
        variable_descriptions={'returns': 'Portfolio returns', 'ulcer_index': 'Ulcer Index'},
        variable_units={'returns': 'percent', 'ulcer_index': 'percent'},
        description="Martin ratio - return per unit of Ulcer Index"
    )
    
    # Formula 15: Kappa Ratio (3rd order)
    print("Generating Kappa 3 Ratio dataset...")
    ret_kappa = np.random.uniform(-0.1, 0.3, n_samples)
    lpm3 = np.random.uniform(0.001, 0.1, n_samples)
    X_kappa = np.column_stack([ret_kappa, lpm3])
    kappa3 = ret_kappa / np.power(lpm3, 1/3) + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_kappa, y=kappa3,
        variable_names=['returns', 'lpm3'],
        variable_descriptions={'returns': 'Portfolio returns', 'lpm3': 'Lower partial moment (3rd order)'},
        variable_units={'returns': 'percent', 'lpm3': 'percent^3'},
        description="Kappa 3 ratio - return per unit of downside risk"
    )
    
    # Formula 16: Gain-Loss Ratio
    print("Generating Gain-Loss Ratio dataset...")
    avg_gain = np.random.uniform(0.01, 0.1, n_samples)
    avg_loss = np.random.uniform(0.01, 0.1, n_samples)
    X_gainloss = np.column_stack([avg_gain, avg_loss])
    gainloss = avg_gain / avg_loss + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_gainloss, y=gainloss,
        variable_names=['avg_gain', 'avg_loss'],
        variable_descriptions={'avg_gain': 'Average gain per winning trade', 'avg_loss': 'Average loss per losing trade'},
        variable_units={'avg_gain': 'percent', 'avg_loss': 'percent'},
        description="Gain-Loss ratio - average win to average loss"
    )
    
    # Formula 17: Upside Potential Ratio
    print("Generating Upside Potential Ratio dataset...")
    upside_potential = np.random.uniform(0.05, 0.3, n_samples)
    downside_risk = np.random.uniform(0.03, 0.2, n_samples)
    X_upr = np.column_stack([upside_potential, downside_risk])
    upr = upside_potential / downside_risk + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_upr, y=upr,
        variable_names=['upside_potential', 'downside_risk'],
        variable_descriptions={'upside_potential': 'Expected upside above MAR', 'downside_risk': 'Downside deviation below MAR'},
        variable_units={'upside_potential': 'percent', 'downside_risk': 'percent'},
        description="Upside Potential Ratio"
    )
    
    # Formula 18: Sterling Ratio
    print("Generating Sterling Ratio dataset...")
    annual_ret_sterling = np.random.uniform(-0.1, 0.3, n_samples)
    avg_dd = np.random.uniform(0.05, 0.4, n_samples)
    X_sterling = np.column_stack([annual_ret_sterling, avg_dd])
    sterling = (annual_ret_sterling - 0.1) / avg_dd + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_sterling, y=sterling,
        variable_names=['annual_return', 'avg_drawdown'],
        variable_descriptions={'annual_return': 'Annualized return', 'avg_drawdown': 'Average drawdown'},
        variable_units={'annual_return': 'percent', 'avg_drawdown': 'percent'},
        description="Sterling ratio - excess return per unit of average drawdown"
    )
    
    # Formula 19: Burke Ratio
    print("Generating Burke Ratio dataset...")
    excess_ret = np.random.uniform(-0.05, 0.25, n_samples)
    sqrt_sum_dd = np.random.uniform(0.1, 0.6, n_samples)
    X_burke = np.column_stack([excess_ret, sqrt_sum_dd])
    burke = excess_ret / sqrt_sum_dd + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_burke, y=burke,
        variable_names=['excess_return', 'sqrt_sum_dd'],
        variable_descriptions={'excess_return': 'Return above risk-free rate', 'sqrt_sum_dd': 'Square root of sum of squared drawdowns'},
        variable_units={'excess_return': 'percent', 'sqrt_sum_dd': 'percent'},
        description="Burke ratio - return per unit of drawdown magnitude"
    )
    
    # Formula 20: Pain Ratio
    print("Generating Pain Ratio dataset...")
    ret_pain = np.random.uniform(-0.1, 0.3, n_samples)
    pain_index = np.random.uniform(0.02, 0.3, n_samples)
    X_pain = np.column_stack([ret_pain, pain_index])
    pain_ratio = ret_pain / pain_index + np.random.normal(0, noise_level, n_samples)
    
    system.discover_validate_interpret(
        X=X_pain, y=pain_ratio,
        variable_names=['returns', 'pain_index'],
        variable_descriptions={'returns': 'Portfolio returns', 'pain_index': 'Average drawdown over period'},
        variable_units={'returns': 'percent', 'pain_index': 'percent'},
        description="Pain ratio - return per unit of pain index"
    )
    
    # Save results
    os.makedirs('hypatiax/data/finance/risk', exist_ok=True)
    system.export_results('hypatiax/data/finance/risk/risk_comprehensive_20.json', format='json')
    
    # Summary statistics
    valid = sum(1 for r in system.results if r['validation']['valid'])
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Samples per formula: {n_samples}")
    print(f"  Noise level: {noise_level}")
    print(f"  Output: data/risk_comprehensive_20.json")
    print(f"{'='*60}")
    
    return system

if __name__ == "__main__":
    system = generate_risk_formulas(n_samples=200, noise_level=0.01)
