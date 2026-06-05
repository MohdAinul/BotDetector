import { useDashboard } from "./hooks/useDashboard";
import StatCards from "./components/StatCards";
import ThreatFeed from "./components/ThreatFeed";
import ScoreGauge from "./components/ScoreGauge";
import LiveChecker from "./components/LiveChecker";

export default function App() {
  const { stats, feed, loading } = useDashboard();

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "24px 20px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "28px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              background: "#3b82f6",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
            }}
          >
            🛡️
          </div>
          <div>
            <h1
              style={{ fontSize: "20px", fontWeight: "700", color: "#f1f5f9" }}
            >
              BotDetector
            </h1>
            <p style={{ fontSize: "12px", color: "#64748b" }}>
              Real-time bot detection dashboard
            </p>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            background: "#14532d",
            color: "#4ade80",
            padding: "6px 14px",
            borderRadius: "20px",
            fontSize: "12px",
          }}
        >
          <span
            style={{
              width: "7px",
              height: "7px",
              background: "#4ade80",
              borderRadius: "50%",
              display: "inline-block",
              animation: "pulse 1.5s infinite",
            }}
          />
          API Live
        </div>
      </div>

      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}`}</style>

      {/* Stat Cards */}
      <StatCards stats={stats} />

      {/* Feed + Gauge */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "16px" }}>
        <ThreatFeed feed={feed} />
        <ScoreGauge feed={feed} />
      </div>

      {/* Live Checker */}
      <LiveChecker />

      {/* Footer */}
      <div
        style={{
          textAlign: "center",
          marginTop: "24px",
          color: "#334155",
          fontSize: "11px",
        }}
      >
        Botdetector v1.0 · API Key: bs_test_demo123 · Polling every 3s ·
        Backend: http://localhost:8000
      </div>
    </div>
  );
}
