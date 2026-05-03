from dataclasses import dataclass
from pathlib import Path
import ffmpeg
import tempfile
from faster_whisper import WhisperModel
from huggingface_hub.utils import LocalEntryNotFoundError
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TaskProgressColumn


@dataclass
class Word:
    text: str
    start: float
    end: float


def extract_audio(media_path: Path) -> Path:
    suffix = media_path.suffix.lower()
    audio_formats = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"}
    if suffix in audio_formats:
        return media_path

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    out_path = Path(tmp.name)
    ffmpeg.input(str(media_path)).output(str(out_path), ac=1, ar=16000).overwrite_output().run(
        quiet=True
    )
    return out_path


def _load_model(model_name: str) -> WhisperModel:
    try:
        return WhisperModel(model_name, device="auto", compute_type="int8", local_files_only=True)
    except (LocalEntryNotFoundError, Exception) as e:
        if "local_files_only" in str(e) or "not found" in str(e).lower() or "Entry Not Found" in str(e):
            raise RuntimeError(
                f"Whisper model '{model_name}' is not available locally.\n"
                f"Download it by running:  pip install -e . --force-reinstall\n"
                f"(or re-run setup to fetch the model)"
            ) from None
        raise


def transcribe(media_path: Path, model_name: str = "small", language: str | None = None) -> list[Word]:
    audio_path = extract_audio(media_path)
    model = _load_model(model_name)
    segments, info = model.transcribe(str(audio_path), word_timestamps=True, language=language)
    duration = info.duration

    words: list[Word] = []
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("Transcribing...", total=duration)
        for segment in segments:
            for w in segment.words:
                text = w.word.strip()
                if text:
                    words.append(Word(text=text, start=w.start, end=w.end))
            progress.update(task, completed=segment.end)

    return words
