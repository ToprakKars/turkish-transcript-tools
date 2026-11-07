"""Core helpers for cleaning and checking Turkish transcripts.

A transcript line is expected to look like:

    [00:01:23] Speaker A: Merhaba, nasılsınız?

The timestamp and the speaker label are optional.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

TIMESTAMP_RE = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\s*")
SPEAKER_RE = re.compile(r"^([^:\[\]]{1,40}):(?:\s+|$)")
WORD_RE = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşüâîûÂÎÛ']+")

# Common characters that appear when Turkish text is typed on a non-Turkish keyboard
# or copied from a badly encoded file.
ENCODING_FIXES = {
    "Ã§": "ç", "Ã‡": "Ç",
    "ÄŸ": "ğ", "Äž": "Ğ",
    "Ä±": "ı", "Ä°": "İ",
    "Ã¶": "ö", "Ã–": "Ö",
    "ÅŸ": "ş", "Åž": "Ş",
    "Ã¼": "ü", "Ãœ": "Ü",
}


@dataclass
class Line:
    number: int
    seconds: int | None
    speaker: str | None
    text: str


@dataclass
class Report:
    lines: int = 0
    words: int = 0
    words_per_speaker: Counter = field(default_factory=Counter)
    problems: list[str] = field(default_factory=list)


def turkish_lower(text: str) -> str:
    """Lowercase text using Turkish rules (I -> ı, İ -> i)."""
    return text.replace("I", "ı").replace("İ", "i").lower()


def fix_encoding(text: str) -> str:
    """Repair common mojibake for Turkish characters."""
    for broken, correct in ENCODING_FIXES.items():
        text = text.replace(broken, correct)
    return text


def clean_text(text: str) -> str:
    """Fix encoding, collapse whitespace and tidy spaces around punctuation."""
    text = fix_encoding(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])(?=[^\s\d.,!?;:\"')\]])", r"\1 ", text)
    return text


def parse_line(raw: str, number: int) -> Line:
    seconds = None
    match = TIMESTAMP_RE.match(raw)
    if match:
        h, m, s = (int(x) for x in match.groups())
        seconds = h * 3600 + m * 60 + s
        raw = raw[match.end():]
    speaker = None
    match = SPEAKER_RE.match(raw)
    if match:
        speaker = match.group(1).strip()
        raw = raw[match.end():]
    return Line(number=number, seconds=seconds, speaker=speaker, text=raw.strip())


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def analyse(text: str) -> Report:
    """Parse a whole transcript and collect stats and problems."""
    report = Report()
    last_seconds = -1
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        line = parse_line(raw, number)
        report.lines += 1
        words = count_words(line.text)
        report.words += words
        report.words_per_speaker[line.speaker or "(unknown)"] += words

        if line.seconds is not None:
            if line.seconds < last_seconds:
                report.problems.append(f"line {number}: timestamp goes backwards")
            last_seconds = line.seconds
        if raw.lstrip().startswith("[") and line.seconds is None:
            report.problems.append(f"line {number}: malformed timestamp")
        if not line.text:
            report.problems.append(f"line {number}: empty text")
        if any(bad in raw for bad in ENCODING_FIXES):
            report.problems.append(f"line {number}: broken Turkish characters")
    return report


def format_timestamp(seconds: int) -> str:
    h, rest = divmod(seconds, 3600)
    m, s = divmod(rest, 60)
    return f"[{h:02d}:{m:02d}:{s:02d}]"


def clean_transcript(text: str) -> str:
    """Return a cleaned copy of the transcript, keeping timestamps and speakers."""
    out = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        line = parse_line(raw, number)
        parts = []
        if line.seconds is not None:
            parts.append(format_timestamp(line.seconds))
        if line.speaker:
            parts.append(f"{line.speaker}:")
        parts.append(clean_text(line.text))
        out.append(" ".join(parts))
    return "\n".join(out) + "\n"
