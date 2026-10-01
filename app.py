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
    return "tiktok-developers-site-verification=BIrGMOBIPySOeUTPqClKkPHo3EmQR6U7"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
