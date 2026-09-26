import os
import json
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix


RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

FEATURES = [
    "connections",
    "failed_connections",
    "unique_destinations",
    "bytes_out",
]


# --------------------------------------------------
# NORMAL NETWORK BEHAVIOR
# --------------------------------------------------

def generate_normal(n):
    return np.column_stack([
        rng.normal(25, 8, n).clip(5, 60),
        rng.normal(3, 2, n).clip(0, 12),
        rng.normal(5, 2, n).clip(1, 12),
        rng.normal(500_000, 250_000, n).clip(50_000, 1_500_000),
    ])


# --------------------------------------------------
# PORT SCAN
# --------------------------------------------------

def generate_port_scan(n):
    return np.column_stack([
        rng.normal(115, 20, n).clip(70, 180),
        rng.normal(45, 10, n).clip(20, 80),
        rng.normal(35, 8, n).clip(20, 60),
        rng.normal(1_000_000, 400_000, n).clip(200_000, 3_000_000),
    ])


# --------------------------------------------------
# LATERAL MOVEMENT
# --------------------------------------------------

def generate_lateral_movement(n):
    return np.column_stack([
        rng.normal(125, 25, n).clip(80, 190),
        rng.normal(35, 8, n).clip(20, 70),
        rng.normal(27, 7, n).clip(16, 50),
        rng.normal(8_000_000, 2_500_000, n).clip(
            4_000_000,
            18_000_000,
        ),
    ])


# --------------------------------------------------
# DATA EXFILTRATION
# --------------------------------------------------

def generate_exfiltration(n):
    return np.column_stack([
        rng.normal(90, 18, n).clip(60, 150),
        rng.normal(10, 4, n).clip(2, 25),
        rng.normal(7, 3, n).clip(2, 15),
        rng.normal(25_000_000, 6_000_000, n).clip(
            10_000_000,
            50_000_000,
        ),
    ])


# --------------------------------------------------
# CREATE DATASET
# --------------------------------------------------

normal = generate_normal(2000)

port_scan = generate_port_scan(300)

lateral = generate_lateral_movement(300)

exfiltration = generate_exfiltration(300)


X = np.vstack([
    normal,
    port_scan,
    lateral,
    exfiltration,
])


# 0 = normal
# 1 = suspicious
y = np.concatenate([
    np.zeros(len(normal)),
    np.ones(len(port_scan)),
    np.ones(len(lateral)),
    np.ones(len(exfiltration)),
])


print()
print("=" * 60)
print("MINISOC ML TRAINING")
print("=" * 60)

print(f"Normal samples:       {len(normal)}")
print(f"Port scan samples:    {len(port_scan)}")
print(f"Lateral samples:      {len(lateral)}")
print(f"Exfiltration samples: {len(exfiltration)}")
print(f"Total samples:        {len(X)}")


# --------------------------------------------------
# TRAIN ONLY ON NORMAL TRAFFIC
# --------------------------------------------------

model = IsolationForest(
    n_estimators=200,
    contamination=0.15,
    random_state=RANDOM_SEED,
    n_jobs=1,
)

model.fit(normal)


# --------------------------------------------------
# EVALUATE
# --------------------------------------------------

predictions = model.predict(X)

# Isolation Forest:
# +1 = normal
# -1 = anomaly

predicted = (predictions == -1).astype(int)


print()
print("=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print(
    classification_report(
        y,
        predicted,
        target_names=[
            "Normal",
            "Suspicious",
        ],
        digits=3,
    )
)

print("Confusion Matrix:")
print(confusion_matrix(y, predicted))


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

models_dir = project_root / "models"

models_dir.mkdir(
    parents=True,
    exist_ok=True,
)


import joblib

model_path = models_dir / "isolation_forest.joblib"

joblib.dump(
    model,
    model_path,
)


# --------------------------------------------------
# SAVE METRICS
# --------------------------------------------------

report = classification_report(
    y,
    predicted,
    target_names=[
        "Normal",
        "Suspicious",
    ],
    output_dict=True,
)


metrics = {
    "model": "IsolationForest",
    "training_samples": len(normal),
    "evaluation_samples": len(X),
    "features": FEATURES,
    "classes": [
        "Normal",
        "Suspicious",
    ],
    "metrics": report,
}


metrics_path = models_dir / "metrics.json"

with open(
    metrics_path,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        metrics,
        file,
        indent=2,
    )


print()
print("=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(f"Model:   {model_path}")
print(f"Metrics: {metrics_path}")
print()