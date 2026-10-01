from flask import Flask, send_from_directory, redirect, request, session, jsonify
import os, secrets, urllib.parse, requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("TIKTOK_REDIRECT_URI", "https://cem-ai-studio.onrender.com/auth/tiktok/callback")
SCOPES = "user.info.basic,video.upload"

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/terms.html")
def terms():
    return send_from_directory(".", "terms.html")

@app.route("/privacy.html")
def privacy():
    return send_from_directory(".", "privacy.html")

@app.route("/tiktok-developers-site-verification.txt")
def tiktok_verification():
    return send_from_directory(".", "tiktok-developers-site-verification.txt", mimetype="text/plain")

@app.route("/tiktok1d5bRrkCI9muV1ncrPR62Dx42QfdWcnb.txt")
def tiktok_signature_new():
    return send_from_directory(".", "tiktok1d5bRrkCI9muV1ncrPR62QfdWcnb.txt", mimetype="text/plain")

@app.route("/auth/tiktok")
def tiktok_login():
    if not CLIENT_KEY:
        return "TikTok Client Key Render ortamında tanımlı değil.", 500
    state = secrets.token_urlsafe(32)
    session["tiktok_state"] = state
    params = {
        "client_key": CLIENT_KEY,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }
    return redirect("https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(params))

@app.route("/auth/tiktok/callback")
def tiktok_callback():
    if request.args.get("error"):
        return f"TikTok yetkilendirmesi başarısız: {request.args.get('error')} — {request.args.get('error_description','')}", 400
    if request.args.get("state") != session.get("tiktok_state"):
        return "Geçersiz OAuth state.", 400
    code = request.args.get("code")
    if not code:
        return "TikTok authorization code alınamadı.", 400
    if not CLIENT_KEY or not CLIENT_SECRET:
        return "TikTok Client Key/Secret Render ortamında tanımlı değil.", 500
    r = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        },
        timeout=20
    )
    if r.status_code != 200:
        return f"TikTok token alınamadı: {r.text}", 400
    data = r.json()
    session["tiktok_access_token"] = data.get("access_token")
    session["tiktok_open_id"] = data.get("open_id")
    session["tiktok_scope"] = data.get("scope", "")
    return redirect("/?tiktok=connected")

@app.route("/api/tiktok/status")
def tiktok_status():
    return jsonify({
        "connected": bool(session.get("tiktok_access_token")),
        "open_id": session.get("tiktok_open_id"),
        "scope": session.get("tiktok_scope", "")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
