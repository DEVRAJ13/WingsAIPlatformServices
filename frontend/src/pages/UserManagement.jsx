import { useEffect, useState } from "react";
import { KeyRound, Plus, ShieldCheck, UserCog, UserX } from "lucide-react";
import { createUser, listRoles, listUsers, resetUserPassword, updateUser, updateUserStatus } from "../api/users";
import Badge from "../components/common/Badge";

const emptyForm = {
  name: "",
  email: "",
  temporary_password: "",
  employee_id: "",
  department: "",
  designation: "",
  manager_name: "",
  role: "REQUESTER",
};

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setLoading(true);
    try {
      const [userData, roleData] = await Promise.all([listUsers(), listRoles()]);
      setUsers(userData || []);
      setRoles(roleData || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load user management.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function setField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function startEdit(user) {
    setEditing(user.id);
    setForm({
      name: user.name || "",
      email: user.email || "",
      temporary_password: "",
      employee_id: user.employee_id || "",
      department: user.department || "",
      designation: user.designation || "",
      manager_name: user.manager_name || "",
      role: user.role === "USER" ? "REQUESTER" : user.role,
    });
    setNotice("");
  }

  function resetForm() {
    setEditing(null);
    setForm(emptyForm);
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      if (editing) {
        const payload = {
          name: form.name,
          email: form.email,
          employee_id: form.employee_id || null,
          department: form.department || null,
          designation: form.designation || null,
          manager_name: form.manager_name || null,
          role: form.role,
        };
        await updateUser(editing, payload);
        setNotice("User profile and role updated successfully.");
      } else {
        if (!form.temporary_password) throw new Error("Temporary password is required.");
        await createUser(form);
        setNotice("User created. Share the temporary credentials securely; the user can change the password after login.");
      }
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Unable to save user.");
    } finally {
      setSaving(false);
    }
  }

  async function toggleStatus(user) {
    try {
      await updateUserStatus(user.id, user.status === "ACTIVE" ? "INACTIVE" : "ACTIVE");
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to change user status.");
    }
  }

  async function resetPassword(user) {
    const password = window.prompt(`Temporary password for ${user.name} (minimum 8 characters):`);
    if (!password) return;
    try {
      await resetUserPassword(user.id, password);
      setNotice(`Temporary password reset for ${user.name}. They must change it after login.`);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to reset password.");
    }
  }

  return (
    <div className="page-stack">
      <div className="page-intro">
        <div>
          <div className="eyebrow"><ShieldCheck size={13} /> ADMINISTRATION</div>
          <h1>User Management</h1>
          <p>Create enterprise accounts, assign real IT roles, manage profiles and control access.</p>
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {notice && <div className="success-box">{notice}</div>}

      <div className="two-column-grid">
        <section className="panel">
          <div className="panel-head">
            <div><h2>{editing ? "Edit user" : "Create user"}</h2><p>{editing ? "Update profile or role." : "Create a preset enterprise account."}</p></div>
            {editing ? <button className="secondary-btn" onClick={resetForm}>New user</button> : <Plus size={19} />}
          </div>
          <form className="form-stack" onSubmit={submit}>
            <label>Name<input value={form.name} onChange={(e) => setField("name", e.target.value)} required /></label>
            <label>Email<input type="email" value={form.email} onChange={(e) => setField("email", e.target.value)} required /></label>
            {!editing && <label>Temporary password<input type="password" value={form.temporary_password} onChange={(e) => setField("temporary_password", e.target.value)} minLength={8} required /></label>}
            <label>Employee ID<input value={form.employee_id} onChange={(e) => setField("employee_id", e.target.value)} /></label>
            <label>Department<input value={form.department} onChange={(e) => setField("department", e.target.value)} /></label>
            <label>Designation<input value={form.designation} onChange={(e) => setField("designation", e.target.value)} /></label>
            <label>Manager<input value={form.manager_name} onChange={(e) => setField("manager_name", e.target.value)} /></label>
            <label>Role<select value={form.role} onChange={(e) => setField("role", e.target.value)}>{roles.map((role) => <option key={role.key} value={role.key}>{role.title}</option>)}</select></label>
            <button className="primary-btn" disabled={saving}>{saving ? "Saving..." : editing ? "Save changes" : "Create user"}</button>
          </form>
        </section>

        <section className="panel table-panel">
          <div className="panel-head"><div><h2>Enterprise users</h2><p>{users.length} configured account{users.length === 1 ? "" : "s"}</p></div><UserCog size={19} /></div>
          {loading ? <p>Loading users...</p> : users.length === 0 ? <p>No users found.</p> : (
            <div className="table-list">
              {users.map((user) => (
                <div className="table-row" key={user.id}>
                  <div><strong>{user.name}</strong><span>{user.email} · {user.designation || "Employee"}</span></div>
                  <Badge tone={user.status === "ACTIVE" ? "success" : "danger"}>{user.role === "USER" ? "REQUESTER" : user.role}</Badge>
                  <div className="row-actions">
                    <button className="icon-btn" title="Edit" onClick={() => startEdit(user)}><UserCog size={15} /></button>
                    <button className="icon-btn" title="Reset password" onClick={() => resetPassword(user)}><KeyRound size={15} /></button>
                    <button className="icon-btn" title="Activate / disable" onClick={() => toggleStatus(user)}><UserX size={15} /></button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
