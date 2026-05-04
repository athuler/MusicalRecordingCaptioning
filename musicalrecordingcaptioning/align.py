from dataclasses import dataclass
import re
from thefuzz import fuzz
from .genius import Song
from .transcribe import Word


@dataclass
class CaptionLine:
    text: str
    start: float
    end: float


def _normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text).lower().strip()


def _words_to_text(words: list[Word]) -> str:
    return " ".join(w.text for w in words)


def _find_song_start(words: list[Word], song_lines: list[str], search_from: int) -> int:
    """Return the index in `words` where this song likely begins."""
    if not song_lines:
        return search_from

    # build a probe string from first 1-2 lyric lines
    probe = _normalize(" ".join(song_lines[:2]))
    probe_word_count = len(probe.split())
    window = max(probe_word_count, 8)
    best_score = 0
    best_idx = search_from

    for i in range(search_from, len(words) - window + 1):
        candidate = _normalize(_words_to_text(words[i : i + window]))
        score = fuzz.partial_ratio(probe, candidate)
        if score > best_score:
            best_score = score
            best_idx = i
        # stop scanning if we're well past a likely song boundary (5 min of silence)
        if best_score >= 90:
            break

    return best_idx


def _match_line_to_words(
    lyric_line: str, words: list[Word], search_from: int, lookahead: int = 40
) -> tuple[int, int]:
    """
    Return (start_word_idx, end_word_idx) for the best match of lyric_line in
    words[search_from : search_from + lookahead].
    """
    probe = _normalize(lyric_line)
    probe_len = len(probe.split())
    window = max(probe_len, 4)
    end = min(search_from + lookahead, len(words))

    best_score = 0
    best_start = search_from
    best_end = min(search_from + window, len(words))

    for i in range(search_from, end):
        candidate_end = min(i + window, len(words))
        candidate = _normalize(_words_to_text(words[i:candidate_end]))
        score = fuzz.ratio(probe, candidate)
        if score > best_score:
            best_score = score
            best_start = i
            best_end = candidate_end

    return best_start, best_end


def align(songs: list[Song], words: list[Word]) -> list[CaptionLine]:
    captions: list[CaptionLine] = []
    word_cursor = 0

    for song in songs:
        lines = [l for l in song.lyrics if l.strip()]
        if not lines:
            continue

        song_start_idx = _find_song_start(words, lines, word_cursor)

        line_cursor = song_start_idx
        for i, lyric_line in enumerate(lines):
            if line_cursor >= len(words):
                break

            # lookahead grows for longer lines; cap to avoid runaway search
            lookahead = max(60, len(lyric_line.split()) * 6)
            start_idx, end_idx = _match_line_to_words(lyric_line, words, line_cursor, lookahead)

            start_time = words[start_idx].start
            end_time = words[min(end_idx, len(words) - 1)].end

            # end time = start of next line if available, otherwise word end
            captions.append(CaptionLine(text=f"♪ {lyric_line} ♪", start=start_time, end=end_time))
            line_cursor = max(line_cursor + 1, end_idx)

        word_cursor = line_cursor

    # fix overlapping end/start times
    for i in range(len(captions) - 1):
        if captions[i].end > captions[i + 1].start:
            captions[i].end = captions[i + 1].start

    return captions


def _words_to_transcript_lines(
    words: list[Word], max_words: int = 8, pause_threshold: float = 0.6
) -> list[CaptionLine]:
    """Group a flat word list into caption lines, splitting on pauses or word count."""
    lines: list[CaptionLine] = []
    group: list[Word] = []

    for i, word in enumerate(words):
        group.append(word)
        gap_after = (words[i + 1].start - word.end) if i + 1 < len(words) else pause_threshold + 1
        if len(group) >= max_words or gap_after >= pause_threshold:
            lines.append(CaptionLine(
                text=" ".join(w.text for w in group),
                start=group[0].start,
                end=group[-1].end,
            ))
            group = []

    if group:
        lines.append(CaptionLine(
            text=" ".join(w.text for w in group),
            start=group[0].start,
            end=group[-1].end,
        ))

    return lines


def fill_gaps(
    captions: list[CaptionLine], words: list[Word], min_gap: float = 1.0
) -> list[CaptionLine]:
    """Insert transcript-based captions into time ranges not covered by lyric captions."""
    if not captions:
        return _words_to_transcript_lines(words)

    covered: list[tuple[float, float]] = [(c.start, c.end) for c in captions]
    word_idx = 0
    gap_captions: list[CaptionLine] = []

    def _collect_gap(gap_start: float, gap_end: float) -> None:
        nonlocal word_idx
        if gap_end - gap_start < min_gap:
            return
        gap_words: list[Word] = []
        while word_idx < len(words) and words[word_idx].start < gap_start:
            word_idx += 1
        while word_idx < len(words) and words[word_idx].end <= gap_end:
            gap_words.append(words[word_idx])
            word_idx += 1
        gap_captions.extend(_words_to_transcript_lines(gap_words))

    # gap before first caption
    _collect_gap(0.0, covered[0][0])

    # gaps between captions
    for i in range(len(covered) - 1):
        _collect_gap(covered[i][1], covered[i + 1][0])

    # gap after last caption
    if words:
        _collect_gap(covered[-1][1], words[-1].end)

    merged = sorted(captions + gap_captions, key=lambda c: c.start)
    return merged
