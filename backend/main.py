"""
main.py — BotShield FastAPI Server
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import time, uuid, json
from detector import check_honeypot, check_fingerprint, check_behavior, get_verdict

app = FastAPI(title="BotShield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (MongoDB later)
detections = []
api_keys = {
    "bs_test_demo123": {"company": "Demo Company", "plan": "free"},
    "bs_live_ainul001": {"company": "Ainul Test", "plan": "pro"},
}


# ── Pydantic Models ───────────────────────────────────────────────────────────
class MouseCoord(BaseModel):
    x: float
    y: float
    t: float

class ScrollEvent(BaseModel):
    delta: float
    t: float

class Fingerprint(BaseModel):
    canvas_hash:   Optional[str] = None
    has_battery:   bool = False
    user_agent:    str = ""
    screen_width:  int = 0
    screen_height: int = 0
    webdriver:     bool = False
    touch_support: bool = False
    language:      Optional[str] = None
    honeypot:      str = ""

class Behavior(BaseModel):
    mouse_coords:        List[MouseCoord] = []
    scroll_events:       List[ScrollEvent] = []
    keystroke_intervals: List[float] = []

class AnalyseRequest(BaseModel):
    session_id:  str
    api_key:     str
    fingerprint: Fingerprint
    behavior:    Behavior


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name":    "BotShield API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs"
    }

@app.post("/analyse")
def analyse(req: AnalyseRequest, request: Request):
    start = time.time()

    # Validate API key
    company = api_keys.get(req.api_key, {}).get("company", "unknown")

    # Run 3 layers
    h_result  = check_honeypot(req.fingerprint.honeypot)
    fp_result = check_fingerprint(req.fingerprint.dict())
    beh_result = check_behavior({
        "mouse_coords":        [m.dict() for m in req.behavior.mouse_coords],
        "scroll_events":       [s.dict() for s in req.behavior.scroll_events],
        "keystroke_intervals": req.behavior.keystroke_intervals,
    })

    verdict = get_verdict(h_result, fp_result, beh_result)

    # Save to log
    entry = {
        "id":          str(uuid.uuid4())[:8],
        "session_id":  req.session_id,
        "company":     company,
        "api_key":     req.api_key,
        "ip":          request.client.host,
        "timestamp":   time.time(),
        "verdict":     verdict["verdict"],
        "bot_score":   verdict["bot_score"],
        "caught_by":   verdict.get("caught_by", ""),
        "flags":       verdict.get("flags", []),
        "latency_ms":  round((time.time() - start) * 1000, 2),
        "user_agent":  req.fingerprint.user_agent[:80],
    }
    detections.insert(0, entry)
    if len(detections) > 500:
        detections.pop()

    return {**verdict, "session_id": req.session_id, "latency_ms": entry["latency_ms"]}


@app.get("/dashboard/stats")
def stats(api_key: str = "bs_test_demo123"):
    company_data = [d for d in detections if d["api_key"] == api_key]
    total  = len(company_data)
    bots   = sum(1 for d in company_data if d["verdict"] == "BOT")
    sus    = sum(1 for d in company_data if d["verdict"] == "SUSPICIOUS")
    humans = sum(1 for d in company_data if d["verdict"] == "HUMAN")
    return {
        "total":      total,
        "bots":       bots,
        "suspicious": sus,
        "humans":     humans,
        "catch_rate": round(bots / total * 100, 1) if total else 0
    }


@app.get("/dashboard/feed")
def feed(api_key: str = "bs_test_demo123"):
    company_data = [d for d in detections if d["api_key"] == api_key]
    return company_data[:20]


@app.get("/sdk.js")
def sdk():
    """The JS snippet companies paste on their website."""
    js = """
(function() {
  var BotShield = {
    init: function(apiKey) {
      this.apiKey = apiKey;
      this.sessionId = Math.random().toString(36).substr(2, 9);
      this.mouseData = [];
      this.scrollData = [];
      this.keyData = [];
      this.lastKeyTime = null;
      this._track();
      setTimeout(function() { BotShield._analyse(); }, 4000);
    },
    _track: function() {
      document.addEventListener('mousemove', function(e) {
        if (BotShield.mouseData.length < 100) {
          BotShield.mouseData.push({x: e.clientX, y: e.clientY, t: Date.now()});
        }
      });
      window.addEventListener('scroll', function() {
        BotShield.scrollData.push({delta: window.scrollY, t: Date.now()});
      });
      document.addEventListener('keydown', function() {
        var now = Date.now();
        if (BotShield.lastKeyTime) {
          BotShield.keyData.push(now - BotShield.lastKeyTime);
        }
        BotShield.lastKeyTime = now;
      });
    },
    _getFingerprint: function() {
      var canvas = document.createElement('canvas');
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.font = '11pt Arial';
      ctx.fillText('BotShield', 2, 15);
      var hash = canvas.toDataURL().length.toString();
      return {
        canvas_hash:   hash,
        has_battery:   'getBattery' in navigator,
        user_agent:    navigator.userAgent,
        screen_width:  screen.width,
        screen_height: screen.height,
        webdriver:     navigator.webdriver || false,
        touch_support: 'ontouchstart' in window,
        language:      navigator.language,
        honeypot:      document.getElementById('_bs_hp') ? 
                       document.getElementById('_bs_hp').value : ''
      };
    },
    _analyse: function() {
      fetch('http://localhost:8000/analyse', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          session_id:  this.sessionId,
          api_key:     this.apiKey,
          fingerprint: this._getFingerprint(),
          behavior: {
            mouse_coords:        this.mouseData,
            scroll_events:       this.scrollData,
            keystroke_intervals: this.keyData
          }
        })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.is_bot) {
          console.warn('BotShield: Bot detected', data);
        }
      });
    }
  };
  window.BotShield = BotShield;
})();
"""
    return Response(
        content=js,
        media_type="application/javascript"
    )

@app.get("/health")
def health():
    return {"status": "ok", "total_detections": len(detections)}