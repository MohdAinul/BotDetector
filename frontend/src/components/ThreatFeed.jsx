const verdictColor = {
  BOT: { bg: "#7f1d1d", text: "#fca5a5" },
  HUMAN: { bg: "#14532d", text: "#86efac" },
  SUSPICIOUS: { bg: "#78350f", text: "#fcd34d" },
};

function timeAgo(ts) {
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 5) return "just now";
  if (diff < 60) return `${diff}s ago`;
  return `${Math.floor(diff / 60)}m ago`;
}

export default function ThreatFeed({ feed }) {
  return (
    <div className="card" style={{ flex: 2 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "16px",
        }}
      >
        <h3
          style={{
            fontSize: "13px",
            color: "#94a3b8",
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}
        >
          Live Threat Feed
        </h3>
        <span
          style={{
            background: "#14532d",
            color: "#4ade80",
            fontSize: "11px",
            padding: "3px 10px",
            borderRadius: "20px",
            display: "flex",
            alignItems: "center",
            gap: "5px",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              background: "#4ade80",
              borderRadius: "50%",
              display: "inline-block",
              animation: "pulse 1.5s infinite",
            }}
          />
          Live
        </span>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes slideIn { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      {feed.length === 0 ? (
        <div
          style={{
            color: "#475569",
            textAlign: "center",
            padding: "40px 0",
            fontSize: "13px",
          }}
        >
          Waiting for traffic... Open the test website to see detections.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {feed.slice(0, 8).map((entry, i) => {
            const vc = verdictColor[entry.verdict] || verdictColor.SUSPICIOUS;
            return (
              <div
                key={entry.id}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                  background: "#0f172a",
                  borderRadius: "8px",
                  padding: "10px 12px",
                  animation: i === 0 ? "slideIn 0.3s ease" : "none",
                  borderLeft: `3px solid ${vc.text}`,
                }}
              >
                <span
                  style={{
                    background: vc.bg,
                    color: vc.text,
                    fontSize: "10px",
                    padding: "2px 8px",
                    borderRadius: "10px",
                    fontWeight: "600",
                    whiteSpace: "nowrap",
                    marginTop: "1px",
                  }}
                >
                  {entry.verdict}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span
                      style={{
                        color: "#f1f5f9",
                        fontSize: "12px",
                        fontFamily: "monospace",
                      }}
                    >
                      {entry.ip}
                    </span>
                    <span style={{ color: "#475569", fontSize: "10px" }}>
                      {timeAgo(entry.timestamp)}
                    </span>
                  </div>
                  <div
                    style={{
                      color: "#64748b",
                      fontSize: "11px",
                      marginTop: "3px",
                    }}
                  >
                    {entry.flags?.slice(0, 2).join(" · ") || "No flags"}
                  </div>
                </div>
                <span
                  style={{
                    color:
                      entry.bot_score > 0.7
                        ? "#ef4444"
                        : entry.bot_score > 0.4
                          ? "#f59e0b"
                          : "#22c55e",
                    fontSize: "13px",
                    fontWeight: "600",
                    whiteSpace: "nowrap",
                  }}
                >
                  {entry.bot_score?.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
