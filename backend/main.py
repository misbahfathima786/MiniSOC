from agent import investigate_incident, generate_incident_report
from datetime import datetime, timezone
from typing import Dict, List
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from detector import detect_anomaly
from simulator import (
    HOSTS,
    normal_event,
    suspicious_event,
    port_scan_event,
    data_exfiltration_event,
)

app = FastAPI(
    title="MiniSOC",
    description="Autonomous Network Compromise Detection & Response Agent",
    version="0.1.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# In-memory MVP state
# ---------------------------------------------------------

hosts: List[Dict] = [dict(host) for host in HOSTS]

incidents: List[Dict] = []

connected_clients: List[WebSocket] = []


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc).isoformat()


async def broadcast(event: Dict):
    disconnected = []

    for client in connected_clients:
        try:
            await client.send_json(event)
        except Exception:
            disconnected.append(client)

    for client in disconnected:
        if client in connected_clients:
            connected_clients.remove(client)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "MiniSOC",
        "timestamp": utc_now(),
    }


# ---------------------------------------------------------
# Hosts
# ---------------------------------------------------------

@app.get("/api/hosts")
def get_hosts():
    return hosts


# ---------------------------------------------------------
# Incidents
# ---------------------------------------------------------

@app.get("/api/incidents")
def get_incidents():
    return incidents


# ---------------------------------------------------------
# Generate normal traffic
# ---------------------------------------------------------

@app.post("/api/simulate/normal/{host_id}")
async def simulate_normal(host_id: str):

    host = next(
        (h for h in hosts if h["id"] == host_id),
        None,
    )

    if not host:
        return {
            "error": "Host not found"
        }

    event = normal_event(host_id)

    result = detect_anomaly(event)

    response = {
        "type": "TRAFFIC_EVENT",
        "event": event,
        "detection": {
            "detected": result.detected,
            "severity": result.severity,
            "risk_score": result.risk_score,
            "reason": result.reason,
        },
    }

    await broadcast(response)

    return response

@app.get("/api/scenarios")
async def get_scenarios():
    return [
        {
            "id": "SUSPICIOUS_LATERAL_MOVEMENT",
            "name": "Suspicious Lateral Movement",
        },
        {
            "id": "PORT_SCAN",
            "name": "Port Scan",
        },
        {
            "id": "DATA_EXFILTRATION",
            "name": "Data Exfiltration",
        },
    ]

# ---------------------------------------------------------
# Simulate suspicious activity
# ---------------------------------------------------------

