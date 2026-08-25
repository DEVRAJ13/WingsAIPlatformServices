import { Bell, Menu, Search } from "lucide-react";
const titles = {
  "/dashboard": ["Dashboard", "AI operations overview"],
  "/ai": ["AI Console", "Ask WINGS and investigate operational knowledge"],
  "/incidents": ["Incidents", "Monitor and investigate service incidents"],
  "/approvals": ["Approval Center", "Human-in-the-loop operational actions"],
  "/knowledge": ["Knowledge", "Search the WINGS knowledge base"],
  "/documents": ["Documents", "Manage enterprise knowledge"],
  "/settings": ["Settings", "Platform preferences and account"],
  "/admin/users": ["User Management", "Enterprise accounts, roles and access"],
};
export default function Header({ path, onMenu, onLogout }) {
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  const [title, subtitle] = titles[path] || [
    "WINGS AI",
    "Enterprise AI operations",
  ];
  return (
    <header className="topbar">
      <button className="mobile-menu" onClick={onMenu}>
        <Menu size={21} />
      </button>
      <div>
        <div className="topbar-title">{title}</div>
        <div className="topbar-subtitle">{subtitle}</div>
      </div>
      <div className="topbar-actions">
        <button className="icon-btn">
          <Search size={18} />
        </button>
        <button className="icon-btn notification">
          <Bell size={18} />
          <i />
        </button>
        <button className="user-menu" onClick={onLogout}>
          <span className="avatar">DT</span>
          <span className="user-copy">
            <strong>{user?.name || user?.email || "WINGS User"}</strong>
            <small>{user?.role || "REQUESTER"}</small>
          </span>
        </button>
      </div>
    </header>
  );
}
