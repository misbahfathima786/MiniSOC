from typing import Dict, Any


def get_host_history(host_id: str, incidents: list) -> Dict[str, Any]:
    """Return previous incidents associated with a host."""

    history = [
        incident
        for incident in incidents
        if incident["host_id"] == host_id
    ]

    return {
        "host_id": host_id,
        "incident_count": len(history),
        "incidents": history,
    }


def get_network_connections(event: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize network behavior for the agent."""

    return {
        "connections": event.get("connections", 0),
        "failed_connections": event.get("failed_connections", 0),
        "unique_destinations": event.get("unique_destinations", 0),
        "bytes_out": event.get("bytes_out", 0),
        "event_type": event.get("event_type", "UNKNOWN"),
    }


def investigate_incident(
    incident: Dict[str, Any],
    event: Dict[str, Any],
    incidents: list,
) -> Dict[str, Any]:
    """
    Deterministic SOC investigation workflow.

    The agent gathers context, evaluates risk,
    and recommends a response.
    """

    host_id = incident["host_id"]

    history = get_host_history(
        host_id,
        incidents,
    )

    network = get_network_connections(event)

    findings = []

    if network["connections"] > 80:
        findings.append(
            "High connection volume detected."
        )

    if network["failed_connections"] > 20:
        findings.append(
            "Large number of failed connections detected."
        )

    if network["unique_destinations"] > 15:
        findings.append(
            "Destination diversity is outside the normal baseline."
        )

    if network["bytes_out"] > 5_000_000:
        findings.append(
            "High outbound traffic detected."
        )

    risk_score = incident["risk_score"]

    if risk_score >= 70:
        recommendation = "ISOLATE_HOST"
    elif risk_score >= 40:
        recommendation = "MONITOR_HOST"
    else:
        recommendation = "NO_ACTION"

    return {
        "host_id": host_id,
        "risk_score": risk_score,
        "findings": findings,
        "previous_incidents": history["incident_count"],
        "network_context": network,
        "recommendation": recommendation,
        "investigation_status": "COMPLETE",
    }


def generate_incident_report(
    incident: Dict[str, Any],
    investigation: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a structured SOC incident report."""
    report_status = (
    "CONTAINED"
    if investigation["recommendation"] == "ISOLATE_HOST"
    else str(incident["status"])
    )
    return {
        "incident_id": incident["id"],
        "host_id": incident["host_id"],
        "severity": incident["severity"],
        "risk_score": incident["risk_score"],
        "status": report_status,
        "findings": investigation["findings"],
        "recommendation": investigation["recommendation"],
        "summary": (
            f"{incident['severity']} severity network security "
            f"incident detected on {incident['host_id']}. "
            f"Investigation recommends "
            f"{investigation['recommendation']}."
        ),
    }