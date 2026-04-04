from data import generate_work_energy_data
from models import NeuralNetModel, PolynomialModel
from hybrid import HybridAxiomaticModel
from evaluate import evaluate
from plots import plot_results

data = generate_work_energy_data()

models = {
    "NeuralNet": NeuralNetModel(),
    "Polynomial": PolynomialModel(),
    "Hybrid": HybridAxiomaticModel()
}

predictions = {}

for name, model in models.items():
    model.fit(data["x_train"], data["y_train"])
    
    train_mse, test_mse = evaluate(model, data)
    
    print(f"{name}: Train MSE={train_mse:.4f}, Test MSE={test_mse:.4f}")
    
    predictions[name] = model.predict(data["x_full"])

plot_results(data, predictions)
