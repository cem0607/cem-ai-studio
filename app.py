from flask import Flask, send_from_directory, redirect, request, session, jsonify
import os, secrets, urllib.parse, requests, math

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("TIKTOK_REDIRECT_URI", "https://cem-ai-studio.onrender.com/auth/tiktok/callback")
SCOPES = "user.info.basic,video.upload"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

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

@app.route("/sample/rava-na.mp4")
def sample_video():
    return send_from_directory(".", "RAVA_NA_KLIP_FINAL.mp4", mimetype="video/mp4")

@app.route("/api/tiktok/upload", methods=["POST"])
def tiktok_upload():
    token = session.get("tiktok_access_token")
    if not token:
        return jsonify({"ok": False, "error": "TikTok hesabı bağlı değil."}), 401
    video = request.files.get("video")
    if not video or not video.filename:
        return jsonify({"ok": False, "error": "Video seçilmedi."}), 400
    video_bytes = video.read()
    size = len(video_bytes)
    if size == 0:
        return jsonify({"ok": False, "error": "Video dosyası boş."}), 400

    chunk_size = max(5 * 1024 * 1024, min(64 * 1024 * 1024, size))
    total_chunks = math.ceil(size / chunk_size)

    init = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8"
        },
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks
            }
        },
        timeout=30
    )
    if init.status_code != 200:
        return jsonify({"ok": False, "stage": "init", "details": init.text}), 400

    init_data = init.json()
    if init_data.get("error", {}).get("code") != "ok":
        return jsonify({"ok": False, "stage": "init", "details": init_data}), 400

    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]

    for index in range(total_chunks):
        start = index * chunk_size
        end = min(start + chunk_size, size) - 1
        chunk = video_bytes[start:end + 1]
        put = requests.put(
            upload_url,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {start}-{end}/{size}"
            },
            data=chunk,
            timeout=120
        )
        if put.status_code not in (200, 201, 204):
            return jsonify({"ok": False, "stage": "upload", "details": put.text}), 400

    return jsonify({
        "ok": True,
        "publish_id": publish_id,
        "message": "Video TikTok'a taslak olarak gönderildi. TikTok uygulamasındaki gelen bildirime dokunarak düzenleyip yayınlayabilirsiniz."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

@app.route("/tiktokB2YxhNvcIQTtnkaT8bmfRI2npqbzDNEa.txt")
def tiktok_signature_file():
    return send_from_directory(".", "tiktokB2YxhNvcIQTtnkaT8bmfRI2npqbzDNEa.txt", mimetype="text/plain")
