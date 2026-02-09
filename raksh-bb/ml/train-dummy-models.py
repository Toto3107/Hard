import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_dummy_dataset(n_samples: int = 2000) -> pd.DataFrame:
    # Simple synthetic region: e.g., lat 19–24, lon 72–80 (roughly central India)
    lats = np.random.uniform(19.0, 24.0, size=n_samples)
    lons = np.random.uniform(72.0, 80.0, size=n_samples)

    # Fake heuristic for feasibility:
    # - some band is "good", others "bad"
    center_lat, center_lon = 21.5, 76.0
    dist = np.sqrt((lats - center_lat) ** 2 + (lons - center_lon) ** 2)

    # closer to center → more feasible
    feas_prob = np.exp(-dist)  # 0..1-ish
    feas = (np.random.rand(n_samples) < feas_prob).astype(int)

    # Depth: deeper when farther from center, plus noise
    base_depth = 80 + dist * 80  # 80m to ~200m
    noise = np.random.normal(0, 10, size=n_samples)
    depth = np.clip(base_depth + noise, 40, 250)

    df = pd.DataFrame(
        {
            "latitude": lats,
            "longitude": lons,
            "feasible": feas,
            "depth_m": depth,
        }
    )

    return df

def train_and_save_models():
    df = generate_dummy_dataset()
    csv_path = os.path.join(DATA_DIR, "raksh_dummy_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved dummy dataset to {csv_path} (shape={df.shape})")

    feature_cols = ["latitude", "longitude"]
    X = df[feature_cols]
    y_f = df["feasible"].astype(int)
    y_d = df["depth_m"].astype(float)

    X_train, X_test, y_f_train, y_f_test = train_test_split(
        X, y_f, test_size=0.2, random_state=42
    )
    _, _, y_d_train, y_d_test = train_test_split(
        X, y_d, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_f_train)

    reg = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    reg.fit(X_train, y_d_train)

    feas_bundle = {"model": clf, "features": feature_cols}
    depth_bundle = {"model": reg, "features": feature_cols}

    feas_path = os.path.join(MODELS_DIR, "feasibility_rf.joblib")
    depth_path = os.path.join(MODELS_DIR, "depth_rf.joblib")

    joblib.dump(feas_bundle, feas_path)
    joblib.dump(depth_bundle, depth_path)

    print(f"Saved classifier to {feas_path}")
    print(f"Saved regressor to {depth_path}")

if __name__ == "__main__":
    train_and_save_models()
