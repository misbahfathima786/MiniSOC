import random
from datetime import datetime, timezone


HOSTS = [
    {
        "id": "HOST-01",
        "ip": "10.0.0.11",
        "name": "Finance-Workstation",
        "status": "ONLINE",
    },
    {
        "id": "HOST-02",
        "ip": "10.0.0.12",
        "name": "HR-Workstation",
        "status": "ONLINE",
    },
    {
        "id": "HOST-03",
        "ip": "10.0.0.13",
        "name": "Engineering-PC",
        "status": "ONLINE",
    },
    {
        "id": "HOST-04",
        "ip": "10.0.0.14",
        "name": "File-Server",
        "status": "ONLINE",
    },
]


def normal_event(host_id: str):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "connections": random.randint(10, 35),
        "failed_connections": random.randint(0, 5),
        "unique_destinations": random.randint(2, 8),
        "bytes_out": random.randint(100_000, 1_500_000),
        "event_type": "NORMAL_TRAFFIC",
    }


def suspicious_event(host_id: str):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "connections": random.randint(100, 160),
        "failed_connections": random.randint(25, 50),
        "unique_destinations": random.randint(20, 35),
        "bytes_out": random.randint(6_000_000, 15_000_000),
        "event_type": "SUSPICIOUS_LATERAL_MOVEMENT",
    }


def port_scan_event(host_id: str):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "connections": random.randint(90, 140),
        "failed_connections": random.randint(30, 60),
        "unique_destinations": random.randint(25, 45),
        "bytes_out": random.randint(500_000, 2_000_000),
        "event_type": "PORT_SCAN",
    }


def data_exfiltration_event(host_id: str):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "connections": random.randint(70, 120),
        "failed_connections": random.randint(5, 15),
        "unique_destinations": random.randint(3, 10),
        "bytes_out": random.randint(15_000_000, 40_000_000),
        "event_type": "DATA_EXFILTRATION",
    }