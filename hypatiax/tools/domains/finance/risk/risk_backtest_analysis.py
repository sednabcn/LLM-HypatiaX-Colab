import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import stats

# ===== DATA FETCHING =====

COINGECKO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SPY': 'spdr-s-p-500-etf-trust',  # S&P 500 ETF
    'GLD': 'spdr-gold-shares',  # Gold ETF
    'AGG': 'ishares-core-u-s-aggregate-bond-etf',  # Bond ETF
}

def get_historical_prices(symbol, days=365):
    """Fetch historical price data from CoinGecko"""
    
    coin_id = COINGECKO_IDS.get(symbol.upper())
    
    if not coin_id:
        print(f"❌ Symbol '{symbol}' not found!")
        return []
    
    print(f"📊 Fetching {symbol} prices ({days} days)...")
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        prices = []
        for timestamp, price in data['prices']:
            prices.append({
                'timestamp': timestamp,
                'date': datetime.fromtimestamp(timestamp/1000),
                'price_usd': price
            })
        return prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return []

# ===== RISK METRIC CALCULATIONS =====

def calculate_rolling_metrics(returns: pd.Series, window: int = 30) -> pd.DataFrame:
    """
    Calculate rolling risk metrics
    
    Args:
        returns: Daily returns series
        window: Rolling window size
    """
    df = pd.DataFrame()
    
    # Rolling Volatility (annualized)
    df['volatility'] = returns.rolling(window).std() * np.sqrt(252) * 100
    
    # Rolling Sharpe (assuming 3% risk-free rate)
    risk_free_daily = 0.03 / 252
    df['sharpe'] = (returns.rolling(window).mean() - risk_free_daily) / returns.rolling(window).std() * np.sqrt(252)
    
    # Rolling VaR 95%
    df['var_95'] = returns.rolling(window).quantile(0.05) * 100
    
    # Rolling Max Drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.rolling(window, min_periods=1).max()
    drawdown = (cumulative - running_max) / running_max
    df['max_dd'] = drawdown.rolling(window).min() * 100
    
    return df

def calculate_portfolio_metrics(returns: np.ndarray, benchmark_returns: np.ndarray = None) -> Dict:
    """Calculate comprehensive portfolio metrics"""
    
    # Basic statistics
    total_return = (1 + returns).prod() - 1
    annual_return = (1 + total_return) ** (252 / len(returns)) - 1
    volatility = np.std(returns) * np.sqrt(252)
    
    # VaR and CVaR
    var_95 = np.percentile(returns, 5)
    cvar_95 = np.mean(returns[returns <= var_95])
    
    # Sharpe Ratio
    risk_free = 0.03 / 252
    sharpe = (np.mean(returns) - risk_free) / np.std(returns) * np.sqrt(252)
    
    # Sortino Ratio
    downside_returns = returns[returns < 0]
    sortino = (np.mean(returns) - risk_free) / np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
    
    # Maximum Drawdown
    cumulative = (1 + returns).cumprod()
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = np.min(drawdown)
    
    # Calmar Ratio
    calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
    
    metrics = {
        'total_return': total_return * 100,
        'annual_return': annual_return * 100,
        'volatility': volatility * 100,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'var_95': var_95 * 100,
        'cvar_95': cvar_95 * 100,
        'max_drawdown': max_dd * 100,
        'calmar_ratio': calmar,
        'winning_days': len(returns[returns > 0]),
        'losing_days': len(returns[returns < 0]),
        'win_rate': len(returns[returns > 0]) / len(returns) * 100
    }
    
    # Add beta and tracking metrics if benchmark provided
    if benchmark_returns is not None and len(benchmark_returns) == len(returns):
        covariance = np.cov(returns, benchmark_returns)[0, 1]
        market_variance = np.var(benchmark_returns)
        beta = covariance / market_variance if market_variance > 0 else 1.0
        
        # Treynor Ratio
        treynor = (np.mean(returns) - risk_free) / beta * 252 if beta != 0 else 0
        
        # Information Ratio
        active_returns = returns - benchmark_returns
        ir = np.mean(active_returns) / np.std(active_returns) * np.sqrt(252) if np.std(active_returns) > 0 else 0
        
        # Correlation
        correlation = np.corrcoef(returns, benchmark_returns)[0, 1]
        
        metrics.update({
            'beta': beta,
            'treynor_ratio': treynor,
            'information_ratio': ir,
            'correlation': correlation,
            'tracking_error': np.std(active_returns) * np.sqrt(252) * 100
        })
    
    return metrics

