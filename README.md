# BotShield — Real-Time Bot Detection API

> An API-first bot detection platform that identifies fake and automated
> traffic using 3-layer behavioral analysis — similar to how Cloudflare,
> DataDome, and PerimeterX work, but open-source and affordable.

---

## The Problem

Companies lose **$100 billion/year** to:

- Click fraud bots inflating ad costs
- Scalper bots buying out inventory in milliseconds
- Scraper bots stealing pricing data
- Fake account bots manipulating social platforms

Existing solutions (Cloudflare, DataDome) cost **$3,000-$10,000/month** —
completely inaccessible for startups and small businesses.

BotShield provides the same core technology as an affordable API.

---

## 🔍 How It Works — 3 Layers of Detection

### Layer 1 — Honeypot Trap

A hidden input field is injected into forms. Humans never see it
so never fill it. Bots auto-fill every field they find.
Result: **100% confidence instant detection.**

### Layer 2 — Browser Fingerprinting

Silent JavaScript checks run the moment a visitor arrives:

| Check                | Human              | Bot                        |
| -------------------- | ------------------ | -------------------------- |
| Canvas fingerprint   | Unique GPU hash    | null (no GPU)              |
| Battery API          | Real battery level | None (server)              |
| Webdriver flag       | false              | true (Playwright/Selenium) |
| Screen vs User-Agent | Consistent         | Inconsistent               |
| Touch support        | Matches device     | Missing                    |

### Layer 3 — Behavioral Analysis

4 seconds of silent observation:

| Signal           | Human Pattern            | Bot Pattern              |
| ---------------- | ------------------------ | ------------------------ |
| Mouse movement   | Natural curves, trembles | Perfectly straight lines |
| Scroll speed     | Varies, flicks, pauses   | Constant robotic speed   |
| Keystroke timing | Rhythm varies naturally  | Exactly N ms per key     |
| Mouse variance   | High (natural jitter)    | Near-zero (robotic)      |

### Final Score

All 3 layers combine into a **bot score from 0.0 to 1.0:**

```
> 0.7   →  BOT        (blocked)
0.4-0.7 →  SUSPICIOUS (challenged)
< 0.4   →  HUMAN      (passed)
```

---

## Architecture

```
Companies paste one script on their site:
<script src="https://botshield.app/sdk.js"
        data-key="bs_live_xxxxx"></script>

         ↓ silent data collection ↓

┌─────────────────────────────────────┐
│         BotShield Platform          │
│                                     │
│  React Dashboard  ←  MongoDB        │
│       ↑                ↑            │
│  FastAPI Engine  →  Detection Log   │
│       ↑                             │
│  ML Models (Random Forest +         │
│             Isolation Forest)       │
└─────────────────────────────────────┘
```

---

## Tech Stack

| Layer      | Technology                                 | Purpose              |
| ---------- | ------------------------------------------ | -------------------- |
| Frontend   | React + Vite                               | Live dashboard       |
| Backend    | FastAPI (Python)                           | Detection API        |
| ML Models  | Scikit-learn                               | Bot classification   |
| Dataset    | HuggingFace (37,438 real Twitter accounts) | Model training       |
| Styling    | Custom CSS                                 | Dark theme dashboard |
| Simulation | Playwright + Requests                      | Bot/Human testing    |

---

## Detection Performance

| Metric            | Score                |
| ----------------- | -------------------- |
| Model Accuracy    | ~96%                 |
| ROC-AUC           | ~0.99                |
| API Response Time | < 50ms               |
| Dataset Size      | 37,438 real accounts |

---

## Project Structure

```
botdetector/
├── backend/
│   ├── main.py              ← FastAPI server (6 endpoints)
│   ├── detector.py          ← 3-layer detection logic
│   ├── models/              ← trained ML models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── StatCards.jsx    ← live metrics
│   │   │   ├── ThreatFeed.jsx   ← real-time feed
│   │   │   ├── ScoreGauge.jsx   ← bot probability
│   │   │   └── LiveChecker.jsx  ← manual checker
│   │   └── hooks/
│   │       └── useDashboard.js  ← polling hook
│   └── package.json
├── test-site/
│   └── index.html           ← demo website with SDK
├── bot-simulator/
│   └── bot.py               ← simulates bot + human visits
├── load_data.py             ← real dataset pipeline
├── train.py                 ← model training
└── README.md
```

---

## Setup & Run

### Prerequisites

- Python 3.9+
- Node.js 18+
- pip

### 1. Clone the repo

```bash
git clone https://github.com/MohdAinul/botdetector.git
cd botdetector
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Test Site

```bash
cd test-site
python3 -m http.server 3000
```

### 5. Simulate Bot Attack

```bash
cd bot-simulator
python3 bot.py
# Choose: 1 (bot) / 2 (human) / 3 (both)
```

### 6. Open Dashboard

```
http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint           | Description                  |
| ------ | ------------------ | ---------------------------- |
| POST   | `/analyse`         | Main detection endpoint      |
| GET    | `/dashboard/stats` | Total requests, bots, humans |
| GET    | `/dashboard/feed`  | Latest 20 detections         |
| GET    | `/sdk.js`          | JavaScript SDK for websites  |
| GET    | `/health`          | Server health check          |

### Example Request

```json
POST /analyse
{
  "session_id": "abc123",
  "api_key": "bs_test_demo123",
  "fingerprint": {
    "canvas_hash": null,
    "has_battery": false,
    "webdriver": true,
    "user_agent": "HeadlessChrome/120",
    "honeypot": "bot-was-here"
  },
  "behavior": {
    "mouse_coords": [
      {"x":0,"y":0,"t":0},
      {"x":500,"y":0,"t":50}
    ],
    "scroll_events": [
      {"delta":100,"t":0}
    ],
    "keystroke_intervals": [50,50,50,50]
  }
}
```

### Example Response

```json
{
  "verdict": "BOT",
  "is_bot": true,
  "bot_score": 0.97,
  "caught_by": "honeypot + fingerprint + behavioral",
  "flags": [
    "Filled hidden honeypot field",
    "Webdriver flag detected",
    "No canvas fingerprint — headless browser",
    "Mouse moves in perfect straight line",
    "Robotic keystroke timing (std=0.0ms)"
  ],
  "latency_ms": 12.4
}
```

---

## 💼 Business Model

This project is architected as a real SaaS product:

```
Free       →    1,000 requests/month  →  ₹0
Starter    →   50,000 requests/month  →  ₹999/month
Pro        →  500,000 requests/month  →  ₹4,999/month
Enterprise →   Unlimited              →  Custom pricing
```

Competing with: Cloudflare Bot Management ($200+/month),
DataDome ($3,000/month), PerimeterX (acquired for $1B)

---

## 🗺️ Roadmap

- [x] 3-layer detection engine
- [x] React live dashboard
- [x] Bot simulator for testing
- [ ] Company auth + API key system
- [ ] Redis queue for high throughput
- [ ] MongoDB persistent storage
- [ ] Deploy to Railway + Vercel
- [ ] NLP on tweet content
- [ ] IP geolocation threat map

---

## 👤 Author

**Mohd Ainul**  
[GitHub](https://github.com/MohdAinul) ·
[LinkedIn](https://www.linkedin.com/in/mohd-ainul-27492b27a/) ·
[Portfolio](https://portfolio-kappa-bay-89.vercel.app)

---

## 📄 License

MIT License — free to use, modify, and distribute.
