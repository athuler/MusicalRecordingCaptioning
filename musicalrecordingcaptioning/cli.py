from pathlib import Path
from typing import Annotated
import typer
from .config import resolve_genius_token
from .genius import fetch_album_lyrics, _parse_genius_album_url
from .transcribe import transcribe
from .align import align
from .srt_writer import write_srt

app = typer.Typer(add_completion=False)


@app.command()
def main(
    file: Annotated[Path, typer.Argument(help="Path to video or audio file")],
    url: Annotated[str, typer.Option(help="Genius album URL (https://genius.com/albums/...)")],
    genius_token: Annotated[
        str | None, typer.Option("--genius-token", help="Genius API access token")
    ] = None,
    output: Annotated[
        Path | None, typer.Option(help="Output .srt file path (default: <input>.srt)")
    ] = None,
    model: Annotated[
        str, typer.Option(help="Whisper model size: tiny, base, small, medium, large")
    ] = "base",
) -> None:
    if not file.exists():
        typer.echo(f"Error: file not found: {file}", err=True)
        raise typer.Exit(1)

    out_path = output or file.with_suffix(".srt")

    try:
        token = resolve_genius_token(genius_token)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    try:
        artist, album = _parse_genius_album_url(url)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Fetching lyrics for '{album}' by '{artist}'...")
    songs = fetch_album_lyrics(url, token)
    typer.echo(f"  Found {len(songs)} tracks.")

    typer.echo(f"Transcribing '{file}' with Whisper model '{model}'...")
    words = transcribe(file, model)
    typer.echo(f"  Transcribed {len(words)} words.")

    typer.echo("Aligning lyrics to transcript...")
    captions = align(songs, words)
    typer.echo(f"  Generated {len(captions)} caption lines.")

    write_srt(captions, out_path)
    typer.echo(f"SRT written to: {out_path}")
