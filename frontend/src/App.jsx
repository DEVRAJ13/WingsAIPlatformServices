import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import AIConsole from "./pages/AIConsole";
import Incidents from "./pages/Incidents";
import IncidentDetails from "./pages/IncidentDetails";
import Approvals from "./pages/Approvals";
import Knowledge from "./pages/Knowledge";
import Documents from "./pages/Documents";
import Settings from "./pages/Settings";
import UserManagement from "./pages/UserManagement";
import Monitoring from "./pages/Monitoring";

function Protected({ children }) {
  return localStorage.getItem("wings_access_token") ? children : <Navigate to="/login" replace />;
}

function PasswordGate({ children }) {
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  if (user?.must_change_password && location.pathname !== "/settings") {
    return <Navigate to="/settings?changePassword=1" replace />;
  }
  return children;
}

function MonitoringAccess({ children }) {
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  const role = String(user?.role || "REQUESTER").toUpperCase();
  const allowed = ["PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR"];
  return allowed.includes(role) ? children : <Navigate to="/dashboard" replace />;
}

function AdminOnly({ children }) {
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  const role = String(user?.role || "REQUESTER").toUpperCase();
  return role === "PLATFORM_ADMIN" || role === "ADMIN" ? children : <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><PasswordGate><AppLayout /></PasswordGate></Protected>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="ai" element={<AIConsole />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="incidents/:id" element={<IncidentDetails />} />
        <Route path="approvals" element={<Approvals />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="documents" element={<Documents />} />
        <Route path="settings" element={<Settings />} />
        <Route path="admin/users" element={<AdminOnly><UserManagement /></AdminOnly>} />
        <Route path="monitoring" element={<MonitoringAccess><Monitoring /></MonitoringAccess>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
