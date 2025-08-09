# YouTube Download and Trim Script

A Python script that downloads audio from YouTube videos and trims them to specified time intervals.

## Prerequisites

1. **Python 3.7+**
2. **FFmpeg** - Required for audio processing
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python yt_dt.py <youtube_url> <start_time> <end_time>
```

### Examples

1. **Download and trim from 30 seconds to 2 minutes 15 seconds:**

```bash
python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 0:30 2:15
```

2. **Using seconds only:**

```bash
python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 30 135
```

3. **Specify custom output filename:**

```bash
python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 1:30 2:45 --output my_clip.mp3
```

4. **Keep the temporary full download:**

```bash
python yt_dt.py "https://youtube.com/watch?v=dQw4w9WgXcQ" 0:30 2:15 --keep-temp
```

### Time Formats Supported

- **Seconds only:** `30` (30 seconds)
- **Minutes:Seconds:** `1:30` (1 minute 30 seconds)
- **Hours:Minutes:Seconds:** `1:30:45` (1 hour 30 minutes 45 seconds)

### Command Line Options

- `--output, -o`: Specify output filename (default: auto-generated)
- `--keep-temp`: Keep the temporary full audio download
- `--help`: Show help message

## Features

- Downloads high-quality audio from YouTube videos
- Supports various time formats for flexibility
- Automatically cleans up temporary files
- Provides detailed progress and error messages
- Validates time ranges and audio duration
- Generates descriptive output filenames

## Error Handling

The script includes comprehensive error handling for:

- Invalid YouTube URLs
- Network connection issues
- Invalid time formats
- Time ranges that exceed video duration
- Missing dependencies
- File system permissions

## Dependencies

- **yt-dlp**: Modern YouTube downloader
- **pydub**: Audio manipulation library
- **ffmpeg**: Audio/video processing (system dependency)
