# Musical Recording Captioning

Caption recordings of musical theater, concerts, or any video that has lyrics on Genius.

## How it works

1. Fetches all track lyrics for an album from the [Genius API](https://genius.com/api-clients)
2. Transcribes the audio locally using [Whisper](https://github.com/openai/whisper) (via `faster-whisper`) to get word-level timestamps
3. Fuzzy-matches each lyric line to the transcript to determine timing
4. Writes a `.srt` subtitle file

All processing after the initial Genius lyrics fetch runs entirely offline.

## Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installed and on your `PATH`
- A Genius API access token — get one at https://genius.com/api-clients

## Installation

```bash
pip install musicalrecordingcaptioning
```

Or from source:

```bash
git clone https://github.com/you/MusicalRecordingCaptioning
cd MusicalRecordingCaptioning
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

The installer automatically downloads the default Whisper model (`small`) so the first run works offline.

## Configuration

Copy `.env.example` to `.env` and fill in your token:

```
GENIUS_ACCESS_TOKEN=your_token_here
```

Or pass it directly via `--genius-token`.

## Usage

```bash
# Basic usage (token from .env, auto-detects language)
mrc recording.mp4 --url https://genius.com/albums/Lin-manuel-miranda/Hamilton

# Specify language explicitly for faster, more accurate transcription
mrc recording.mp4 --url https://genius.com/albums/Lin-manuel-miranda/Hamilton --language en

# French show
mrc spectacle.mp4 --url https://genius.com/albums/... --language fr

# Specify output file and a larger model for better accuracy
mrc show.mp4 --url https://genius.com/albums/Claude-michel-schonberg/Les-miserables-original-broadway-cast-recording \
    --output les-mis.srt --model medium --language fr

# Pass token explicitly
mrc concert.mp3 --url https://genius.com/albums/Anais-mitchell/Hadestown \
    --genius-token abc123
```

### Options

| Option | Default | Description |
|---|---|---|
| `--url` | required | Genius album URL (`https://genius.com/albums/...`) |
| `--genius-token` | from `.env` | Genius API access token |
| `--output` | `<input>.srt` | Output SRT file path |
| `--model` | `small` | Whisper model: `tiny`, `base`, `small`, `medium`, `large` |
| `--language` | auto-detect | Audio language as ISO 639-1 code (e.g. `en`, `fr`, `de`) |

### Whisper models

| Model | Size | Notes |
|---|---|---|
| `tiny` | ~75 MB | Fastest, least accurate |
| `base` | ~145 MB | Good for clear speech |
| `small` | ~466 MB | **Default.** Handles singing and background music well |
| `medium` | ~1.5 GB | High accuracy, slower |
| `large` | ~3.1 GB | Best accuracy, slow |

Only the `small` model is downloaded at install time. Other models are downloaded on first use when specified via `--model`.
