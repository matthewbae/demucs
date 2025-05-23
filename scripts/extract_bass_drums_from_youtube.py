# In the demucs virtualenv, run this first to generate stems
# python3 -m demucs -d cpu --jobs 2 --mp3 [name-of-mp3].mp3
#
# Make sure you have already installed ffmpeg and demucs
# pip install demucs
# brew install ffmpeg
import subprocess
import sys

import yt_dlp
from pydub import AudioSegment

youtube_url = sys.argv[1]


def download_youtube_mp3(url: str, output_dir: str = ".") -> str:
    output_template = f"{output_dir}/%(title)s.%(ext)s"
    info = None

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    if info:
        title = info.get("title", "unknown_title")
        filename = f"{title}.mp3"
        return title, filename
    else:
        raise RuntimeError("Failed to download or extract YouTube info.")


def separate_audio_with_demucs(file_path: str):
    try:
        subprocess.run(
            ["python3", "-m", "demucs", "-d", "cpu", "--jobs", "2", "--mp3", file_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Demucs failed: {e}")


print("Downloading YouTube audio...")
title, file_name = download_youtube_mp3(youtube_url)

print("Extracting stems...")
separate_audio_with_demucs(file_name)

print("Overlaying bass & drum stems...")
audio1 = AudioSegment.from_file(f"./separated/htdemucs/{title}/bass.mp3")
audio2 = AudioSegment.from_file(f"./separated/htdemucs/{title}/drums.mp3")

# Overlay audio2 on top of audio1 starting at the beginning (position=0)
combined = audio1.overlay(audio2)

# Export result
combined.export(f"{title}_bass_and_drums.mp3", format="mp3")
print("Done")
