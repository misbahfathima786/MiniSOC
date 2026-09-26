from dataclasses import dataclass
from typing import Dict, Any

from ml_detector import ml_detect


@dataclass
class DetectionResult:
    detected: bool
    severity: str
    risk_score: int
    reason: str


def detect_anomaly(event: Dict[str, Any]) -> DetectionResult:
    """
    Hybrid defensive detector:
    - Rule-based detection
    - Isolation Forest ML anomaly detection
    """

    score = 0
    reasons = []

    connections = event.get("connections", 0)
    failed_connections = event.get("failed_connections", 0)
    unique_destinations = event.get("unique_destinations", 0)
    bytes_out = event.get("bytes_out", 0)

    # -----------------------------
    # ML anomaly detection
    # -----------------------------

    ml_result = ml_detect(event)

    if ml_result["is_anomaly"]:
        score += 20
        reasons.append(
            f"ML anomaly detected "
            f"(IsolationForest score: {ml_result['anomaly_score']})"
        )

    # -----------------------------
    # Rule-based detection
    # -----------------------------

    if connections > 80:
        score += 30
        reasons.append("abnormally high connection volume")

    if failed_connections > 20:
        score += 20
        reasons.append("high number of failed connections")

    if unique_destinations > 15:
        score += 25
        reasons.append("unusual number of destination hosts")

    if bytes_out > 5_000_000:
        score += 25
        reasons.append("unusually high outbound traffic")

    score = min(score, 100)

    if score >= 70:
        severity = "HIGH"
    elif score >= 40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    detected = score >= 40

    if not reasons:
        reason = "Network behavior within expected baseline."
    else:
        reason = "; ".join(reasons)

    return DetectionResult(
        detected=detected,
        severity=severity,
        risk_score=score,
        reason=reason,
    )