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
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <form onSubmit={handleSubmit} style={{ background: "#fff", padding: 32, borderRadius: 8, width: 360, boxShadow: "0 2px 8px rgba(0,0,0,.1)" }}>
        <h1 style={{ marginBottom: 24, fontSize: 22 }}>Dara Manqué</h1>
        {error && <p style={{ color: "red", marginBottom: 12 }}>{error}</p>}
        <label style={{ display: "block", marginBottom: 4 }}>Email</label>
        <input
          type="email" value={email} onChange={e => setEmail(e.target.value)}
          required style={{ width: "100%", padding: 8, marginBottom: 16, border: "1px solid #ccc", borderRadius: 4 }}
        />
        <label style={{ display: "block", marginBottom: 4 }}>Mot de passe</label>
        <input
          type="password" value={password} onChange={e => setPassword(e.target.value)}
          required style={{ width: "100%", padding: 8, marginBottom: 24, border: "1px solid #ccc", borderRadius: 4 }}
        />
        <button
          type="submit" disabled={loading}
          style={{ width: "100%", padding: 10, background: "#1a73e8", color: "#fff", border: "none", borderRadius: 4, fontSize: 16 }}
        >
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </div>
  );
}
