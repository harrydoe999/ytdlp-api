import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    quality = data.get("quality", "1080")
    mode = data.get("mode", "video")  # "video" or "audio"

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    file_id = str(uuid.uuid4())
    output_path = f"{DOWNLOAD_FOLDER}/{file_id}.%(ext)s"

    if mode == "audio":
        command = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "-o", output_path,
            url
        ]
    else:
        command = [
            "yt-dlp",
            "-f", f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best",
            "--merge-output-format", "mp4",
            "--no-playlist",

            "-o", output_path,
            url
        ]

    subprocess.run(command, check=True)

    # Find the actual output file
    for f in os.listdir(DOWNLOAD_FOLDER):
        if f.startswith(file_id):
            return send_file(
                os.path.join(DOWNLOAD_FOLDER, f),
                as_attachment=True
            )

    return jsonify({"error": "Download failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
