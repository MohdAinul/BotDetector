export default function ScoreGauge({ feed }) {
  const latest = feed[0];
  const score = latest?.bot_score ?? 0;
  const verdict = latest?.verdict ?? "WAITING";
  const pct = Math.round(score * 100);

  const color = score > 0.7 ? "#ef4444" : score > 0.4 ? "#f59e0b" : "#22c55e";

  // SVG arc calculation
  const r = 54;
  const circ = Math.PI * r;
  const offset = circ - (pct / 100) * circ;

  return (
    <div
      className="card"
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <h3
        style={{
          fontSize: "13px",
          color: "#94a3b8",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          marginBottom: "16px",
          alignSelf: "flex-start",
        }}
      >
        Latest Bot Score
      </h3>

      <svg width="140" height="80" viewBox="0 0 140 80">
        <path
          d="M10 70 A60 60 0 0 1 130 70"
          fill="none"
          stroke="#334155"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d="M10 70 A60 60 0 0 1 130 70"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.5s ease, stroke 0.3s" }}
        />
        <text
          x="70"
          y="65"
          textAnchor="middle"
          fill={color}
          fontSize="22"
          fontWeight="600"
        >
          {pct}%
        </text>
      </svg>

      <div
        style={{
          marginTop: "12px",
          padding: "6px 20px",
          borderRadius: "20px",
          fontSize: "13px",
          fontWeight: "600",
          background:
            score > 0.7 ? "#7f1d1d" : score > 0.4 ? "#78350f" : "#14532d",
          color: color,
        }}
      >
        {verdict}
      </div>

      {latest && (
        <div style={{ marginTop: "16px", width: "100%" }}>
          {[
            {
              label: "Fingerprint score",
              value: latest.fingerprint_score ?? 0,
            },
            { label: "Behavior score", value: latest.behavior_score ?? 0 },
          ].map((row, i) => (
            <div key={i} style={{ marginBottom: "8px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "4px",
                }}
              >
                <span style={{ fontSize: "11px", color: "#64748b" }}>
                  {row.label}
                </span>
                <span style={{ fontSize: "11px", color: "#f1f5f9" }}>
                  {Math.round(row.value * 100)}%
                </span>
              </div>
              <div
                style={{
                  background: "#334155",
                  borderRadius: "4px",
                  height: "5px",
                }}
              >
                <div
                  style={{
                    width: `${row.value * 100}%`,
                    height: "100%",
                    borderRadius: "4px",
                    background:
                      row.value > 0.7
                        ? "#ef4444"
                        : row.value > 0.4
                          ? "#f59e0b"
                          : "#22c55e",
                    transition: "width 0.5s ease",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
