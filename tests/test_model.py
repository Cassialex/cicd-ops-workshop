from sklearn.metrics import accuracy_score

from ci_cd.inference import predict
from ci_cd.train import load_data, train

# Min accuracy. Test fails if test accuracy after training dips below this.
MIN_ACCURACY = 0.8


def test_model_accuracy():
    # Train and save the model, and load it back the way deployment would.
    train()

    _, X_test, _, y_test = load_data()
    y_pred = predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    assert accuracy >= MIN_ACCURACY, (
        f"Accuracy {accuracy:.2f} is below threshold {MIN_ACCURACY:.2f}"
    )
