import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

# TODO: replace this with your real dataset path
df = pd.read_csv("data/raksh_dataset.csv")

feature_cols = ["latitude", "longitude"]  # extend later
X = df[feature_cols]

y_feasible = df["feasible"].astype(int)           # 0/1
y_depth = df["depth_m"].astype(float)             # numeric

X_train, X_test, y_f_train, y_f_test = train_test_split(
    X, y_feasible, test_size=0.2, random_state=42
)
_, _, y_d_train, y_d_test = train_test_split(
    X, y_depth, test_size=0.2, random_state=42
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

joblib.dump({"model": clf, "features": feature_cols}, "models/feasibility_rf.joblib")
joblib.dump({"model": reg, "features": feature_cols}, "models/depth_rf.joblib")

print("Saved models to models/feasibility_rf.joblib and models/depth_rf.joblib")
