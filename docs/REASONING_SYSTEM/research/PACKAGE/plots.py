import matplotlib.pyplot as plt

def plot_results(data, predictions):
    plt.figure()

    plt.plot(data["x_full"], data["y_true"], label="True", linewidth=2)

    for name, y_pred in predictions.items():
        plt.plot(data["x_full"], y_pred, label=name)

    plt.axvline(5, linestyle="--", label="Train/Test Split")

    plt.legend()
    plt.xlabel("x")
    plt.ylabel("Work")
    plt.title("Extrapolation Comparison")
    plt.show()
