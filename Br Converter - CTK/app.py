import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
import tempfile
import os
import uuid
import re
import requests
from io import BytesIO

ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x800")
app.title("BR Converter - YouTube para MP3")
app.iconbitmap("icon.ico")

def obter_info_video():
    url = url_entry.get().strip()
    if not url.startswith("http"):
        status_label.configure(text="URL inválida.", text_color="red")
        return

    status_label.configure(text="Obtendo informações...", text_color="orange")

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Sem título')
            thumbnail_url = info_dict.get('thumbnail', '')

        # Exibir título
        status_label.configure(text=f"Título: {title}", text_color="#dce3dc")

        # Exibir thumbnail
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            img_data = Image.open(BytesIO(response.content)).resize((300, 180))
            photo = ImageTk.PhotoImage(img_data)
            thumb_label.configure(image=photo)
            thumb_label.image = photo
            thumb_label.pack(pady=10)

        # Mostrar botão de download
        download_button.configure(text="Baixar MP3", command=baixar_mp3)
        download_button.pack(pady=10)

    except Exception as e:
        status_label.configure(text=f"Erro: {e}", text_color="red")

def baixar_mp3():
    url = url_entry.get().strip()
    if not url.startswith("http"):
        status_label.configure(text="URL inválida.", text_color="red")
        return

    status_label.configure(text="Baixando MP3...", text_color="orange")

    try:
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_dir, exist_ok=True)

        # Primeiro pega os dados para obter o título
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Sem título')

        # Limpa nome do título para ser nome do arquivo
        nome_limpo = re.sub(r'[\\/*?:"<>|]', "", title)
        out_path = os.path.join(downloads_dir, f"{nome_limpo}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_path,
            'no-mtime': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_path = os.path.join(downloads_dir, f"{nome_limpo}.mp3")
        if os.path.exists(mp3_path):
            import time
            os.utime(mp3_path, (time.time(), time.time()))

            status_label.configure(text=f"Download concluído: {nome_limpo}.mp3", text_color="#35d03b")
            download_button.configure(text="Abrir Arquivo", command=lambda: os.startfile(mp3_path))

    except Exception as e:
        status_label.configure(text=f"Erro: {e}", text_color="red")


# Widgets
image_path = "1.png"
image = Image.open(image_path)

logo_ctk_image = ctk.CTkImage(light_image=image, size=(100, 100))

logo_label = ctk.CTkLabel(app, image=logo_ctk_image, text="")  
logo_label.pack(pady=10)

ctk.CTkLabel(app, text="Baixe Musicas Grátis", font=("poppins", 30), text_color="#35d03b").pack(pady=10)
ctk.CTkLabel(app, text="Converter videos do Youtube para MP3 de forma rápido e fácil.", font=("poppins", 15), text_color="#dce3dc").pack(pady=10)

url_entry = ctk.CTkEntry(app, width=400, height=50, font=("poppins", 15), placeholder_text="Cole o link do vídeo do YouTube", border_color="#35d03b")
url_entry.pack(pady=20)

convert_button = ctk.CTkButton(app, text="Converter", command=obter_info_video, font=("poppins", 15), fg_color="#35d03b", hover_color="#26912a")
convert_button.pack(pady=10)

status_label = ctk.CTkLabel(app, text="", font=("poppins", 15), text_color="#dce3dc")
status_label.pack(pady=10)

thumb_label = ctk.CTkLabel(app, text="", font=("poppins", 15), text_color="#dce3dc")
thumb_label.pack_forget()

download_button = ctk.CTkButton(app, text="Abrir Arquivo", command=baixar_mp3, font=("poppins", 15), fg_color="#35d03b", hover_color="#26912a")
download_button.pack_forget()

app.mainloop()
