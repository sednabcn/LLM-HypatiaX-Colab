import numpy as np

class HybridAxiomaticModel:
    """
    Uses known structure from axioms:
    W = 1/2 m v^2
    v^2 = v0^2 + 2 a x
    """

    def __init__(self):
        self.m = 1.0
        self.a = None
        self.v0 = 0.0

    def fit(self, x, y):
        # Fit parameter 'a' using least squares
        # W = 1/2 * m * (2 a x) = m a x
        A = x.reshape(-1,1)
        self.a = np.linalg.lstsq(A, y, rcond=None)[0][0]

    def predict(self, x):
        return self.m * self.a * x
