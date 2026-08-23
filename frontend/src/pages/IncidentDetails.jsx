import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Bot, Ticket, Loader2 } from "lucide-react";
import Badge from "../components/common/Badge";
import { getIncident } from "../api/incidents";
import { diagnoseIncident } from "../api/agent";
import { createAIApproval } from "../api/approvals";

export default function IncidentDetails() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null),
    [diagnosis, setDiagnosis] = useState(null),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    (async () => {
      try {
        setIncident(await getIncident(id));
      } catch (err) {
        setError(err.response?.data?.detail || "Unable to load incident.");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);
  async function diagnose() {
    setBusy(true);
    setError("");
    try {
      const data = await diagnoseIncident(id);
      setDiagnosis(data);
    } catch (err) {
      setError(err.response?.data?.detail || "AI diagnosis failed.");
    } finally {
      setBusy(false);
    }
  }
  async function requestTicket() {
    if (!incident) return;
    setBusy(true);
    try {
      await createAIApproval({
        tool_name: "create_itsm_ticket",
        reason: `AI-assisted escalation for incident ${incident.id}.`,
        parameters: {
          title: `INC-${incident.id} · ${incident.title}`,
          description: incident.description,
          priority: incident.priority || incident.severity || "Medium",
        },
      });
      alert("Approval request created.");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create approval.");
    } finally {
      setBusy(false);
    }
  }
  if (loading)
    return (
      <div className="page-stack">
        <div className="panel empty-mini">
          <Loader2 className="spin" size={24} />
          <span>Loading incident...</span>
        </div>
      </div>
    );
  if (!incident)
    return (
      <div className="page-stack">
        <div className="error-box">{error || "Incident not found."}</div>
      </div>
    );
  return (
    <div className="page-stack">
      <Link to="/incidents" className="back-link">
        <ArrowLeft size={16} /> Back to incidents
      </Link>
      <div className="detail-header panel">
        <div>
          <Badge
            tone={(
              incident.priority ||
              incident.severity ||
              "medium"
            ).toLowerCase()}
          >
            {String(
              incident.priority || incident.severity || "MEDIUM",
            ).toUpperCase()}
          </Badge>
          <h1>
            INC-{incident.id} · {incident.title}
          </h1>
          <p>
            {incident.service_name} · {incident.environment} · Created{" "}
            {incident.created_at
              ? new Date(incident.created_at).toLocaleString()
              : "-"}
          </p>
        </div>
        <button className="primary-btn" onClick={diagnose} disabled={busy}>
          {busy ? <Loader2 className="spin" size={17} /> : <Bot size={17} />}{" "}
          Diagnose with AI
        </button>
      </div>
      {error && <div className="error-box">{error}</div>}
      <div className="two-column">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Incident details</h2>
              <p>Current operational context</p>
            </div>
          </div>
          <div className="detail-grid">
            <div>
              <span>Service</span>
              <strong>{incident.service_name}</strong>
            </div>
            <div>
              <span>Environment</span>
              <strong>{incident.environment}</strong>
            </div>
            <div>
              <span>Status</span>
              <Badge tone="info">{incident.status}</Badge>
            </div>
            <div>
              <span>Severity</span>
              <Badge
                tone={(
                  incident.priority ||
                  incident.severity ||
                  "medium"
                ).toLowerCase()}
              >
                {incident.priority || incident.severity || "MEDIUM"}
              </Badge>
            </div>
          </div>
          <div className="description-box">
            <span>Description</span>
            <p>{incident.description}</p>
          </div>
        </div>
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>AI diagnosis</h2>
              <p>Generated after investigation</p>
            </div>
          </div>
          {diagnosis ? (
            <div className="description-box">
              <p>{diagnosis.answer}</p>
              {diagnosis.diagnosis && (
                <small>
                  Incident data retrieved for INC-{diagnosis.diagnosis.id}.
                </small>
              )}
            </div>
          ) : (
            <div className="empty-mini">
              <Bot size={24} />
              <strong>No diagnosis yet</strong>
              <span>Run AI diagnosis to investigate this incident.</span>
            </div>
          )}
        </div>
      </div>
      <div className="panel">
        <div className="panel-head">
          <div>
            <h2>Recommended actions</h2>
            <p>Actions remain subject to human approval</p>
          </div>
        </div>
        <div className="recommendation">
          <div className="rec-icon">
            <Ticket size={18} />
          </div>
          <div>
            <strong>Create ITSM ticket</strong>
            <span>Escalate the incident for operational investigation.</span>
          </div>
          <button
            className="secondary-btn"
            onClick={requestTicket}
            disabled={busy}
          >
            Request approval
          </button>
        </div>
      </div>
    </div>
  );
}
