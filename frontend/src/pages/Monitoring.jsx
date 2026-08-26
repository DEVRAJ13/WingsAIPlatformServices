import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  Clock3,
  Database,
  Eye,
  Gauge,
  RefreshCw,
  Server,
  ShieldCheck,
  Ticket,
  Workflow,
  XCircle,
  Zap,
} from "lucide-react";

import Badge from "../components/common/Badge";
import {
  getMonitoringAgents,
  getMonitoringHealth,
  getMonitoringOverview,
  getWorkflowDetail,
  listWorkflowRuns,
} from "../api/monitoring";

function formatNumber(value) {
  return new Intl.NumberFormat().format(Number(value || 0));
}

function formatMs(value) {
  return `${Number(value || 0).toFixed(0)} ms`;
}

function statusTone(status) {
  if (["HEALTHY", "COMPLETED", "SUCCESS", "APPROVED"].includes(status)) return "success";
  if (["FAILED", "ERROR", "TIMEOUT", "REJECTED", "DOWN"].includes(status)) return "danger";
  if (["WAITING_FOR_APPROVAL", "RUNNING", "PENDING"].includes(status)) return "pending";
  return "info";
}

export default function Monitoring() {
  const [overview, setOverview] = useState(null);
  const [health, setHealth] = useState([]);
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [overviewData, healthData, agentData, workflowData] = await Promise.all([
        getMonitoringOverview(),
        getMonitoringHealth(),
        getMonitoringAgents(),
        listWorkflowRuns(50),
      ]);
      setOverview(overviewData);
      setHealth(healthData.services || []);
      setAgents(agentData.agents || []);
      setWorkflows(workflowData.workflows || []);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load monitoring data.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 15000);
    return () => window.clearInterval(timer);
  }, []);

  async function openWorkflow(workflowId) {
    setDetailLoading(true);
    try {
      setSelected(await getWorkflowDetail(workflowId));
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load workflow details.",
      );
    } finally {
      setDetailLoading(false);
    }
  }

  const llm = overview?.llm || {};
  const run = overview?.workflows || {};

  return (
    <div className="page-stack">
      <div className="page-intro monitoring-header">
        <div>
          <div className="eyebrow">
            <Activity size={13} /> PLATFORM OBSERVABILITY
          </div>
          <h1>Monitoring</h1>
          <p>
            Platform health, agentic workflows, LLM usage and operational telemetry.
          </p>
        </div>

        <button className="secondary-btn" onClick={load} disabled={loading}>
          <RefreshCw size={14} className={loading ? "spin" : ""} />
          Refresh
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      <section className="stats-grid">
        <MetricCard icon={Workflow} label="Agent workflows" value={formatNumber(run.total)} detail={`${formatNumber(run.completed)} completed`} />
        <MetricCard icon={Zap} label="Workflow success" value={`${run.success_rate || 0}%`} detail={`${formatNumber(run.failed)} failed`} />
        <MetricCard icon={Bot} label="LLM requests" value={formatNumber(llm.requests)} detail={`${formatNumber(llm.total_tokens)} total tokens`} />
        <MetricCard icon={Clock3} label="Average LLM latency" value={formatMs(llm.avg_latency_ms)} detail={`${formatNumber(run.running)} running`} />
      </section>

      <div className="monitoring-grid">
        <section className="panel monitoring-panel">
          <div className="panel-head">
            <div>
              <h2>Service health</h2>
              <p>Backend connectivity and integration status</p>
            </div>
            <Server size={18} />
          </div>

          <div className="health-grid">
            {health.map((service) => (
              <div className="health-card" key={service.name}>
                <div className="health-icon">
                  {service.name === "PostgreSQL" ? <Database size={17} /> :
                   service.name === "Ollama" ? <Bot size={17} /> :
                   service.name === "Jira" || service.name === "ServiceNow" ? <Ticket size={17} /> :
                   <Server size={17} />}
                </div>
                <div>
                  <strong>{service.name}</strong>
                  <span>{service.message || "Service check completed"}</span>
                </div>
                <div className="health-meta">
                  <Badge tone={statusTone(service.status)}>{service.status}</Badge>
                  {service.latency_ms != null && <small>{formatMs(service.latency_ms)}</small>}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel monitoring-panel">
          <div className="panel-head">
            <div>
              <h2>AI usage</h2>
              <p>Tracked across agent workflow LLM calls</p>
            </div>
            <Gauge size={18} />
          </div>

          <div className="usage-summary">
            <Usage label="Input tokens" value={formatNumber(llm.input_tokens)} />
            <Usage label="Output tokens" value={formatNumber(llm.output_tokens)} />
            <Usage label="Total tokens" value={formatNumber(llm.total_tokens)} />
            <Usage label="Agent runs" value={formatNumber(run.total)} />
          </div>
        </section>
      </div>

      <section className="panel monitoring-panel">
        <div className="panel-head">
          <div>
            <h2>Agent health</h2>
            <p>Agent calls, token consumption and average latency</p>
          </div>
          <Bot size={18} />
        </div>

        <div className="agent-health-list">
          {agents.map((agent) => (
            <div className="agent-health-row" key={agent.agent_name}>
              <div className="agent-name">
                <span className="status-dot" />
                <div>
                  <strong>{agent.agent_name}</strong>
                  <small>{agent.requests} request(s)</small>
                </div>
              </div>
              <span>{formatNumber(agent.total_tokens)} tokens</span>
              <span>{formatMs(agent.avg_latency_ms)}</span>
              <Badge tone="success">{agent.status}</Badge>
            </div>
          ))}
        </div>
      </section>

      <section className="panel monitoring-panel">
        <div className="panel-head">
          <div>
            <h2>Agent workflow runs</h2>
            <p>Actual LangGraph execution history</p>
          </div>
          <Workflow size={18} />
        </div>

        {workflows.length === 0 ? (
          <div className="empty-mini">
            <Workflow size={25} />
            <strong>No workflows recorded yet</strong>
            <span>Run a request through the AI Console to see the graph here.</span>
          </div>
        ) : (
          <div className="workflow-list">
            {workflows.map((workflow) => (
              <button
                className="workflow-row"
                key={workflow.workflow_id}
                onClick={() => openWorkflow(workflow.workflow_id)}
              >
                <div className="workflow-main">
                  <strong>{workflow.workflow_id}</strong>
                  <span>{workflow.question}</span>
                </div>
                <Badge tone={statusTone(workflow.status)}>{workflow.status}</Badge>
                <span className="workflow-node">{workflow.current_node || workflow.intent || "-"}</span>
                <Eye size={16} />
              </button>
            ))}
          </div>
        )}
      </section>

      {selected && (
        <section className="panel monitoring-panel workflow-detail">
          <div className="panel-head">
            <div>
              <h2>{selected.workflow_id}</h2>
              <p>{selected.question}</p>
            </div>
            <button className="secondary-btn" onClick={() => setSelected(null)}>Close</button>
          </div>

          {detailLoading ? (
            <div className="empty-mini"><RefreshCw size={22} className="spin" /><span>Loading workflow...</span></div>
          ) : (
            <>
              <div className="workflow-detail-summary">
                <Badge tone={statusTone(selected.status)}>{selected.status}</Badge>
                <span>{selected.intent || "unknown intent"}</span>
                <span>{selected.duration_ms ? formatMs(selected.duration_ms) : "Running"}</span>
              </div>

              <div className="workflow-trace">
                {selected.steps?.map((step, index) => (
                  <div className="trace-step" key={step.id}>
                    <div className={`trace-marker ${step.status === "SUCCESS" ? "trace-success" : step.status === "FAILED" ? "trace-failed" : "trace-running"}`}>
                      {step.status === "SUCCESS" ? <CheckCircle2 size={14} /> : step.status === "FAILED" ? <XCircle size={14} /> : <Clock3 size={14} />}
                    </div>
                    <div className="trace-content">
                      <div className="trace-title">
                        <strong>{step.node_name}</strong>
                        <Badge tone={statusTone(step.status)}>{step.status}</Badge>
                      </div>
                      <span>{step.duration_ms != null ? formatMs(step.duration_ms) : "Running"}</span>
                      {step.error && <small className="trace-error">{step.error}</small>}
                    </div>
                    {index < (selected.steps?.length || 0) - 1 && <div className="trace-line" />}
                  </div>
                ))}
              </div>

              <div className="workflow-usage">
                <h3>LLM usage</h3>
                {selected.llm_usage?.length ? selected.llm_usage.map((u, index) => (
                  <div className="usage-row" key={`${u.agent_name}-${index}`}>
                    <strong>{u.agent_name || "unknown agent"}</strong>
                    <span>{formatNumber(u.input_tokens)} in</span>
                    <span>{formatNumber(u.output_tokens)} out</span>
                    <span>{formatNumber(u.total_tokens)} total</span>
                    <span>{formatMs(u.latency_ms)}</span>
                  </div>
                )) : <div className="empty-mini"><span>No LLM usage recorded for this workflow.</span></div>}
              </div>
            </>
          )}
        </section>
      )}
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="stat-icon"><Icon size={20} /></div>
      <div className="stat-copy"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>
    </div>
  );
}

function Usage({ label, value }) {
  return (
    <div className="usage-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
