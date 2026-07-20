import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import AppShell from "../../components/AppShell";
import { useAuth } from "../../hooks/useAuth";
import { getAffluence, getFraud } from "../../api/client";
import type { AffluenceResponse, FraudResponse } from "../../api/types";

export default function AnalyticsPage() {
  const { role } = useAuth();
  const navigate = useNavigate();
  const [affluence, setAffluence] = useState<AffluenceResponse | null>(null);
  const [fraud, setFraud] = useState<FraudResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([getAffluence(), getFraud()])
      .then(([a, f]) => {
        setAffluence(a.data);
        setFraud(f.data);
      })
      .catch(() => setError(true));
  }, []);

  // Fusionne historique + prévision pour un seul graphique continu
  const chartData = affluence
    ? [
        ...affluence.history.map((h) => ({ date: h.date, Historique: h.patients })),
        ...affluence.forecast.map((f) => ({ date: f.date, Prévision: f.predicted_patients })),
      ]
    : [];

  return (
    <AppShell role={role ?? "doctor"}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700 }}>🤖 Analytics IA</h1>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/${role}`)}>
          ← Retour
        </button>
      </div>
      <p className="badge badge-info" style={{ marginBottom: 24 }}>
        Données de démonstration
      </p>

      {error && (
        <div className="card" style={{ color: "var(--danger, #c0392b)" }}>
          Module IA indisponible. Vérifiez que le backend tourne sur le port 9000.
        </div>
      )}

      {/* --- Section Affluence --- */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>
          Prévision d'affluence (30 jours)
        </h2>
        {affluence && (
          <>
            <div style={{ display: "flex", gap: 24, margin: "12px 0" }}>
              <div><strong style={{ fontSize: 24 }}>{affluence.kpis.peak}</strong><br /><span className="text-muted">Pic prévu ({affluence.kpis.peak_date})</span></div>
              <div><strong style={{ fontSize: 24 }}>{affluence.kpis.average}</strong><br /><span className="text-muted">Moyenne / jour</span></div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="Historique" stroke="#2563eb" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="Prévision" stroke="#f59e0b" dot={false} strokeWidth={2} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </>
        )}
      </div>

      {/* --- Section Fraude --- */}
      <div className="card">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>
          Détection de nomadisme médical
        </h2>
        {fraud && (
          <>
            <p className="text-muted" style={{ marginBottom: 12 }}>
              <strong style={{ color: "var(--danger, #c0392b)" }}>{fraud.total}</strong> patients au comportement atypique — {fraud.suspects.length} plus suspects ci-dessous.
            </p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                <thead>
                  <tr style={{ textAlign: "left", borderBottom: "1px solid var(--border)" }}>
                    <th style={{ padding: 8 }}>Patient</th>
                    <th style={{ padding: 8 }}>Visites</th>
                    <th style={{ padding: 8 }}>Médecins</th>
                    <th style={{ padding: 8 }}>Hôpitaux</th>
                    <th style={{ padding: 8 }}>Médicaments</th>
                    <th style={{ padding: 8 }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {fraud.suspects.map((s, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                      <td style={{ padding: 8 }}>{s.patient}</td>
                      <td style={{ padding: 8 }}>{s.visites}</td>
                      <td style={{ padding: 8 }}>{s.medecins_distincts}</td>
                      <td style={{ padding: 8 }}>{s.hopitaux_distincts}</td>
                      <td style={{ padding: 8 }}>{s.medicaments_distincts}</td>
                      <td style={{ padding: 8 }}>
                        <span className="badge" style={{ background: s.score < -0.1 ? "#c0392b" : "#f59e0b", color: "white" }}>
                          {s.score.toFixed(3)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
