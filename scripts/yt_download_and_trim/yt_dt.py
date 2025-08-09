#!/usr/bin/env python3
"""
YouTube Download and Trim Script

This script downloads audio from YouTube videos and trims them to specified time intervals.

Requirements:
- yt-dlp: pip install yt-dlp
- pydub: pip install pydub
- ffmpeg: brew install ffmpeg (on macOS) or equivalent on other platforms

Usage:
    python yt_dt.py <youtube_url> <start_time> <end_time> [--output output_file.mp3]

    # Basic usage - trim from 30 seconds to 2:15
    python yt_dt.py "https://youtube.com/watch?v=VIDEO_ID" 0:30 2:15
    python yt_dt.py "https://www.youtube.com/watch?v=YJEusVsXiZA" 2:27:00 2:35:20

    # Using seconds only
    python yt_dt.py "https://youtube.com/watch?v=VIDEO_ID" 30 135

    # Custom output filename
    python yt_dt.py "https://youtube.com/watch?v=VIDEO_ID" 1:30 2:45 --output my_clip.mp3

    # Keep temporary full download
    python yt_dt.py "https://youtube.com/watch?v=VIDEO_ID" 0:30 2:15 --keep-temp

Time format: HH:MM:SS or MM:SS or SS
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yt_dlp
    from pydub import AudioSegment
except ImportError as e:
    print(f"Error: Missing required package. Please install: {e.name}")
    print("Run: pip install yt-dlp pydub")
    sys.exit(1)


def parse_time_to_seconds(time_str: str) -> int:
    """
    Convert time string to seconds.
    Accepts formats: HH:MM:SS, MM:SS, or SS
    """
    parts = time_str.split(":")

    if len(parts) == 1:
        # SS format
        return int(parts[0])
    elif len(parts) == 2:
        # MM:SS format
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        # HH:MM:SS format
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM:SS, MM:SS, or SS")


def download_youtube_audio(url: str, output_dir: str = "temp") -> str:
    """
    Download audio from YouTube video.
    Returns the path to the downloaded audio file.
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Configure yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")

            # Clean title for filename
            clean_title = re.sub(r"[^\w\s-]", "", title).strip()
            clean_title = re.sub(r"[-\s]+", "-", clean_title)

            # Download the audio
            ydl.download([url])

            # Find the downloaded file
            expected_filename = f"{output_dir}/{clean_title}.mp3"

            # Sometimes the filename might be slightly different, so search for it
            mp3_files = list(Path(output_dir).glob("*.mp3"))

            # First try exact match with cleaned title
            for file in mp3_files:
                if clean_title.lower() in file.stem.lower():
                    return str(file)

            # If no match found with cleaned title, try matching with original title words
            title_words = title.lower().split()
            for file in mp3_files:
                file_stem_lower = file.stem.lower()
                # Check if most title words are in the filename
                matches = sum(1 for word in title_words if word in file_stem_lower)
                if matches >= len(title_words) * 0.7:  # 70% of words match
                    return str(file)

            # If still no match, return the most recently created mp3 file
            if mp3_files:
                newest_file = max(mp3_files, key=lambda f: f.stat().st_mtime)
                return str(newest_file)

            # If exact match not found, return the expected filename
            return expected_filename

    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")


def trim_audio(input_file: str, start_seconds: int, end_seconds: int, output_file: str):
    """
    Trim audio file to specified time interval.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_mp3(input_file)

        # Convert seconds to milliseconds
        start_ms = start_seconds * 1000
        end_ms = end_seconds * 1000

        # Validate time bounds
        if start_ms >= len(audio):
            raise ValueError(
                f"Start time ({start_seconds}s) exceeds audio duration ({len(audio)//1000}s)"
            )

        if end_ms > len(audio):
            print(
                f"Warning: End time ({end_seconds}s) exceeds audio duration ({len(audio)//1000}s). Using full duration."
            )
            end_ms = len(audio)

        if start_ms >= end_ms:
            raise ValueError("Start time must be less than end time")

        # Trim the audio
        trimmed_audio = audio[start_ms:end_ms]

        # Export the trimmed audio
        trimmed_audio.export(output_file, format="mp3")
        print(f"Successfully created trimmed audio: {output_file}")
        print(f"Duration: {(end_ms - start_ms) // 1000} seconds")

    except Exception as e:
        raise Exception(f"Failed to trim audio: {str(e)}")


def cleanup_temp_file(file_path: str):
    """Remove temporary file if it exists."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        print(f"Warning: Could not remove temporary file {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube audio and trim to specified time interval",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 0:30 2:15
  python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 30 135 --output my_clip.mp3
  python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 1:30:45 1:33:20

Time formats supported: HH:MM:SS, MM:SS, or SS (seconds only)
        """,
    )

    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("start_time", help="Start time (HH:MM:SS, MM:SS, or SS)")
    parser.add_argument("end_time", help="End time (HH:MM:SS, MM:SS, or SS)")
    parser.add_argument(
        "--output", "-o", help="Output filename (default: auto-generated)"
    )
    parser.add_argument(
        "--keep-temp", action="store_true", help="Keep temporary downloaded file"
    )

    args = parser.parse_args()

    try:
        # Parse time arguments
        start_seconds = parse_time_to_seconds(args.start_time)
        end_seconds = parse_time_to_seconds(args.end_time)

        if start_seconds >= end_seconds:
            print("Error: Start time must be less than end time")
            sys.exit(1)

        print(f"Downloading audio from: {args.url}")
        print(
            f"Time range: {args.start_time} to {args.end_time} ({end_seconds - start_seconds} seconds)"
        )

        # Download the audio
        temp_audio_file = download_youtube_audio(args.url)
        print(f"Downloaded: {temp_audio_file}")

        # Generate output filename if not provided
        if args.output:
            output_file = args.output
        else:
            base_name = Path(temp_audio_file).stem
            output_file = f"{base_name}_trimmed_{args.start_time.replace(':', '-')}_to_{args.end_time.replace(':', '-')}.mp3"

        # Trim the audio
        trim_audio(temp_audio_file, start_seconds, end_seconds, output_file)

        # Cleanup temporary file unless user wants to keep it
        if not args.keep_temp:
            cleanup_temp_file(temp_audio_file)

        print(f"\n✅ Success! Trimmed audio saved as: {output_file}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
