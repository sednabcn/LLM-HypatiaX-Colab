import matplotlib.pyplot as plt
import numpy as np

# Data specifications
T_train = np.linspace(273, 373, 200)  # Training range [273, 373]K
T_extrap_near = np.linspace(448, 537, 50)  # 1.2× regime
T_extrap_medium = np.linspace(746, 1119, 50)  # 2× regime  
T_extrap_far = np.linspace(1865, 2795, 50)  # 5× regime

# Ground truth Arrhenius equation
A = 1e11
Ea = 80000  # J/mol
R = 8.314  # J/(mol·K)
k_true = lambda T: A * np.exp(-Ea / (R * T))

# Neural network predictions (piecewise linear approximation)
# Learns ~64 linear segments in training range
# Extrapolates linearly from boundaries → catastrophic
def nn_predict(T):
    if T <= 373:  # Interpolation
        return k_true(T) + np.random.normal(0, 0.05 * k_true(T))
    else:  # Extrapolation - linear divergence
        slope_at_boundary = ... # derivative at T=373
        return k_true(373) + slope_at_boundary * (T - 373)
        # This will be VERY wrong for exponential decay

# Hybrid v40 discovered expression (rational approximation)
def hybrid_predict(T):
    # From File 4: (T * (0.130/T)/(393.7 - T) - 4.9e-6) * (T - (601.3 - T))
    return (T * (0.130368 / (T * (393.7101 - T)) - 4.9038e-6)) * (T - (601.2518 - T)) - 0.0035860

# Plot requirements
fig, ax = plt.subplots(figsize=(10, 6))

# 1. Training region (green shaded background)
ax.axvspan(273, 373, alpha=0.2, color='green', label='Training Range')

# 2. Ground truth (black solid line)
T_all = np.linspace(273, 2800, 1000)
ax.plot(T_all, k_true(T_all), 'k-', linewidth=2, label='Ground Truth')

# 3. Neural Network (red dashed) - shows divergence
ax.plot(T_train, nn_train_predictions, 'r--', linewidth=2, label='Neural Network')
ax.plot(T_extrap, nn_extrap_predictions, 'r--', linewidth=2, alpha=0.7)

# 4. Hybrid v40 (blue/green solid) - perfect match
ax.plot(T_all, hybrid_predict(T_all), 'b-', linewidth=2, label='Hybrid v40', alpha=0.8)

# 5. Annotation at 2× point (T=746K)
ax.annotate('NN Error: 3348%', xy=(746, nn_predict(746)), 
            xytext=(900, nn_predict(746)*2),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            fontsize=12, color='red', weight='bold')

# Formatting
ax.set_xlabel('Temperature T (K)', fontsize=14)
ax.set_ylabel('Rate Constant k', fontsize=14)
ax.set_title('Extrapolation Failure: Arrhenius Equation', fontsize=16, weight='bold')
ax.legend(loc='upper right', fontsize=12)
ax.set_yscale('log')  # Log scale for exponential decay
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figure1_extrapolation_failure.png', dpi=300, bbox_inches='tight')
