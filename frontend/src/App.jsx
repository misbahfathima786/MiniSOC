import { useEffect, useState } from "react";

import {
  ShieldAlert,
  ShieldCheck,
  Server,
  Activity,
  Brain,
  Lock,
  Wifi,
  AlertTriangle,
  Search,
  Zap,
} from "lucide-react";

import "./App.css";

const API = "http://localhost:8000";


function NetworkTopology({ hosts }) {
  const hostPositions = [
    { id: "HOST-01", className: "node-top-left" },
    { id: "HOST-02", className: "node-bottom-left" },
    { id: "HOST-03", className: "node-top-right" },
    { id: "HOST-04", className: "node-bottom-right" },
  ];

  const getHost = (id) =>
    hosts.find((host) => host.id === id);

  return (
    <div>
      <div className="panel-header">
        <div>
          <p className="panel-label">NETWORK VISIBILITY</p>
          <h3>Live Network Topology</h3>
        </div>

        <Activity size={22} />
      </div>

      <div className="topology">
        <svg
          className="topology-lines"
          viewBox="0 0 1000 500"
        >
          <line
            x1="500"
            y1="250"
            x2="210"
            y2="120"
          />

          <line
            x1="500"
            y1="250"
            x2="210"
            y2="380"
          />

          <line
            x1="500"
            y1="250"
            x2="790"
            y2="120"
          />

          <line
            x1="500"
            y1="250"
            x2="790"
            y2="380"
          />
        </svg>

        <div className="soc-node">
          <Brain size={30} />

          <strong>SOC AGENT</strong>

          <span>AI DEFENSE</span>
        </div>

        {hostPositions.map(({ id, className }) => {
          const host = getHost(id);

          if (!host) {
            return null;
          }

          const isolated =
            host.status === "ISOLATED";

          return (
            <div
              key={id}
              className={`network-node ${className} ${
                isolated ? "isolated-node" : ""
              }`}
            >
              <div className="node-icon">
                {isolated ? (
                  <Lock size={22} />
                ) : (
                  <Server size={22} />
                )}
              </div>

              <strong>{host.id}</strong>

              <span>{host.name}</span>

              <small
                className={
                  isolated
                    ? "node-danger"
                    : "node-online"
                }
              >
                ● {host.status}
              </small>
            </div>
          );
        })}
      </div>
    </div>
  );
}


