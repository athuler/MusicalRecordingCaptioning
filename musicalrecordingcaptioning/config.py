import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")


def resolve_genius_token(cli_token: str | None) -> str:
    token = cli_token or os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "Genius API token required. Set GENIUS_ACCESS_TOKEN in .env or pass --genius-token."
        )
    return token
