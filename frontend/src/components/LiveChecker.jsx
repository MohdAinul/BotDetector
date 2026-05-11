import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function LiveChecker() {
  const [form, setForm] = useState({
    followers: 120,
    following: 4500,
    tweets: 25000,
    age: 60,
    daily: 85,
    has_pic: false,
    has_bio: false,
    verified: false,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyse = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/analyse`, {
        session_id: Math.random().toString(36).substr(2, 9),
        api_key: "bs_test_demo123",
        fingerprint: {
          canvas_hash: form.has_pic ? "abc123" : null,
          has_battery: false,
          user_agent: "Mozilla/5.0 (Test)",
          screen_width: 1920,
          screen_height: 1080,
          webdriver: false,
          touch_support: false,
          language: "en-US",
          honeypot: "",
        },
        behavior: {
          mouse_coords:
            form.daily > 50
              ? [
                  { x: 0, y: 0, t: 0 },
                  { x: 500, y: 0, t: 100 },
                  { x: 500, y: 400, t: 200 },
                ]
              : [
                  { x: 0, y: 0, t: 0 },
                  { x: 120, y: 80, t: 100 },
                  { x: 200, y: 130, t: 180 },
                  { x: 310, y: 190, t: 280 },
                ],
          scroll_events:
            form.daily > 50
              ? [
                  { delta: 100, t: 0 },
                  { delta: 200, t: 100 },
                  { delta: 300, t: 200 },
                ]
              : [
                  { delta: 100, t: 0 },
                  { delta: 180, t: 150 },
                  { delta: 290, t: 320 },
                ],
          keystroke_intervals:
            form.daily > 50 ? [50, 50, 50, 50, 50] : [120, 98, 145, 87, 134],
        },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const inp = (label, key, type = "number") => (
    <div>
      <label
        style={{
          color: "#64748b",
          fontSize: "11px",
          display: "block",
          marginBottom: "4px",
        }}
      >
        {label}
      </label>
      {type === "bool" ? (
        <select
          value={form[key] ? "yes" : "no"}
          onChange={(e) =>
            setForm({ ...form, [key]: e.target.value === "yes" })
          }
          style={{
            width: "100%",
            background: "#0f172a",
            border: "1px solid #334155",
            borderRadius: "6px",
            color: "#f1f5f9",
            padding: "7px 8px",
            fontSize: "12px",
          }}
        >
          <option value="no">No</option>
          <option value="yes">Yes</option>
        </select>
      ) : (
        <input
          type="number"
          value={form[key]}
          onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
          style={{
            width: "100%",
            background: "#0f172a",
            border: "1px solid #334155",
            borderRadius: "6px",
            color: "#f1f5f9",
            padding: "7px 8px",
            fontSize: "12px",
          }}
        />
      )}
    </div>
  );

  const scoreColor = result
    ? result.bot_score > 0.7
      ? "#ef4444"
      : result.bot_score > 0.4
        ? "#f59e0b"
        : "#22c55e"
    : "#3b82f6";

  return (
    <div className="card">
      <h3
        style={{
          fontSize: "13px",
          color: "#94a3b8",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          marginBottom: "16px",
        }}
      >
        Live Account Checker
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "12px",
          marginBottom: "12px",
        }}
      >
        {inp("Followers", "followers")}
        {inp("Following", "following")}
        {inp("Tweet Count", "tweets")}
        {inp("Account Age (days)", "age")}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "12px",
          marginBottom: "16px",
        }}
      >
        {inp("Avg Daily Tweets", "daily")}
        {inp("Has Profile Pic?", "has_pic", "bool")}
        {inp("Has Bio?", "has_bio", "bool")}
        {inp("Verified?", "verified", "bool")}
      </div>

      <button
        onClick={analyse}
        disabled={loading}
        style={{
          background: loading ? "#1e3a5f" : "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: "8px",
          padding: "10px 24px",
          fontSize: "13px",
          fontWeight: "600",
          cursor: loading ? "not-allowed" : "pointer",
          width: "100%",
        }}
      >
        {loading ? "Analysing..." : "Analyse Account"}
      </button>

      {result && (
        <div
          style={{
            marginTop: "16px",
            background: "#0f172a",
            borderRadius: "10px",
            padding: "16px",
            borderLeft: `4px solid ${scoreColor}`,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "12px",
            }}
          >
            <div>
              <div
                style={{
                  color: scoreColor,
                  fontSize: "22px",
                  fontWeight: "700",
                }}
              >
                {result.verdict}
              </div>
              <div style={{ color: "#64748b", fontSize: "12px" }}>
                Caught by: {result.caught_by}
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div
                style={{
                  color: scoreColor,
                  fontSize: "28px",
                  fontWeight: "700",
                }}
              >
                {Math.round(result.bot_score * 100)}%
              </div>
              <div style={{ color: "#64748b", fontSize: "11px" }}>
                bot probability
              </div>
            </div>
          </div>

          {result.flags?.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {result.flags.map((flag, i) => (
                <span
                  key={i}
                  style={{
                    background: "#1e293b",
                    color: "#fca5a5",
                    fontSize: "11px",
                    padding: "3px 8px",
                    borderRadius: "6px",
                    border: "1px solid #ef444433",
                  }}
                >
                  {flag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
