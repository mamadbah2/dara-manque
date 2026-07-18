import { useEffect, useRef, useState } from "react";
import { getLastScan } from "../api/client";

interface Props {
  /** Called when a scanned card resolves to an existing patient. */
  onKnown: (patientId: number) => void;
  /** Called when a scanned card is not associated with any patient yet. */
  onUnknown: (uid: string) => void;
}

/**
 * "Reader station" panel. Polls the backend for the last card scanned on the
 * hardware reader (ESP32). On a new scan it hands off to the parent: a known
 * card opens the patient record, an unknown card opens enrollment.
 *
 * The first poll only sets a baseline `seq` so a scan that happened before the
 * screen opened is never replayed.
 */
export default function CardStation({ onKnown, onUnknown }: Props) {
  const lastSeq = useRef<number | null>(null);
  const onKnownRef = useRef(onKnown);
  const onUnknownRef = useRef(onUnknown);
  onKnownRef.current = onKnown;
  onUnknownRef.current = onUnknown;

  const [online, setOnline] = useState(true);

  useEffect(() => {
    let active = true;

    async function poll() {
      try {
        const { data } = await getLastScan();
        if (!active) return;
        setOnline(true);
        if (lastSeq.current === null) {
          lastSeq.current = data.seq; // baseline — ignore prior scans
          return;
        }
        if (data.seq > lastSeq.current) {
          lastSeq.current = data.seq;
          if (data.known && data.patient) onKnownRef.current(data.patient.id);
          else if (data.uid) onUnknownRef.current(data.uid);
        }
      } catch {
        if (active) setOnline(false);
      }
    }

    poll();
    const timer = setInterval(poll, 1200);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <div
      className="card"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 18,
        borderColor: "var(--primary)",
        background: "var(--primary-light)",
      }}
    >
      <span className="card-station-pulse" aria-hidden style={{ fontSize: 30 }}>
        📇
      </span>
      <div style={{ flex: 1 }}>
        <h2 style={{ fontSize: 17, fontWeight: 600 }}>
          {online ? "En attente de carte…" : "Lecteur hors ligne"}
        </h2>
        <p className="text-muted" style={{ marginTop: 4 }}>
          {online
            ? "Posez une carte patient sur le lecteur pour ouvrir son dossier."
            : "Impossible de joindre le serveur. Nouvelle tentative en cours…"}
        </p>
      </div>
      <span
        style={{
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: online ? "#16A34A" : "#DC2626",
          boxShadow: online ? "0 0 0 4px rgba(22,163,74,0.15)" : "none",
        }}
      />
      <style>{`
        .card-station-pulse { animation: cardStationPulse 1.6s ease-in-out infinite; }
        @keyframes cardStationPulse {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.12); }
        }
      `}</style>
    </div>
  );
}