# ===== BACKTESTING ENGINE =====

def backtest_portfolio_strategy(prices: List[Dict], initial_investment: float = 100000,
                                rebalance_frequency: int = 30) -> pd.DataFrame:
    """
    Backtest a simple portfolio strategy
    
    Args:
        prices: List of price dictionaries
        initial_investment: Starting capital
        rebalance_frequency: Days between rebalancing
    """
    
    if not prices:
        return pd.DataFrame()
    
    df = pd.DataFrame(prices)
    df['returns'] = df['price_usd'].pct_change()
    df['cumulative_returns'] = (1 + df['returns']).cumprod()
    df['portfolio_value'] = initial_investment * df['cumulative_returns']
    
    # Calculate drawdown
    df['running_max'] = df['portfolio_value'].cummax()
    df['drawdown'] = (df['portfolio_value'] - df['running_max']) / df['running_max'] * 100
    
    # Calculate rolling metrics
    rolling_metrics = calculate_rolling_metrics(df['returns'].dropna())
    df = df.join(rolling_metrics, how='left')
    
    return df

def compare_strategies(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Compare multiple portfolio strategies
    
    Args:
        data_dict: Dictionary of {name: dataframe} for each strategy
    """
    
    comparison = []
    
    for name, df in data_dict.items():
        returns = df['returns'].dropna().values
        
        if len(returns) == 0:
            continue
        
        metrics = calculate_portfolio_metrics(returns)
        metrics['strategy'] = name
        comparison.append(metrics)
    
    return pd.DataFrame(comparison)

# ===== STRESS TESTING =====

def stress_test_portfolio(returns: np.ndarray, scenarios: Dict[str, float]) -> Dict:
    """
    Stress test portfolio under various scenarios
    
    Args:
        returns: Historical returns
        scenarios: Dict of {scenario_name: shock_percentage}
    """
    
    current_value = 100000
    results = {}
    
    for scenario_name, shock in scenarios.items():
        stressed_value = current_value * (1 + shock)
        loss = current_value - stressed_value
        
        # Calculate probability of this scenario
        mu = np.mean(returns)
        sigma = np.std(returns)
        z_score = (shock - mu) / sigma if sigma > 0 else 0
        probability = stats.norm.cdf(z_score) * 100
        
        results[scenario_name] = {
            'shock_pct': shock * 100,
            'portfolio_value': stressed_value,
            'loss_amount': loss,
            'probability_pct': probability
        }
    
    return results

# ===== VISUALIZATION =====

def create_risk_dashboard(df: pd.DataFrame, symbol: str, save_path: str):
    """Create comprehensive risk analysis dashboard"""
    
    if df.empty:
        print("No data to visualize")
        return
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle(f'{symbol.upper()} Risk Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Portfolio Value & Drawdown
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(df['date'], df['portfolio_value'], 'b-', linewidth=2, label='Portfolio Value')
    ax1_twin.plot(df['date'], df['drawdown'], 'r-', linewidth=2, label='Drawdown %')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Portfolio Value ($)', color='b')
    ax1_twin.set_ylabel('Drawdown (%)', color='r')
    ax1.set_title('Portfolio Value & Drawdown')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    
    # 2. Rolling Volatility
    ax2 = axes[0, 1]
    ax2.plot(df['date'], df['volatility'], 'purple', linewidth=2)
    ax2.fill_between(df['date'], 0, df['volatility'], alpha=0.3, color='purple')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Annualized Volatility (%)')
    ax2.set_title('Rolling 30-Day Volatility')
    ax2.grid(True, alpha=0.3)
    
    # 3. Rolling Sharpe Ratio
    ax3 = axes[1, 0]
    ax3.plot(df['date'], df['sharpe'], 'g-', linewidth=2)
    ax3.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax3.axhline(y=1, color='orange', linestyle='--', linewidth=1, label='Target: 1.0')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Sharpe Ratio')
    ax3.set_title('Rolling 30-Day Sharpe Ratio')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Value at Risk (VaR 95%)
    ax4 = axes[1, 1]
    ax4.plot(df['date'], df['var_95'], 'r-', linewidth=2)
    ax4.fill_between(df['date'], df['var_95'], 0, alpha=0.3, color='red')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('VaR 95% (%)')
    ax4.set_title('Rolling Value at Risk (95% Confidence)')
    ax4.grid(True, alpha=0.3)
    
    # 5. Returns Distribution
    ax5 = axes[2, 0]
    returns_pct = df['returns'].dropna() * 100
    ax5.hist(returns_pct, bins=50, alpha=0.7, color='blue', edgecolor='black')
    ax5.axvline(x=returns_pct.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns_pct.mean():.2f}%')
    ax5.axvline(x=np.percentile(returns_pct, 5), color='orange', linestyle='--', linewidth=2, label=f'VaR 95%: {np.percentile(returns_pct, 5):.2f}%')
    ax5.set_xlabel('Daily Returns (%)')
    ax5.set_ylabel('Frequency')
    ax5.set_title('Returns Distribution')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Cumulative Returns
    ax6 = axes[2, 1]
    cumulative_pct = (df['cumulative_returns'] - 1) * 100
    ax6.plot(df['date'], cumulative_pct, 'darkgreen', linewidth=2)
    ax6.fill_between(df['date'], 0, cumulative_pct, where=(cumulative_pct > 0), alpha=0.3, color='green', label='Gain')
    ax6.fill_between(df['date'], 0, cumulative_pct, where=(cumulative_pct < 0), alpha=0.3, color='red', label='Loss')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('Cumulative Return (%)')
    ax6.set_title('Cumulative Returns')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n📊 Dashboard saved to: {save_path}")
    
    return fig

def print_risk_report(metrics: Dict, symbol: str):
    """Print formatted risk analysis report"""
    
    print("\n" + "="*70)
    print(f"📈 RISK ANALYSIS REPORT: {symbol.upper()}")
    print("="*70)
    
    print("\n📊 RETURN METRICS")
    print("-" * 70)
    print(f"Total Return:        {metrics['total_return']:>8.2f}%")
    print(f"Annualized Return:   {metrics['annual_return']:>8.2f}%")
    print(f"Win Rate:            {metrics['win_rate']:>8.2f}% ({metrics['winning_days']} winning days)")
    
    print("\n⚡ VOLATILITY METRICS")
    print("-" * 70)
    print(f"Annualized Volatility: {metrics['volatility']:>8.2f}%")
    print(f"VaR (95%):            {metrics['var_95']:>8.2f}%")
    print(f"CVaR (95%):           {metrics['cvar_95']:>8.2f}%")
    print(f"Maximum Drawdown:     {metrics['max_drawdown']:>8.2f}%")
    
    print("\n🎯 RISK-ADJUSTED RETURNS")
    print("-" * 70)
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:>8.2f}")
    print(f"Sortino Ratio:       {metrics['sortino_ratio']:>8.2f}")
    print(f"Calmar Ratio:        {metrics['calmar_ratio']:>8.2f}")
    
    if 'beta' in metrics:
        print("\n📉 MARKET COMPARISON")
        print("-" * 70)
        print(f"Beta:                {metrics['beta']:>8.2f}")
        print(f"Treynor Ratio:       {metrics['treynor_ratio']:>8.2f}")
        print(f"Information Ratio:   {metrics['information_ratio']:>8.2f}")
        print(f"Correlation:         {metrics['correlation']:>8.2f}")
        print(f"Tracking Error:      {metrics['tracking_error']:>8.2f}%")
    
    # Risk Assessment
    print("\n⚠️  RISK ASSESSMENT")
    print("-" * 70)
    
    risk_level = "Low"
    if metrics['volatility'] > 30:
        risk_level = "Very High"
    elif metrics['volatility'] > 20:
        risk_level = "High"
    elif metrics['volatility'] > 15:
        risk_level = "Moderate"
    
    print(f"Risk Level: {risk_level}")
    print(f"Recommendation: ", end="")
    
    if metrics['sharpe_ratio'] > 1.5 and metrics['max_drawdown'] > -20:
        print("STRONG BUY - Excellent risk-adjusted returns")
    elif metrics['sharpe_ratio'] > 1.0:
        print("BUY - Good risk-adjusted returns")
    elif metrics['sharpe_ratio'] > 0.5:
        print("HOLD - Moderate risk-adjusted returns")
    else:
        print("AVOID - Poor risk-adjusted returns")
    
    print("\n" + "="*70)

# ===== MAIN EXECUTION =====

def run_complete_risk_analysis(symbol='BTC', days=365, initial_investment=100000,
                                export_excel=True):
    """Run complete risk analysis with all metrics and visualizations"""
    
    print("🚀 Starting Comprehensive Risk Analysis...")
    print(f"Parameters: {days} days, ${initial_investment:,.0f} initial investment")
    print("-" * 70)
    
    # Fetch data
    print(f"\n1️⃣  Fetching historical {symbol} prices...")
    prices = get_historical_prices(symbol, days)
    
    if not prices:
        print("❌ Failed to fetch price data")
        return None
    
    print(f"✅ Fetched {len(prices)} days of price data")
    
    # Run backtest
    print("\n2️⃣  Running backtest simulation...")
    results_df = backtest_portfolio_strategy(prices, initial_investment)
    
    if results_df.empty:
        print("❌ Backtest failed")
        return None
    
    print(f"✅ Backtest complete: {len(results_df)} days simulated")
    
    # Calculate metrics
    print("\n3️⃣  Calculating risk metrics...")
    returns = results_df['returns'].dropna().values
    metrics = calculate_portfolio_metrics(returns)
    print_risk_report(metrics, symbol)
    
    # Stress test
    print("\n4️⃣  Running stress tests...")
    stress_scenarios = {
        'Market Crash (-30%)': -0.30,
        'Bear Market (-20%)': -0.20,
        'Correction (-10%)': -0.10,
        'Flash Crash (-5%)': -0.05,
        'Bull Rally (+50%)': 0.50
    }
    stress_results = stress_test_portfolio(returns, stress_scenarios)
    
    print("\n📊 STRESS TEST RESULTS")
    print("-" * 70)
    for scenario, result in stress_results.items():
        print(f"{scenario:<25} Value: ${result['portfolio_value']:>10,.0f}  "
              f"Loss: ${result['loss_amount']:>10,.0f}  "
              f"Prob: {result['probability_pct']:>5.2f}%")
    
    # Visualize
    print("\n5️⃣  Creating visualizations...")
    png_path = f'risk_analysis_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    create_risk_dashboard(results_df, symbol, png_path)
    
    # Export to Excel
    if export_excel:
        print("\n6️⃣  Exporting to Excel...")
        excel_path = f'risk_analysis_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            results_df.to_excel(writer, sheet_name='Daily Data', index=False)
            
            # Metrics sheet
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
            
            # Stress test sheet
            stress_df = pd.DataFrame(stress_results).T
            stress_df.to_excel(writer, sheet_name='Stress Tests')
            
        print(f"✅ Excel file saved: {excel_path}")
    
    print("\n🎉 Analysis complete!")
    
    return results_df, metrics

# ===== RUN THE ANALYSIS =====
if __name__ == "__main__":
    
    # Analyze different assets
    assets = ['BTC', 'ETH', 'SPY']
    
    for symbol in assets:
        results, metrics = run_complete_risk_analysis(
            symbol=symbol,
            days=365,
            initial_investment=100000
        )
        print("\n" + "="*70 + "\n")