@app.post("/api/simulate/attack")
async def simulate_attack(scenario: dict | None = None):

    host_id = "HOST-03"

    # Prevent duplicate incidents for an already isolated host
    existing_incident = next(
        (
            incident
            for incident in incidents
            if incident["host_id"] == host_id
            and incident["status"] == "CONTAINED"
        ),
        None,
    )

    if existing_incident:
        return {
            "message": f"{host_id} is already contained.",
            "incident": existing_incident,
            "already_contained": True,
        }

    scenario_name = "SUSPICIOUS_LATERAL_MOVEMENT"

    if scenario:
        scenario_name = scenario.get(
            "scenario",
            "SUSPICIOUS_LATERAL_MOVEMENT",
        )

    if scenario_name == "PORT_SCAN":
        event = port_scan_event(host_id)
        incident_type = "Port Scan"

    elif scenario_name == "DATA_EXFILTRATION":
        event = data_exfiltration_event(host_id)
        incident_type = "Data Exfiltration"

    else:
        event = suspicious_event(host_id)
        incident_type = "Suspicious Lateral Movement"

    result = detect_anomaly(event)

    incident = {
        "id": f"INC-{str(uuid.uuid4())[:8].upper()}",
        "host_id": host_id,
        "host_name": next(
            h["name"] for h in hosts if h["id"] == host_id
        ),
        "type": incident_type,
        "severity": result.severity,
        "risk_score": result.risk_score,
        "status": "DETECTED",
        "detected_at": utc_now(),
        "contained_at": None,
        "reason": result.reason,
        "agent_status": "INVESTIGATING",
        "agent_reasoning": (
            "The detection engine identified abnormal "
            "network behavior. Agent investigation initiated."
        ),
    }

    incidents.insert(0, incident)

    # -----------------------------------------------------
    # SOC Agent investigation
    # -----------------------------------------------------

    investigation = investigate_incident(
        incident,
        event,
        incidents,
    )

    incident["agent_status"] = "INVESTIGATION_COMPLETE"
    incident["agent_findings"] = investigation["findings"]
    incident["agent_recommendation"] = investigation["recommendation"]

    await broadcast(
        {
            "type": "AGENT_INVESTIGATION",
            "incident_id": incident["id"],
            "host_id": host_id,
            "investigation": investigation,
        }
    )

    # Generate structured incident report
    report = generate_incident_report(
        incident,
        investigation,
    )

    incident["incident_report"] = report

    # -----------------------------------------------------
    # Autonomous SOC agent decision
    # -----------------------------------------------------

    if result.risk_score >= 70:
        await broadcast(
            {
                "type": "AGENT_INVESTIGATION",
                "incident_id": incident["id"],
                "host_id": host_id,
                "message": (
                    "Agent investigating abnormal network behavior "
                    "and evaluating containment."
                ),
            }
        )

        # Autonomous containment decision
        host = next(
            h for h in hosts if h["id"] == host_id
        )

        host["status"] = "ISOLATED"

        incident["status"] = "CONTAINED"
        incident["contained_at"] = utc_now()
        incident["agent_status"] = "CONTAINMENT_COMPLETE"

        incident["agent_reasoning"] = (
            "Risk score exceeded the autonomous containment "
            "threshold. The agent correlated abnormal connection "
            "volume, failed connections, destination diversity "
            "and outbound traffic, then isolated the affected host."
        )

        await broadcast(
            {
                "type": "AUTONOMOUS_CONTAINMENT",
                "incident": incident,
                "host_id": host_id,
                "message": (
                    f"Autonomous containment completed. "
                    f"{host_id} has been isolated."
                ),
            }
        )

    await broadcast(
        {
            "type": "INCIDENT_DETECTED",
            "incident": incident,
        }
    )

    return incident

# ---------------------------------------------------------
# Autonomous containment
# ---------------------------------------------------------

@app.post("/api/hosts/{host_id}/isolate")
async def isolate_host(host_id: str):

    host = next(
        (h for h in hosts if h["id"] == host_id),
        None,
    )

    if not host:
        return {
            "error": "Host not found"
        }

    host["status"] = "ISOLATED"

    affected_incidents = []

    for incident in incidents:
        if incident["host_id"] == host_id:
            incident["status"] = "CONTAINED"
            incident["contained_at"] = utc_now()
            incident["agent_status"] = "CONTAINMENT_COMPLETE"

            affected_incidents.append(incident)

    event = {
        "type": "HOST_ISOLATED",
        "host_id": host_id,
        "status": "ISOLATED",
        "timestamp": utc_now(),
        "message": f"{host_id} has been isolated by the response agent.",
        "incidents": affected_incidents,
    }

    await broadcast(event)

    return event

@app.post("/api/lab/reset")
async def reset_lab():

    # Reset all hosts
    for host in hosts:
        host["status"] = "ONLINE"

    # Clear incidents
    incidents.clear()

    await broadcast(
        {
            "type": "LAB_RESET",
            "message": "MiniSOC lab environment has been reset.",
            "timestamp": utc_now(),
        }
    )

    return {
        "status": "RESET",
        "message": "MiniSOC lab has been reset successfully.",
    }
# ---------------------------------------------------------
# WebSocket
# ---------------------------------------------------------

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):

    await websocket.accept()

    connected_clients.append(websocket)

    await websocket.send_json(
        {
            "type": "CONNECTION_ESTABLISHED",
            "message": "MiniSOC event stream connected.",
            "timestamp": utc_now(),
        }
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        if websocket in connected_clients:
            connected_clients.remove(websocket)