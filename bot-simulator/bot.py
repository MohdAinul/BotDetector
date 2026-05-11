"""
bot.py — Simulates a bot attack by directly calling BotShield API
"""
import requests
import time
import random
import string

def generate_session():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

def run_bot():
    print("🤖 Bot starting attack...")

    payload = {
        "session_id": generate_session(),
        "api_key": "bs_test_demo123",
        "fingerprint": {
            "canvas_hash":   None,        # headless = no canvas
            "has_battery":   False,       # server = no battery
            "user_agent":    "Mozilla/5.0 (X11; Linux x86_64) HeadlessChrome/120",
            "screen_width":  1920,
            "screen_height": 1080,
            "webdriver":     True,        # Playwright sets this to True
            "touch_support": False,
            "language":      None,        # bots often have no language
            "honeypot":      "bot-was-here"  # bot filled hidden field
        },
        "behavior": {
            # Perfect straight line mouse movement
            "mouse_coords": [
                {"x": 0,   "y": 0,   "t": 0},
                {"x": 100, "y": 0,   "t": 50},
                {"x": 200, "y": 0,   "t": 100},
                {"x": 300, "y": 0,   "t": 150},
                {"x": 400, "y": 0,   "t": 200},
            ],
            # Perfectly constant scroll speed
            "scroll_events": [
                {"delta": 100, "t": 0},
                {"delta": 200, "t": 100},
                {"delta": 300, "t": 200},
                {"delta": 400, "t": 300},
            ],
            # Robotic keystroke timing — exactly 50ms each
            "keystroke_intervals": [50, 50, 50, 50, 50, 50]
        }
    }

    print("📡 Sending bot session to BotShield API...")
    try:
        res = requests.post("http://localhost:8000/analyse", json=payload)
        data = res.json()
        print(f"\n{'='*40}")
        print(f"  Verdict    : {data['verdict']}")
        print(f"  Bot Score  : {data['bot_score']}")
        print(f"  Caught By  : {data['caught_by']}")
        print(f"  Flags      : {data['flags']}")
        print(f"{'='*40}")
        print("✅ Check dashboard at http://localhost:5173")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure backend is running: uvicorn main:app --reload --port 8000")


def run_human():
    print("✅ Simulating human visit...")

    payload = {
        "session_id": generate_session(),
        "api_key": "bs_test_demo123",
        "fingerprint": {
            "canvas_hash":   "a1b2c3d4e5",  # real GPU renders canvas
            "has_battery":   True,            # real device has battery
            "user_agent":    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",
            "screen_width":  1440,
            "screen_height": 900,
            "webdriver":     False,           # real browser
            "touch_support": False,
            "language":      "en-US",
            "honeypot":      ""               # human never fills honeypot
        },
        "behavior": {
            # Natural curved mouse movement
            "mouse_coords": [
                {"x": 0,   "y": 0,   "t": 0},
                {"x": 45,  "y": 32,  "t": 120},
                {"x": 112, "y": 78,  "t": 230},
                {"x": 198, "y": 134, "t": 310},
                {"x": 276, "y": 201, "t": 420},
                {"x": 334, "y": 289, "t": 490},
            ],
            # Natural scroll with variation
            "scroll_events": [
                {"delta": 80,  "t": 0},
                {"delta": 210, "t": 180},
                {"delta": 190, "t": 420},
                {"delta": 320, "t": 600},
            ],
            # Natural keystroke timing — varies like a human
            "keystroke_intervals": [124, 87, 143, 98, 167, 112, 89, 134]
        }
    }

    try:
        res = requests.post("http://localhost:8000/analyse", json=payload)
        data = res.json()
        print(f"\n{'='*40}")
        print(f"  Verdict    : {data['verdict']}")
        print(f"  Bot Score  : {data['bot_score']}")
        print(f"  Flags      : {data['flags']}")
        print(f"{'='*40}")
        print("✅ Check dashboard at http://localhost:5173")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("BotShield Simulator")
    print("1 — Run Bot Attack")
    print("2 — Run Human Visit")
    print("3 — Run Both")
    choice = input("Choose (1/2/3): ").strip()

    if choice == "1":
        run_bot()
    elif choice == "2":
        run_human()
    elif choice == "3":
        run_bot()
        time.sleep(1)
        run_human()
    else:
        print("Running bot by default...")
        run_bot()