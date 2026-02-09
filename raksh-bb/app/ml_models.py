import os
import joblib
import numpy as np
from typing import Tuple

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

_feasibility_model = None
_depth_model = None
_feature_cols = None
MODEL_VERSION = "v1.0-rf"

def load_models():
    global _feasibility_model, _depth_model, _feature_cols

    feas_path = os.path.join(MODELS_DIR, "feasibility_rf.joblib")
    depth_path = os.path.join(MODELS_DIR, "depth_rf.joblib")

    feas_bundle = joblib.load(feas_path)
    depth_bundle = joblib.load(depth_path)

    _feasibility_model = feas_bundle["model"]
    _depth_model = depth_bundle["model"]
    _feature_cols = feas_bundle["features"]  # assume same list for both

def predict_from_models(lat: float, lon: float) -> Tuple[bool, float]:
    if _feasibility_model is None or _depth_model is None:
        raise RuntimeError("Models not loaded")

    # Order features according to _feature_cols
    feature_values = []
    for col in _feature_cols:
        if col == "latitude":
            feature_values.append(lat)
        elif col == "longitude":
            feature_values.append(lon)
        else:
            # for now, any extra features default to 0; later we compute them
            feature_values.append(0.0)

    X = np.array([feature_values])

    feasible_prob = _feasibility_model.predict_proba(X)[0, 1]
    feasible = feasible_prob >= 0.5

    depth = float(_depth_model.predict(X)[0])

    # If not feasible, you can optionally set depth=0
    if not feasible:
        depth = 0.0

    return feasible, depth
