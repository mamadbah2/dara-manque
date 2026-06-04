import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const role = await signIn(email, password);
      navigate(role === "doctor" ? "/doctor" : "/pharmacist");
    } catch {
      setError("Email ou mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      display: "flex", justifyContent: "center", alignItems: "center",
      minHeight: "100vh", background: "var(--bg)", padding: 16,
    }}>
      <div style={{ width: "100%", maxWidth: 420 }}>
        <div className="card" style={{ padding: 40 }}>
          {/* Logo */}
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <div style={{
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              width: 56, height: 56, borderRadius: "50%",
              background: "var(--primary-light)", marginBottom: 12,
            }}>
              <span style={{ fontSize: 28, color: "var(--primary)", fontWeight: 700 }}>✚</span>
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--text)" }}>Dara Manqué</h1>
            <p className="text-muted" style={{ marginTop: 4 }}>Portail professionnel</p>
          </div>

          {error && (
            <div className="alert alert-error" style={{ marginBottom: 20 }}>{error}</div>
          )}

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">Email</label>
              <input
                id="email"
                className="input"
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="votre@email.com" required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="password">Mot de passe</label>
              <input
                id="password"
                className="input"
                type="password" value={password} onChange={e => setPassword(e.target.value)}
                placeholder="••••••••" required
              />
            </div>
            <button
              className="btn btn-primary btn-full"
              type="submit" disabled={loading}
              style={{ marginTop: 4, padding: "12px 20px", fontSize: 15 }}
            >
              {loading ? "Connexion..." : "Se connecter"}
            </button>
          </form>

          {/* Hint démo */}
          <div style={{
            marginTop: 28, padding: 12,
            background: "var(--bg)", borderRadius: "var(--radius-sm)",
            fontSize: 12, color: "var(--text-muted)",
          }}>
            <strong style={{ display: "block", marginBottom: 4 }}>Accès démo :</strong>
            <span>Médecin — doctor@dara.com / password123</span><br />
            <span>Pharmacien — pharmacist@dara.com / password123</span>
          </div>
        </div>
      </div>
    </div>
  );
}
