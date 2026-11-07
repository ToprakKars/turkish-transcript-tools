# Turkish Transcript Tools

A small Python command-line tool for cleaning and checking Turkish transcripts — the kind of quality checks I do by hand when transcribing Turkish audio (podcasts, interviews, conversations).

No external dependencies, only the Python standard library.

![Output of the check command](https://raw.githubusercontent.com/ToprakKars/ToprakKars/main/assets/transcript-check.png)

## What it does

**`check`** – reads a transcript and reports:
- number of lines and words
- words per speaker
- timestamps that go backwards or are malformed
- lines with no text
- broken Turkish characters from bad encoding (e.g. `Ã¼` instead of `ü`)

**`clean`** – writes a tidied copy:
- repairs broken Turkish characters (`ç ğ ı İ ö ş ü`)
- collapses extra spaces
- fixes spacing around punctuation (`Merhaba ,nasılsın ?` → `Merhaba, nasılsın?`)
- keeps timestamps and speaker labels

It also handles Turkish-specific casing (`I → ı`, `İ → i`), which Python's default `lower()` gets wrong.

## Transcript format

```
[00:00:01] Ayşe: Herkese merhaba, bugün podcastimize hoş geldiniz.
[00:00:06] Mehmet: Merhaba Ayşe!
```

Timestamps (`[hh:mm:ss]`) and speaker labels are optional.

## Usage

```bash
python -m transcript_tools check example.txt
python -m transcript_tools clean example.txt -o cleaned.txt
```

Example output of `check example.txt`:

```
Lines: 4
Words: 19
Words per speaker:
  Ayşe            11
  Mehmet          8

3 problem(s) found:
  - line 2: broken Turkish characters
  - line 3: timestamp goes backwards
  - line 4: empty text
```

`check` exits with code `1` when problems are found, so it can be used in scripts.

## Tests

```bash
python -m unittest discover -s tests -t .
```

Tests run automatically on every push with GitHub Actions.

## Project structure

```
transcript_tools/
  core.py      parsing, cleaning and analysis
  cli.py       command-line interface (argparse)
tests/
  test_core.py unit tests
example.txt    sample transcript with a few mistakes
```
