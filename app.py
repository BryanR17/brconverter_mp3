from flask import Flask, request, send_file, jsonify
import os
import uuid
import yt_dlp
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

temp_files = {}

@app.route("/", methods=["POST"])
def convert_youtube():
    url = request.form.get("youtube_url", "").strip()

    if not url.startswith("http"):
        return jsonify({"error": "URL inválida. Por favor, cole um link válido do YouTube."}), 400

    try:
        video_id = str(uuid.uuid4())
        temp_dir = tempfile.gettempdir()
        temp_base = os.path.join(temp_dir, video_id)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{temp_base}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'Sem título')
            thumbnail = info_dict.get('thumbnail', '')

        mp3_path = f"{temp_base}.mp3"
        if not os.path.exists(mp3_path):
            return jsonify({"error": "Erro: MP3 não foi gerado corretamente."}), 500

        temp_files[video_id] = {
            "path": mp3_path,
            "title": title
        }

        return jsonify({
            "title": title,
            "thumbnail": thumbnail,
            "video_id": video_id
        })

    except Exception as e:
        return jsonify({"error": f"Erro ao processar o vídeo: {str(e)}"}), 500


@app.route("/download/<video_id>")
def download_file(video_id):
    if video_id in temp_files:
        file_info = temp_files.pop(video_id)
        path = file_info["path"]
        title = file_info["title"]

        if os.path.exists(path):
            response = send_file(path, as_attachment=True, download_name=f"{title}.mp3")
            try:
                os.remove(path)
            except:
                pass
            return response

    return "Arquivo não encontrado.", 404


if __name__ == "__main__":
    app.run(debug=True)


