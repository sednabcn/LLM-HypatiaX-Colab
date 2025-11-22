# main_analysis.py
from hypatiax.tools import DeFiDataManager, run_complete_backtest

# Fetch real data
manager = DeFiDataManager()
prices = manager.fetch_and_store_prices("ethereum", days=90)

# Run backtest with real data
results = run_complete_backtest(days=90)

# Export combined results
manager.export_all_data("complete_analysis.xlsx")
