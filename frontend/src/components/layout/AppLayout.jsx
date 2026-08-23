import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  function logout() {
    localStorage.removeItem("wings_access_token");
    localStorage.removeItem("wings_user");
    navigate("/login", { replace: true });
  }
  return (
    <div className="app-shell">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="app-main">
        <Header
          path={location.pathname}
          onMenu={() => setMobileOpen(true)}
          onLogout={logout}
        />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
