import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error

class NeuralNetModel:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(64,64), max_iter=5000)

    def fit(self, x, y):
        self.model.fit(x.reshape(-1,1), y)

    def predict(self, x):
        return self.model.predict(x.reshape(-1,1))


class PolynomialModel:
    def __init__(self, degree=3):
        self.degree = degree
        self.coef = None

    def fit(self, x, y):
        self.coef = np.polyfit(x, y, self.degree)

    def predict(self, x):
        return np.polyval(self.coef, x)
