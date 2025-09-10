// frontend/src/components/PingButton.jsx
import { useState } from "react";
import { pingBackend } from "../api";

export default function PingButton() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const onPing = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await pingBackend(); // ожидаем { status: "ok" } или подобное
      setResult(data);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: 8, alignItems: "start" }}>
      <button onClick={onPing} disabled={loading} style={{ padding: "8px 14px" }}>
        {loading ? "Pinging..." : "Ping API"}
      </button>
      {error && <pre style={{ color: "crimson", whiteSpace: "pre-wrap" }}>{error}</pre>}
      {result && (
        <pre style={{ background: "#f5f5f5", padding: 8, borderRadius: 6 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
