import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np


FEATURES = [
    "connections",
    "failed_connections",
    "unique_destinations",
    "bytes_out",
]


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "isolation_forest.joblib"
)


model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# DETECTION
# --------------------------------------------------

def ml_detect(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect anomalous network behavior using
    the trained Isolation Forest model.
    """

    values = np.array([[
        event.get("connections", 0),
        event.get("failed_connections", 0),
        event.get("unique_destinations", 0),
        event.get("bytes_out", 0),
    ]])

    prediction = model.predict(values)[0]

    anomaly_score = model.decision_function(values)[0]

    is_anomaly = prediction == -1

    normalized_score = int(
        max(
            0,
            min(
                100,
                (0.5 - anomaly_score) * 100
            )
        )
    )

    return {
        "is_anomaly": bool(is_anomaly),
        "anomaly_score": normalized_score,
        "model": "IsolationForest",
    }