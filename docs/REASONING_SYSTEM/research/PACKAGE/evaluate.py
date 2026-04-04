from sklearn.metrics import mean_squared_error

def evaluate(model, data):
    y_train_pred = model.predict(data["x_train"])
    y_test_pred = model.predict(data["x_test"])

    train_mse = mean_squared_error(data["y_train"], y_train_pred)
    test_mse = mean_squared_error(data["y_test"], y_test_pred)

    return train_mse, test_mse
