from flask import Flask, send_from_directory

app = Flask(__name__)

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
    return send_from_directory(".", "tiktok1d5bRrkCI9muV1ncrPR62Dx42QfdWcnb.txt", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
