import type { ReactNode } from "react";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

interface Props {
  role: "doctor" | "pharmacist";
  children: ReactNode;
}

export default function AppShell({ role, children }: Props) {
  const { signOut } = useAuth();
  const navigate = useNavigate();

  function handleSignOut() {
    signOut();
    navigate("/login");
  }

  const roleLabel = role === "doctor" ? "Médecin" : "Pharmacien";
  const email = localStorage.getItem("email") ?? "";

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <header style={{
        position: "sticky", top: 0, zIndex: 10,
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        boxShadow: "var(--shadow-sm)",
        padding: "0 24px",
        height: 60,
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div className="flex items-center gap-2">
          <span style={{ fontSize: 20, color: "var(--primary)", fontWeight: 700 }}>✚</span>
          <span style={{ fontWeight: 700, fontSize: 16, color: "var(--text)" }}>Dara Manqué</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="badge badge-info">{roleLabel}</span>
          {email && <span className="text-muted" style={{ fontSize: 13 }}>{email}</span>}
          <button className="btn btn-ghost btn-sm" onClick={handleSignOut}>
            Déconnexion
          </button>
        </div>
      </header>
      <main style={{ maxWidth: 900, margin: "0 auto", padding: "32px 24px" }}>
        {children}
      </main>
    </div>
  );
}
