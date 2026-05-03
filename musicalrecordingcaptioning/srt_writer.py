from datetime import timedelta
from pathlib import Path
import srt
from .align import CaptionLine


def write_srt(captions: list[CaptionLine], output_path: Path) -> None:
    subtitles = [
        srt.Subtitle(
            index=i + 1,
            start=timedelta(seconds=c.start),
            end=timedelta(seconds=c.end),
            content=c.text,
        )
        for i, c in enumerate(captions)
    ]
    output_path.write_text(srt.compose(subtitles), encoding="utf-8")
