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
