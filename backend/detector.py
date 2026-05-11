"""
detector.py — 3 Layer Bot Detection Engine
Layer 1: Honeypot
Layer 2: Browser Fingerprint  
Layer 3: Behavioral Analysis
"""

import joblib
import numpy as np
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

try:
    model  = joblib.load(os.path.join(MODEL_DIR, "bot_detector.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    ML_READY = True
except:
    ML_READY = False
    print("Warning: ML model not found, using rule-based only")


# ── LAYER 1: HONEYPOT ────────────────────────────────────────────────────────
def check_honeypot(value: str) -> dict:
    """
    Hidden field humans never see.
    Bots auto-fill every field they find.
    If this field has any value = 100% bot.
    """
    caught = bool(value and value.strip())
    return {
        "caught":  caught,
        "method":  "honeypot",
        "score":   1.0 if caught else 0.0,
        "reason":  "Filled hidden honeypot field" if caught else "clean"
    }


# ── LAYER 2: FINGERPRINT ─────────────────────────────────────────────────────
def check_fingerprint(fp: dict) -> dict:
    """
    Checks browser environment.
    Headless browsers (Playwright, Selenium, Puppeteer)
    fail these checks because they have no real GPU,
    no battery, and often expose their webdriver flag.
    """
    flags = []
    score = 0.0

    # Webdriver flag = Selenium or Playwright — instant catch
    if fp.get("webdriver"):
        flags.append("Webdriver flag detected")
        score += 0.90

    # No canvas hash = headless browser with no GPU
    if not fp.get("canvas_hash"):
        flags.append("No canvas fingerprint — headless browser")
        score += 0.35

    # No battery API = running on a server not a real device
    if not fp.get("has_battery"):
        flags.append("No battery API — server environment")
        score += 0.20

    # Claims to be mobile but screen width is desktop size
    ua = fp.get("user_agent", "").lower()
    width = fp.get("screen_width", 1920)
    if "mobile" in ua and width > 1200:
        flags.append("Mobile UA but desktop resolution — inconsistency")
        score += 0.30

    # Claims mobile but no touch support
    if "mobile" in ua and not fp.get("touch_support"):
        flags.append("Mobile UA but no touch events")
        score += 0.20

    # No language set = bot default browser
    if not fp.get("language"):
        flags.append("No browser language set")
        score += 0.10

    score = min(round(score, 3), 1.0)
    return {
        "caught": score >= 0.5,
        "method": "fingerprint",
        "score":  score,
        "flags":  flags
    }


# ── LAYER 3: BEHAVIORAL ──────────────────────────────────────────────────────
def check_behavior(behavior: dict) -> dict:
    """
    Analyzes HOW the user interacts.
    Humans move in curves, scroll with jitter, type with rhythm.
    Bots move in straight lines, scroll perfectly, type robotically.
    """
    mouse   = behavior.get("mouse_coords", [])
    scrolls = behavior.get("scroll_events", [])
    keys    = behavior.get("keystroke_intervals", [])
    flags   = []
    score   = 0.0

    # ── Mouse analysis ──
    if len(mouse) == 0:
        flags.append("Zero mouse movement")
        score += 0.25
    elif len(mouse) >= 3:
        xs = [p["x"] for p in mouse]
        ys = [p["y"] for p in mouse]

        # Perfect straight horizontal or vertical line
        if len(set([round(x) for x in xs])) == 1:
            flags.append("Mouse moves in perfect vertical line")
            score += 0.40
        if len(set([round(y) for y in ys])) == 1:
            flags.append("Mouse moves in perfect horizontal line")
            score += 0.40

        # Teleportation — jumps more than 500px instantly
        for i in range(1, len(mouse)):
            dist = abs(mouse[i]["x"] - mouse[i-1]["x"]) + abs(mouse[i]["y"] - mouse[i-1]["y"])
            if dist > 500:
                flags.append(f"Mouse teleported {int(dist)}px instantly")
                score += 0.35
                break

        # Zero variance in movement = robotic
        x_std = np.std(xs)
        y_std = np.std(ys)
        if x_std < 2 and y_std < 2:
            flags.append("Mouse has near-zero movement variance")
            score += 0.30

    # ── Scroll analysis ──
    if len(scrolls) >= 3:
        deltas = [abs(s["delta"]) for s in scrolls]
        std = np.std(deltas)
        # Perfectly constant scroll = bot
        if std < 1.0:
            flags.append(f"Perfectly constant scroll speed (std={std:.2f})")
            score += 0.35

    # ── Keystroke analysis ──
    if len(keys) >= 4:
        std = np.std(keys)
        avg = np.mean(keys)
        # Very low variance = robotic typing
        if std < 8 and avg < 120:
            flags.append(f"Robotic keystroke timing (std={std:.1f}ms, avg={avg:.0f}ms)")
            score += 0.35

    score = min(round(score, 3), 1.0)
    return {
        "caught": score >= 0.5,
        "method": "behavioral",
        "score":  score,
        "flags":  flags
    }


# ── FINAL VERDICT ─────────────────────────────────────────────────────────────
def get_verdict(honeypot_r, fingerprint_r, behavior_r) -> dict:
    """
    Combines all 3 layers into one final verdict.
    Honeypot = instant bot, no further checks needed.
    Others = weighted combination.
    """
    # Instant catch
    if honeypot_r["caught"]:
        return {
            "is_bot":    True,
            "verdict":   "BOT",
            "bot_score": 1.0,
            "caught_by": "honeypot",
            "flags":     ["Filled hidden honeypot field"]
        }

    fp_score  = fingerprint_r["score"]
    beh_score = behavior_r["score"]

    # Fingerprint is stronger signal (60%) than behavior (40%)
    final = round((fp_score * 0.6) + (beh_score * 0.4), 3)

    all_flags = fingerprint_r["flags"] + behavior_r["flags"]

    if final >= 0.7:
        verdict = "BOT"
    elif final >= 0.4:
        verdict = "SUSPICIOUS"
    else:
        verdict = "HUMAN"

    return {
        "is_bot":            verdict == "BOT",
        "verdict":           verdict,
        "bot_score":         final,
        "caught_by":         "fingerprint+behavioral",
        "flags":             all_flags,
        "fingerprint_score": fp_score,
        "behavior_score":    beh_score
    }