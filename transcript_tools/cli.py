"""Command-line interface.

Usage:
    python -m transcript_tools check  transcript.txt
    python -m transcript_tools clean  transcript.txt -o cleaned.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import analyse, clean_transcript


def cmd_check(path: Path) -> int:
    report = analyse(path.read_text(encoding="utf-8"))
    print(f"Lines: {report.lines}")
    print(f"Words: {report.words}")
    print("Words per speaker:")
    for speaker, words in report.words_per_speaker.most_common():
        print(f"  {speaker:<15} {words}")
    if report.problems:
        print(f"\n{len(report.problems)} problem(s) found:")
        for problem in report.problems:
            print(f"  - {problem}")
        return 1
    print("\nNo problems found.")
    return 0


def cmd_clean(path: Path, output: Path | None) -> int:
    cleaned = clean_transcript(path.read_text(encoding="utf-8"))
    if output:
        output.write_text(cleaned, encoding="utf-8")
        print(f"Cleaned transcript written to {output}")
    else:
        sys.stdout.write(cleaned)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="transcript_tools", description="Clean and check Turkish transcripts.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="show stats and find problems")
    check.add_argument("file", type=Path)

    clean = sub.add_parser("clean", help="fix spacing, punctuation and broken characters")
    clean.add_argument("file", type=Path)
    clean.add_argument("-o", "--output", type=Path)

    args = parser.parse_args(argv)
    if args.command == "check":
        return cmd_check(args.file)
    return cmd_clean(args.file, args.output)
