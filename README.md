# Musical Recording Captioning

Caption recordings of musical theater, concerts, or any video that has lyrics on Genius.

## How it works

1. Fetches all track lyrics for an album from the [Genius API](https://genius.com/api-clients)
2. Transcribes the audio using [OpenAI Whisper](https://github.com/openai/whisper) (via `stable-ts`) to get word-level timestamps
3. Fuzzy-matches each lyric line to the transcript to determine timing
4. Writes a `.srt` subtitle file

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

## Configuration

Copy `.env.example` to `.env` and fill in your token:

```
GENIUS_ACCESS_TOKEN=your_token_here
```

Or pass it directly via `--genius-token`.

## Usage

```bash
# Basic usage (token from .env)
mrc recording.mp4 --url https://genius.com/albums/Lin-manuel-miranda/Hamilton

# Specify output file and a larger Whisper model for better accuracy
mrc show.mp4 --url https://genius.com/albums/Claude-michel-schonberg/Les-miserables-original-broadway-cast-recording \
    --output les-mis.srt --model medium

# Pass token explicitly
mrc concert.mp3 --url https://genius.com/albums/Anaïs-mitchell/Hadestown \
    --genius-token abc123
```

### Options

| Option | Default | Description |
|---|---|---|
| `--url` | required | Genius album URL (`https://genius.com/albums/...`) |
| `--genius-token` | from `.env` | Genius API access token |
| `--output` | `<input>.srt` | Output SRT file path |
| `--model` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large` |

Larger Whisper models are more accurate but slower. `base` works well for most recordings; use `medium` or `large` for noisy or complex audio.
