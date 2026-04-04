import numpy as np

def generate_work_energy_data(N=200, noise=0.01, seed=0):
    np.random.seed(seed)

    m = 1.0
    a = 2.0
    v0 = 0.0

    x = np.linspace(0, 10, N)
    v = np.sqrt(v0**2 + 2*a*x)
    W = 0.5 * m * v**2

    W_noisy = W + noise * np.random.randn(N)

    # Split
    train_mask = x <= 5
    test_mask = x > 5

    return {
        "x_train": x[train_mask],
        "y_train": W_noisy[train_mask],
        "x_test": x[test_mask],
        "y_test": W[test_mask],  # clean test
        "x_full": x,
        "y_true": W
    }
