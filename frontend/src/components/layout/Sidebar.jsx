import { NavLink } from "react-router-dom";
import {
  Activity,
  Bot,
  BookOpen,
  CheckCircle2,
  FileText,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  X,
  ChevronRight,
  Users,
  BarChart3,
} from "lucide-react";
const items = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/ai", "AI Console", Bot],
  ["/incidents", "Incidents", Activity],
  ["/approvals", "Approvals", CheckCircle2],
  ["/knowledge", "Knowledge", BookOpen],
  ["/documents", "Documents", FileText],
];
export default function Sidebar({ mobileOpen, onClose }) {
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  const role = String(user?.role || "REQUESTER").toUpperCase();
  const canManageUsers = role === "PLATFORM_ADMIN" || role === "ADMIN";
  const canMonitor = ["PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR"].includes(role);
  return (
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      <div className="brand">
        <div className="brand-mark">
          <ShieldCheck size={22} />
        </div>
        <div>
          <strong>WINGS AI</strong>
          <span>Operations Platform</span>
        </div>
        <button className="mobile-close" onClick={onClose}>
          <X size={19} />
        </button>
      </div>
      <div className="sidebar-section">Workspace</div>
      <nav>
        {items.map(([to, label, Icon]) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <Icon size={18} />
            <span>{label}</span>
            <ChevronRight size={14} className="nav-chevron" />
          </NavLink>
        ))}
      </nav>
      {canManageUsers && (
        <>
          <div className="sidebar-section">Administration</div>
          <NavLink to="/admin/users" onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            <Users size={18} />
            <span>User Management</span>
            <ChevronRight size={14} className="nav-chevron" />
          </NavLink>
        </>
      )}
      {canMonitor && (
        <>
          <div className="sidebar-section">Observability</div>
          <NavLink to="/monitoring" onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            <BarChart3 size={18} />
            <span>Monitoring</span>
            <ChevronRight size={14} className="nav-chevron" />
          </NavLink>
        </>
      )}
      <div className="sidebar-spacer" />
      <div className="sidebar-section">System</div>
      <NavLink
        to="/settings"
        onClick={onClose}
        className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
      >
        <Settings size={18} />
        <span>Settings</span>
        <ChevronRight size={14} className="nav-chevron" />
      </NavLink>
      <div className="sidebar-status">
        <span className="status-dot" />
        <div>
          <strong>Platform online</strong>
          <small>Core services connected</small>
        </div>
      </div>
    </aside>
  );
}
