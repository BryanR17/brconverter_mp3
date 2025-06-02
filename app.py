from flask import Flask, render_template, request, send_file
import os
import uuid
import yt_dlp
import tempfile


app = Flask(__name__)
temp_files = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("youtube_url", "").strip()

        if not url.startswith("http"):
            return "URL inválida. Por favor, cole um link válido do YouTube."

        try:
            video_id = str(uuid.uuid4())
            temp_dir = tempfile.gettempdir()
            temp_base = os.path.join(temp_dir, video_id)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"{temp_base}.%(ext)s",  # sem forçar .mp3 aqui
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
                return "Erro: MP3 não foi gerado corretamente."

            temp_files[video_id] = {
                "path": mp3_path,
                "title": title
            }

            return render_template("index.html", title=title, thumbnail=thumbnail, video_id=video_id)

        except Exception as e:
            return f"Erro ao processar o vídeo: {str(e)}"

    return render_template("index.html")

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


