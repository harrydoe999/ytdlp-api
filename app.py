import os
import subprocess
import uuid
import shutil

# Install deno if not present
if not shutil.which("deno"):
    os.system("curl -fsSL https://deno.land/install.sh | sh")
    os.environ["PATH"] = f"/opt/render/.deno/bin:{os.environ.get('PATH', '')}"

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    quality = data.get("quality", "1080")
    mode = data.get("mode", "video")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    file_id = str(uuid.uuid4())
    output_path = f"{DOWNLOAD_FOLDER}/{file_id}.%(ext)s"

    if mode == "audio":
        command = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--cookies", "/opt/render/project/src/cookies.txt",
            "--extractor-args", "youtube:player_client=web_safari",
            "--remote-components", "ejs:github",
            "-o", output_path,
            url
        ]
    else:
        command = [
            "yt-dlp",
            "-f", f"best[height<={quality}]/best",
            "--merge-output-format", "mp4",
            "--no-playlist",
            "--cookies", "/opt/render/project/src/cookies.txt",
            "--extractor-args", "youtube:player_client=web_safari",
            "--remote-components", "ejs:github",
            "-o", output_path,
            url
        ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": "yt-dlp failed", "details": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    for f in os.listdir(DOWNLOAD_FOLDER):
        if f.startswith(file_id):
            return send_file(
                os.path.join(DOWNLOAD_FOLDER, f),
                as_attachment=True
            )

    return jsonify({"error": "Download failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