function App() {
  const [hosts, setHosts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  const [attackScenario, setAttackScenario] =
    useState(
      "SUSPICIOUS_LATERAL_MOVEMENT"
    );


  const loadData = async () => {
    try {
      const [
        hostsResponse,
        incidentsResponse,
      ] = await Promise.all([
        fetch(`${API}/api/hosts`),
        fetch(`${API}/api/incidents`),
      ]);

      setHosts(
        await hostsResponse.json()
      );

      setIncidents(
        await incidentsResponse.json()
      );
    } catch (error) {
      console.error(
        "Backend connection failed:",
        error
      );
    }
  };


  useEffect(() => {
    loadData();

    const socket = new WebSocket(
      "ws://localhost:8000/ws/events"
    );

    socket.onopen = () => {
      setConnected(true);
    };

    socket.onclose = () => {
      setConnected(false);
    };

    socket.onmessage = (message) => {
      const data = JSON.parse(
        message.data
      );

      setEvents((previous) => [
        {
          ...data,
          receivedAt:
            new Date().toLocaleTimeString(),
        },
        ...previous,
      ].slice(0, 10));

      if (
        data.type === "INCIDENT_DETECTED" ||
        data.type === "AGENT_INVESTIGATION" ||
        data.type === "AUTONOMOUS_CONTAINMENT" ||
        data.type === "HOST_ISOLATED" ||
        data.type === "LAB_RESET"
      ) {
        loadData();
      }
    };

    return () => {
      socket.close();
    };
  }, []);


  const simulateAttack = async () => {
    setLoading(true);

    try {
      await fetch(
        `${API}/api/simulate/attack`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            scenario: attackScenario,
          }),
        }
      );

      await loadData();
    } catch (error) {
      console.error(
        "Attack simulation failed:",
        error
      );
    } finally {
      setLoading(false);
    }
  };

  const resetLab = async () => {
    try {
      await fetch(`${API}/api/lab/reset`, {
        method: "POST",
      });

      setEvents([]);
      await loadData();
    } catch (error) {
      console.error("Lab reset failed:", error);
    }
  };
  const isolateHost = async (hostId) => {
    try {
      await fetch(
        `${API}/api/hosts/${hostId}/isolate`,
        {
          method: "POST",
        }
      );

      await loadData();
    } catch (error) {
      console.error(
        "Host isolation failed:",
        error
      );
    }
  };


  const activeIncidents =
    incidents.filter(
      (incident) =>
        incident.status !== "CONTAINED"
    );


  const containedIncidents =
    incidents.filter(
      (incident) =>
        incident.status === "CONTAINED"
    );


  const highRisk =
    incidents.filter(
      (incident) =>
        incident.risk_score >= 70
    );


  return (
    <div className="app">

      {/* TOP BAR */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h1>MiniSOC</h1>

            <span>
              Autonomous Network Compromise
              Detection & Response
            </span>
          </div>

        </div>


        <div className="connection">

          <span
            className={`status-dot ${
              connected
                ? "online"
                : "offline"
            }`}
          />

          {connected
            ? "LIVE MONITORING"
            : "CONNECTING"}

        </div>

      </header>


      <main className="dashboard">

        {/* HERO */}

        <section className="hero">

          <div>

            <p className="eyebrow">
              SECURITY OPERATIONS CENTER
            </p>

            <h2>
              Autonomous Network
              <br />
              <span>Defense Agent</span>
            </h2>

            <p className="hero-text">
              Real-time detection,
              investigation and autonomous
              containment of compromised
              internal hosts.
            </p>

          </div>


          {/* ATTACK CONTROLS */}

          <div className="attack-controls">

            <div className="simulation-header">
              <div className="simulation-icon">
                <Zap size={18} />
              </div>

              <div>
                <span className="simulation-label">
                  ATTACK SIMULATION
                </span>

                <small>
                  Controlled security test
                </small>
              </div>
            </div>


            <label className="scenario-label">
              SCENARIO
            </label>


            <select
              className="scenario-select"
              value={attackScenario}
              onChange={(event) =>
                setAttackScenario(event.target.value)
              }
            >
              <option value="SUSPICIOUS_LATERAL_MOVEMENT">
                Lateral Movement
              </option>

              <option value="PORT_SCAN">
                Port Scan
              </option>

              <option value="DATA_EXFILTRATION">
                Data Exfiltration
              </option>
            </select>


            <div className="simulation-buttons">

              <button
                className="attack-button"
                onClick={simulateAttack}
                disabled={loading}
              >
                <Zap size={18} />

                {loading
                  ? "SIMULATING..."
                  : "SIMULATE COMPROMISE"}
              </button>


              <button
                className="reset-button"
                onClick={resetLab}
              >
                ↻ RESET LAB
              </button>

            </div>

          </div>

        </section>


        {/* SINGLE NETWORK TOPOLOGY */}

        <NetworkTopology
          hosts={hosts}
        />


        {/* STATS */}

        <section className="stats-grid">

          <StatCard
            icon={<Server />}
            label="MONITORED HOSTS"
            value={hosts.length}
            detail={`${
              hosts.filter(
                (h) =>
                  h.status === "ONLINE"
              ).length
            } online`}
          />


          <StatCard
            icon={<AlertTriangle />}
            label="ACTIVE INCIDENTS"
            value={
              activeIncidents.length
            }
            detail="requires investigation"
            danger={
              activeIncidents.length > 0
            }
          />


          <StatCard
            icon={<ShieldAlert />}
            label="HIGH RISK EVENTS"
            value={highRisk.length}
            detail="risk score ≥ 70"
            danger={highRisk.length > 0}
          />


          <StatCard
            icon={<Lock />}
            label="CONTAINED"
            value={
              containedIncidents.length
            }
            detail="hosts isolated"
            success={
              containedIncidents.length > 0
            }
          />

        </section>


        {/* INCIDENTS + HOSTS */}

        <section className="content-grid">

          {/* SECURITY INCIDENTS */}

          <div className="panel incident-panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  INCIDENT RESPONSE
                </p>

                <h3>
                  Security Incidents
                </h3>

              </div>

              <ShieldAlert size={22} />

            </div>


            {incidents.length === 0 ? (

              <div className="empty">

                <ShieldCheck size={42} />

                <p>
                  No security incidents
                  detected.
                </p>

                <span>
                  Network operating normally.
                </span>

              </div>

            ) : (

              incidents.map((incident) => (

                <Incident
                  key={incident.id}
                  incident={incident}
                  onIsolate={isolateHost}
                />

              ))

            )}

          </div>


          {/* NETWORK HOSTS */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  ASSET MONITORING
                </p>

                <h3>
                  Network Hosts
                </h3>

              </div>

              <Server size={22} />

            </div>


            <div className="host-list">

              {hosts.map((host) => (

                <div
                  className="host"
                  key={host.id}
                >

                  <div className="host-icon">
                    <Server size={18} />
                  </div>


                  <div className="host-info">

                    <strong>
                      {host.name}
                    </strong>

                    <span>
                      {host.id} · {host.ip}
                    </span>

                  </div>


                  <span
                    className={`host-status ${
                      host.status.toLowerCase()
                    }`}
                  >
                    {host.status}
                  </span>

                </div>

              ))}

            </div>

          </div>

        </section>


        {/* TIMELINE + AGENT */}

        <section className="content-grid">

          {/* INVESTIGATION TIMELINE */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <p className="panel-label">
                  AI SOC AGENT
                </p>

                <h3>
                  Investigation Timeline
                </h3>

              </div>

              <Brain size={22} />

            </div>


            <div className="timeline">

              {events.length === 0 ? (

                <div className="timeline-empty">

                  <Activity size={25} />

                  Waiting for network
                  events...

                </div>

              ) : (

                events.map(
                  (event, index) => (

                    <div
                      className={`timeline-item ${
                        event.type === "AUTONOMOUS_CONTAINMENT" ||
                        event.type === "HOST_ISOLATED"
                          ? "containment-event"
                          : ""
                      }`}
                      key={index}
                    >

                      <div className="timeline-icon">

                        {event.type === "HOST_ISOLATED" ||
                        event.type === "AUTONOMOUS_CONTAINMENT" ? (
                          <Lock size={16} />
                        ) : event.type === "AGENT_INVESTIGATION" ? (
                          <Brain size={16} />
                        ) : event.type === "INCIDENT_DETECTED" ? (
                          <Search size={16} />
                        ) : (
                          <Wifi size={16} />
                        )}

                      </div>


                      <div>

                        <strong>
                          {event.type.replaceAll(
                            "_",
                            " "
                          )}
                        </strong>


                        <p>
                          {event.message ||
                            event.incident
                              ?.agent_reasoning ||
                            event
                              .investigation
                              ?.recommendation ||
                            "Network event received."}
                        </p>


                        {event
                          .investigation
                          ?.findings
                          ?.length > 0 && (

                          <div className="timeline-findings">

                            {event.investigation.findings.map(
                              (
                                finding,
                                findingIndex
                              ) => (

                                <div
                                  key={
                                    findingIndex
                                  }
                                >
                                  ✓ {finding}
                                </div>

                              )
                            )}

                          </div>

                        )}


                        <small>
                          {event.receivedAt}
                        </small>

                      </div>

                    </div>

                  )
                )

              )}

            </div>

          </div>


          {/* AI AGENT */}

          <div className="panel agent-panel">

            <div className="agent-header">

              <div className="agent-avatar">
                <Brain size={27} />
              </div>

              <div>

                <p className="panel-label">
                  AGENT STATUS
                </p>

                <h3>
                  Autonomous Defense Agent
                </h3>

              </div>

            </div>


            <div className="agent-status">

              <span className="pulse" />

              OPERATIONAL

            </div>


            <div className="agent-capabilities">

              <Capability
                text="Continuous network monitoring"
              />

              <Capability
                text="Behavioral anomaly detection"
              />

              <Capability
                text="Incident investigation"
              />

              <Capability
                text="Risk scoring"
              />

              <Capability
                text="Autonomous host containment"
              />

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}


function StatCard({
  icon,
  label,
  value,
  detail,
  danger,
  success,
}) {
  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>


      <div>

        <p>{label}</p>


        <strong
          className={
            danger
              ? "danger-text"
              : success
              ? "success-text"
              : ""
          }
        >
          {value}
        </strong>


        <span>{detail}</span>

      </div>

    </div>
  );
}


function Incident({
  incident,
  onIsolate,
}) {
  const contained =
    incident.status === "CONTAINED";

  return (
    <div
      className={`incident ${
        contained ? "contained" : ""
      }`}
    >

      <div className="incident-top">

        <div>

          <span className="incident-id">
            {incident.id}
          </span>

          <h4>
            {incident.type}
          </h4>

        </div>


        <span
          className={`severity ${
            incident.severity.toLowerCase()
          }`}
        >
          {incident.severity}
        </span>

      </div>


      <div className="risk">

        <div>

          <span>
            RISK SCORE
          </span>

          <strong>
            {incident.risk_score}/100
          </strong>

        </div>


        <div className="risk-bar">

          <div
            style={{
              width: `${incident.risk_score}%`,
            }}
          />

        </div>

      </div>


      <div className="incident-details">

        <div>

          <span>
            AFFECTED HOST
          </span>

          <strong>
            {incident.host_id} ·{" "}
            {incident.host_name}
          </strong>

        </div>


        <div>

          <span>
            AGENT
          </span>

          <strong>
            {incident.agent_status}
          </strong>

        </div>

      </div>


      <p className="reason">

        <strong>
          Detection:
        </strong>{" "}

        {incident.reason}

      </p>


      {incident.agent_findings?.length >
        0 && (

        <div className="agent-findings">

          <div className="agent-findings-title">

            <Brain size={15} />

            SOC AGENT FINDINGS

          </div>


          {incident.agent_findings.map(
            (finding, index) => (

              <div
                className="agent-finding"
                key={index}
              >

                <ShieldCheck size={14} />

                <span>
                  {finding}
                </span>

              </div>

            )
          )}


          {incident.agent_recommendation && (

            <div className="agent-recommendation">

              <span>
                RECOMMENDATION
              </span>

              <strong>
                {incident.agent_recommendation}
              </strong>

            </div>

          )}

        </div>

      )}


      {!contained ? (

        <button
          className="contain-button"
          onClick={() =>
            onIsolate(
              incident.host_id
            )
          }
        >

          <Lock size={16} />

          ISOLATE HOST

        </button>

      ) : (

        <div className="contained-banner">

          <ShieldCheck size={17} />

          HOST CONTAINED

        </div>

      )}

    </div>
  );
}


function Capability({ text }) {
  return (
    <div className="capability">

      <ShieldCheck size={16} />

      {text}

    </div>
  );
}


export default App;