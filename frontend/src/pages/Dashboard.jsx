import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  FileText,
  ArrowUpRight,
  ShieldCheck,
  Loader2,
} from "lucide-react";
import { Link } from "react-router-dom";
import StatCard from "../components/common/StatCard";
import Badge from "../components/common/Badge";
import { listIncidents } from "../api/incidents";
import { listApprovals } from "../api/approvals";
export default function Dashboard() {
  const [incidents, setIncidents] = useState([]),
    [approvals, setApprovals] = useState([]),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    (async () => {
      try {
        const [i, a] = await Promise.all([listIncidents(), listApprovals()]);
        setIncidents(Array.isArray(i) ? i : i.incidents || []);
        setApprovals(Array.isArray(a) ? a : a.approvals || []);
      } finally {
        setLoading(false);
      }
    })();
  }, []);
  const open = incidents.filter((x) => x.status !== "RESOLVED").length;
  const pending = approvals.filter((x) => x.status === "PENDING").length;
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <div className="eyebrow">
            <span className="pulse" /> PLATFORM READY
          </div>
          <h1>Good evening, DevRaj.</h1>
          <p>
            Use WINGS AI to understand incidents, search enterprise knowledge,
            and safely execute approved operational actions.
          </p>
          <Link to="/ai" className="primary-btn">
            <Bot size={17} /> Open AI Console
          </Link>
        </div>
        <div className="hero-orbit">
          <div className="orbit-core">
            <ShieldCheck size={32} />
          </div>
          <div className="orbit-ring r1" />
          <div className="orbit-ring r2" />
        </div>
      </section>
      <section className="stats-grid">
        <StatCard
          icon={Activity}
          label="Open incidents"
          value={loading ? <Loader2 className="spin" /> : open}
          detail="Live from backend"
          tone="blue"
        />
        <StatCard
          icon={CheckCircle2}
          label="Pending approvals"
          value={loading ? <Loader2 className="spin" /> : pending}
          detail="Requires attention"
          tone="amber"
        />
        <StatCard
          icon={FileText}
          label="Knowledge docs"
          value="Indexed"
          detail="pgvector knowledge base"
          tone="purple"
        />
        <StatCard
          icon={Bot}
          label="AI status"
          value="Online"
          detail="Backend AI endpoint"
          tone="green"
        />
      </section>
      <section className="two-column">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Recent incidents</h2>
              <p>Latest operational events</p>
            </div>
            <Link to="/incidents">
              View all <ArrowUpRight size={15} />
            </Link>
          </div>
          <div className="table-list">
            {incidents.slice(0, 5).map((x) => (
              <div className="list-row" key={x.id}>
                <div className="row-main">
                  <strong>INC-{x.id}</strong>
                  <span>{x.title}</span>
                </div>
                <Badge tone={(x.priority || "medium").toLowerCase()}>
                  {x.priority || "MEDIUM"}
                </Badge>
                <time>
                  {x.created_at ? new Date(x.created_at).toLocaleString() : "-"}
                </time>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Approval queue</h2>
              <p>Human-in-the-loop actions</p>
            </div>
            <Link to="/approvals">
              Open <ArrowUpRight size={15} />
            </Link>
          </div>
          <div className="approval-preview">
            {approvals.slice(0, 4).map((x) => (
              <div className="approval-item" key={x.id}>
                <div className="approval-icon">
                  <CheckCircle2 size={17} />
                </div>
                <div>
                  <strong>{x.tool_name}</strong>
                  <span>{x.reason}</span>
                </div>
                <Badge
                  tone={
                    x.status === "APPROVED" || x.status === "EXECUTED"
                      ? "success"
                      : "pending"
                  }
                >
                  {x.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
