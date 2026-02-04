import matplotlib.pyplot as plt
import numpy as np

# Data from Tables 6 & 7
methods = ['Neural\nNetwork', 'Pure\nLLM', 'Hybrid\nv40']
times = [1.7, 6.9, 45.6]  # seconds
r2_scores = [0.93, 1.00, 1.00]
extrap_errors = [3348, np.nan, 0]  # NaN for LLM (not evaluated)
interpretable = [False, True, True]

# Create 2-panel figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel 1: Time vs Extrapolation Error (log scale)
colors = ['red', 'orange', 'green']
markers = ['X', 'o', 's']
sizes = [200, 200, 200]

for i, method in enumerate(methods):
    if not np.isnan(extrap_errors[i]):
        ax1.scatter(times[i], extrap_errors[i], 
                   s=sizes[i], c=colors[i], marker=markers[i],
                   label=method, edgecolors='black', linewidth=2,
                   alpha=0.8, zorder=10)

# Annotate each point
ax1.annotate('Catastrophic\nFailure', xy=(1.7, 3348), 
            xytext=(5, 5000), fontsize=11, color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
ax1.annotate('Not\nEvaluated', xy=(6.9, 1000), 
            fontsize=11, color='orange', style='italic')
ax1.annotate('Perfect\nExtrapolation', xy=(45.6, 50), 
            xytext=(50, 200), fontsize=11, color='green',
            arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

ax1.set_xlabel('Execution Time (seconds)', fontsize=14, weight='bold')
ax1.set_ylabel('Extrapolation Error (%)', fontsize=14, weight='bold')
ax1.set_title('Speed vs Extrapolation Trade-off', fontsize=16, weight='bold')
ax1.set_yscale('log')
ax1.set_ylim([10, 10000])
ax1.grid(True, alpha=0.3, which='both')
ax1.legend(loc='upper left', fontsize=12)

# Panel 2: 3D capability comparison (table-like visualization)
capabilities = ['Fast\nInference', 'High R²', 'Interpretable', 'Extrapolates', 'Discovers\nTruth']
capability_matrix = np.array([
    [1, 1, 0, 0, 0],  # Neural Network
    [1, 1, 1, 0, 0],  # Pure LLM (? for extrapolation)
    [1, 1, 1, 1, 1]   # Hybrid v40
])

im = ax2.imshow(capability_matrix.T, cmap='RdYlGn', aspect='auto', 
               vmin=0, vmax=1, alpha=0.8)

# Add grid and labels
ax2.set_xticks(np.arange(len(methods)))
ax2.set_yticks(np.arange(len(capabilities)))
ax2.set_xticklabels(methods, fontsize=12, weight='bold')
ax2.set_yticklabels(capabilities, fontsize=11)
ax2.set_title('Capability Matrix', fontsize=16, weight='bold')

# Add checkmarks/crosses
for i in range(len(methods)):
    for j in range(len(capabilities)):
        symbol = '✓' if capability_matrix[i, j] == 1 else '✗'
        color = 'white' if capability_matrix[i, j] == 1 else 'black'
        ax2.text(i, j, symbol, ha='center', va='center', 
                fontsize=20, color=color, weight='bold')

# Add border
for spine in ax2.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(2)

plt.tight_layout()
plt.savefig('figure5_regime_comparison.png', dpi=300, bbox_inches='tight')
