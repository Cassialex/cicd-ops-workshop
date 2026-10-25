import pathlib

import joblib
import numpy as np

MODEL_PATH = pathlib.Path("model/model.pkl")


def predict(X: np.ndarray) -> np.ndarray:
    clf = joblib.load(MODEL_PATH)
    return clf.predict(X)
