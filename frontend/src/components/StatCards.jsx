export default function StatCards({ stats }) {
  const cards = [
    {
      label: "Total Requests",
      value: stats.total.toLocaleString(),
      color: "#3b82f6",
      border: "#1d4ed8",
    },
    {
      label: "Bots Blocked",
      value: stats.bots.toLocaleString(),
      color: "#ef4444",
      border: "#b91c1c",
    },
    {
      label: "Humans Passed",
      value: stats.humans.toLocaleString(),
      color: "#22c55e",
      border: "#15803d",
    },
    {
      label: "Suspicious",
      value: stats.suspicious?.toLocaleString() || "0",
      color: "#f59e0b",
      border: "#b45309",
    },
    {
      label: "Catch Rate",
      value: `${stats.catch_rate}%`,
      color: "#a78bfa",
      border: "#7c3aed",
    },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(5, 1fr)",
        gap: "12px",
        marginBottom: "20px",
      }}
    >
      {cards.map((c, i) => (
        <div
          key={i}
          style={{
            background: "#1e293b",
            borderRadius: "12px",
            padding: "16px 20px",
            borderTop: `3px solid ${c.border}`,
            border: "1px solid #334155",
          }}
        >
          <p
            style={{
              color: "#64748b",
              fontSize: "11px",
              marginBottom: "6px",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
            }}
          >
            {c.label}
          </p>
          <h3 style={{ color: c.color, fontSize: "24px", fontWeight: "600" }}>
            {c.value}
          </h3>
        </div>
      ))}
    </div>
  );
}
