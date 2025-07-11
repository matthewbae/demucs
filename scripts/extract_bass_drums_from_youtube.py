# In the demucs virtualenv, run this:
# python3 ./extract_bass_drums_from_youtube.py "https://music.youtube.com/watch?v=eFHxKcpX4eE&si=kxMeyhqyDoke2i5Z"
#
# Make sure you have already installed ffmpeg and demucs
# pip install demucs
# brew install ffmpeg

import os
import re
import subprocess
import sys
import unicodedata

import yt_dlp
from pydub import AudioSegment

# Characters invalid in file names (Windows/macOS/Linux)
SPECIAL_CHARS = (
    r'[<>:"/\\|?*\x00-\x1F\u2022\u29F8]'  # includes fancy slashes and bullets
)

youtube_url = sys.argv[1]


def normalize_visually(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return (
        s.replace("⧸", "/")  # U+29F8 fancy slash
        .replace("⁄", "/")  # U+2044 fraction slash
        .replace("\u00a0", " ")  # non-breaking space
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .strip()
    )


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

normalized_title = normalize_visually(title)
target_ext = ".mp3"

for f in os.listdir("."):
    print(repr(f))

matching_file = None
for f in os.listdir("."):
    if not f.lower().endswith(target_ext):
        continue

    f_normalized = normalize_visually(f)

    if normalized_title.lower() in f_normalized.lower():
        matching_file = f
        break

if not matching_file:
    raise FileNotFoundError(f"Couldn't find a file matching: {normalized_title}")

# Remove special characters
safe_name = re.sub(SPECIAL_CHARS, "", matching_file)

if matching_file != safe_name:
    os.rename(matching_file, safe_name)
    print(f"Renamed to: {safe_name}")
else:
    print("Filename is already clean.")

print("Extracting stems...")
separate_audio_with_demucs(safe_name)

print("Overlaying bass & drum stems...")
audio1 = AudioSegment.from_file(f"./separated/htdemucs/{title}/bass.mp3")
audio2 = AudioSegment.from_file(f"./separated/htdemucs/{title}/drums.mp3")

# Overlay audio2 on top of audio1 starting at the beginning (position=0)
combined = audio1.overlay(audio2)

# Export result
combined.export(f"{title}_bass_and_drums.mp3", format="mp3")
print("Done")
