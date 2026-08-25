import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Settings as SettingsIcon, Server, ShieldCheck, Cpu, KeyRound } from "lucide-react";
import { changePassword } from "../api/auth";

function Status({ children }) { return <small className="setting-status"><i /> {children}</small>; }

export default function Settings() {
  const user = JSON.parse(localStorage.getItem("wings_user") || "null");
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (searchParams.get("changePassword") === "1") {
      setMessage("Password change is required before you can continue.");
    }
  }, [searchParams]);

  async function submit(e) {
    e.preventDefault(); setError(""); setMessage("");
    if (newPassword !== confirmPassword) { setError("New passwords do not match."); return; }
    setSaving(true);
    try {
      const updated = await changePassword(currentPassword, newPassword);
      const nextUser = { ...user, ...updated, must_change_password: false };
      localStorage.setItem("wings_user", JSON.stringify(nextUser));
      setCurrentPassword(""); setNewPassword(""); setConfirmPassword("");
      setMessage("Password changed successfully. Please sign in again.");
      setTimeout(() => {
        localStorage.removeItem("wings_access_token");
        localStorage.removeItem("wings_user");
        navigate("/login", { replace: true });
      }, 900);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to change password.");
    } finally { setSaving(false); }
  }

  return (
    <div className="page-stack">
      <div className="page-intro"><div><div className="eyebrow"><SettingsIcon size={13} /> CONFIGURATION</div><h1>Settings</h1><p>Review platform configuration and manage your account.</p></div></div>
      {user?.must_change_password && <div className="warning-box">Your account was created with a temporary password. Change it now to secure your account.</div>}
      {error && <div className="error-box">{error}</div>}
      {message && <div className="success-box">{message}</div>}
      <div className="settings-grid">
        <div className="panel setting-card"><Server size={20} /><h3>Backend API</h3><span>{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}</span><Status>Connected</Status></div>
        <div className="panel setting-card"><Cpu size={20} /><h3>AI Engine</h3><span>Ollama · Qwen 2.5 1.5B</span><Status>Online</Status></div>
        <div className="panel setting-card"><ShieldCheck size={20} /><h3>Account</h3><span>{user?.name || user?.email} · {user?.role || "REQUESTER"}</span><Status>{user?.status || "ACTIVE"}</Status></div>
      </div>
      <div className="panel setting-card" style={{maxWidth: 620}}>
        <KeyRound size={20} /><h3>Change password</h3><span>Use your current password to set a new password. Minimum 8 characters.</span>
        <form className="form-stack" onSubmit={submit}>
          <label>Current password<input type="password" value={currentPassword} onChange={(e)=>setCurrentPassword(e.target.value)} required /></label>
          <label>New password<input type="password" value={newPassword} onChange={(e)=>setNewPassword(e.target.value)} minLength={8} required /></label>
          <label>Confirm new password<input type="password" value={confirmPassword} onChange={(e)=>setConfirmPassword(e.target.value)} minLength={8} required /></label>
          <button className="primary-btn" disabled={saving}>{saving ? "Changing..." : "Change password"}</button>
        </form>
      </div>
    </div>
  );
}
