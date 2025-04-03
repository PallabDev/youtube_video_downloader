import os
import threading
import yt_dlp
import customtkinter as ctk

# Ensure 'downloads' folder exists
DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Global variables
QUALITY_MAP = {}
quality_var = None
quality_dropdown = None
progress_label = None
progress_bar = None

# Function to fetch available formats
def fetch_formats():
    global QUALITY_MAP

    url = url_entry.get()
    if not url:
        progress_label.configure(text="Enter a valid URL first.", text_color="red")
        return

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        available_qualities = {}

        for fmt in formats:
            height = fmt.get("height")
            format_id = fmt.get("format_id")

            if height in [1080, 720, 480]:  # Consider only these resolutions
                available_qualities[f"{height}p"] = format_id

        if not available_qualities:
            progress_label.configure(text="No valid formats found.", text_color="red")
            return

        QUALITY_MAP.clear()
        QUALITY_MAP.update(available_qualities)

        quality_dropdown.configure(values=list(QUALITY_MAP.keys()))
        quality_var.set(next(iter(QUALITY_MAP.keys())))  # Set the first available option
        progress_label.configure(text="Formats fetched successfully!", text_color="green")

    except Exception as e:
        progress_label.configure(text=f"Error: {str(e)}", text_color="red")

# Function to update progress bar
def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        
        if total_bytes:
            percent = downloaded_bytes / total_bytes
            progress_bar.set(percent)  # Update progress bar
            progress_label.configure(text=f"{int(percent * 100)}%", text_color="yellow")
        else:
            progress_bar.set(0)  # Reset progress bar
            progress_label.configure(text="")  # Hide text at start

    elif d['status'] == 'finished':
        progress_bar.set(1)  # Set progress bar to full
        progress_label.configure(text="Download complete!", text_color="green")
        progress_bar.pack_forget()  # Hide progress bar after completion

# Function to download video in a separate thread
def threaded_download():
    url = url_entry.get()
    quality = quality_var.get()
    format_code = QUALITY_MAP.get(quality)

    if not url or format_code is None:
        progress_label.configure(text="Enter a valid URL and select quality.", text_color="red")
        return

    ydl_opts = {
        'format': f"{format_code}+140",
        'outtmpl': os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'quiet': True,  # Suppress terminal output
    }

    try:
        progress_bar.set(0)  # Reset progress bar
        progress_bar.pack(pady=10)  # Show progress bar before starting
        progress_label.configure(text="")  # Hide text at start
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        progress_label.configure(text=f"Error: {str(e)}", text_color="red")
        progress_bar.pack_forget()  # Hide progress bar on error

# Function to start the download in a separate thread
def download_video():
    thread = threading.Thread(target=threaded_download)
    thread.start()

# UI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("YouTube Video Downloader")
root.geometry("450x400")

ctk.CTkLabel(root, text="YouTube URL:", font=("Arial", 14)).pack(pady=10)
url_entry = ctk.CTkEntry(root, width=350)
url_entry.pack(pady=5)

fetch_button = ctk.CTkButton(root, text="Fetch Formats", command=fetch_formats)
fetch_button.pack(pady=10)

ctk.CTkLabel(root, text="Select Quality:", font=("Arial", 14)).pack(pady=5)
quality_var = ctk.StringVar(value="Select Format")
quality_dropdown = ctk.CTkComboBox(root, values=[], variable=quality_var)
quality_dropdown.pack(pady=5)

download_button = ctk.CTkButton(root, text="Download", command=download_video)
download_button.pack(pady=20)

# Modern progress bar (Initially hidden)
progress_bar = ctk.CTkProgressBar(root, width=300)
progress_bar.set(0)  # Set initial progress to 0
progress_bar.pack_forget()  # Hide progress bar initially

progress_label = ctk.CTkLabel(root, text="", font=("Arial", 12))
progress_label.pack(pady=10)

root.mainloop()
