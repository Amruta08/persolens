import yt_dlp
import tempfile
import os

def download_audio(youtube_url:str) -> str:
    tmp_dir = tempfile.mkdtemp()
    output_path = os.path.join(tmp_dir, "audio.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    return os.path.join(tmp_dir, "audio.wav")