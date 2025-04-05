import os
import threading
import yt_dlp
import customtkinter as ctk

DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

QUALITY_MAP = {}
quality_var = None
quality_dropdown = None
progress_label = None
progress_bar = None
url_entry = None

def fetch_formats():
    global QUALITY_MAP
    url = url_entry.get()
    if not url:
        progress_label.configure(text="Enter a valid URL first.", text_color="red")
        return

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        available_qualities = {}

        for fmt in formats:
            format_id = fmt.get("format_id")
            height = fmt.get("height")
            acodec = fmt.get("acodec")
            vcodec = fmt.get("vcodec")

            if height in [1080, 720, 480] and vcodec != "none":
                available_qualities[f"{height}p"] = format_id

        if not available_qualities:
            progress_label.configure(text="No valid formats found.", text_color="red")
            return

        QUALITY_MAP.clear()
        QUALITY_MAP.update(available_qualities)

        quality_dropdown.configure(values=list(QUALITY_MAP.keys()))
        quality_var.set(next(iter(QUALITY_MAP.keys())))
        progress_label.configure(text="Formats fetched successfully!", text_color="green")

    except Exception as e:
        progress_label.configure(text=f"Error: {str(e)}", text_color="red")

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total
            progress_bar.set(percent)
            progress_label.configure(text=f"{int(percent * 100)}%", text_color="yellow")
    elif d['status'] == 'finished':
        progress_bar.set(1)
        progress_label.configure(text="Download complete!", text_color="green")
        progress_bar.pack_forget()

def threaded_download():
    url = url_entry.get()
    quality = quality_var.get()
    format_code = QUALITY_MAP.get(quality)

    if not url or format_code is None:
        progress_label.configure(text="Enter a valid URL and select quality.", text_color="red")
        return

    ydl_opts = {
        'format': f"{format_code}+bestaudio",
        'outtmpl': os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"),
        'quiet': True,
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
    }

    try:
        progress_bar.set(0)
        progress_bar.pack(pady=10)
        progress_label.configure(text="Downloading...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        progress_label.configure(text=f"Error: {str(e)}", text_color="red")
        progress_bar.pack_forget()

def download_video():
    thread = threading.Thread(target=threaded_download)
    thread.start()

# UI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("YouTube Downloader with ffmpeg")
root.geometry("450x400")

ctk.CTkLabel(root, text="YouTube URL:", font=("Arial", 14)).pack(pady=10)
url_entry = ctk.CTkEntry(root, width=350)
url_entry.pack(pady=5)

ctk.CTkButton(root, text="Fetch Formats", command=fetch_formats).pack(pady=10)

ctk.CTkLabel(root, text="Select Quality:", font=("Arial", 14)).pack(pady=5)
quality_var = ctk.StringVar(value="Select Format")
quality_dropdown = ctk.CTkComboBox(root, values=[], variable=quality_var)
quality_dropdown.pack(pady=5)

ctk.CTkButton(root, text="Download", command=download_video).pack(pady=20)

progress_bar = ctk.CTkProgressBar(root, width=300)
progress_bar.set(0)
progress_bar.pack_forget()

progress_label = ctk.CTkLabel(root, text="", font=("Arial", 12))
progress_label.pack(pady=10)

root.mainloop()
