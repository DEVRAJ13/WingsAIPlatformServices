import { Navigate, Route, Routes } from "react-router-dom";
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
function Protected({ children }) {
  return localStorage.getItem("wings_access_token") ? (
    children
  ) : (
    <Navigate to="/login" replace />
  );
}
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <AppLayout />
          </Protected>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="ai" element={<AIConsole />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="incidents/:id" element={<IncidentDetails />} />
        <Route path="approvals" element={<Approvals />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="documents" element={<Documents />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
