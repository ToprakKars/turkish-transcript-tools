import unittest

from transcript_tools.core import (
    analyse,
    clean_text,
    clean_transcript,
    count_words,
    fix_encoding,
    parse_line,
    turkish_lower,
)


class TestText(unittest.TestCase):
    def test_turkish_lower(self):
        self.assertEqual(turkish_lower("IŞIK İSTANBUL"), "ışık istanbul")

    def test_fix_encoding(self):
        self.assertEqual(fix_encoding("GÃ¼naydÄ±n"), "Günaydın")

    def test_clean_text_spacing(self):
        self.assertEqual(clean_text("Merhaba ,  nasılsın ?İyiyim."), "Merhaba, nasılsın? İyiyim.")

    def test_count_words_with_turkish_letters(self):
        self.assertEqual(count_words("Çok güzel, değil mi?"), 4)


class TestParsing(unittest.TestCase):
    def test_parse_full_line(self):
        line = parse_line("[00:01:05] Ayşe: Selam herkese", 1)
        self.assertEqual(line.seconds, 65)
        self.assertEqual(line.speaker, "Ayşe")
        self.assertEqual(line.text, "Selam herkese")

    def test_parse_plain_line(self):
        line = parse_line("Sadece metin", 1)
        self.assertIsNone(line.seconds)
        self.assertIsNone(line.speaker)


class TestAnalyse(unittest.TestCase):
    def test_stats_and_problems(self):
        text = (
            "[00:00:01] A: Merhaba nasılsın\n"
            "[00:00:05] B: İyiyim teşekkürler\n"
            "[00:00:03] A: Geri giden zaman\n"
            "[0:1] B: bozuk\n"
        )
        report = analyse(text)
        self.assertEqual(report.lines, 4)
        self.assertEqual(report.words_per_speaker["A"], 5)
        self.assertIn("line 3: timestamp goes backwards", report.problems)
        self.assertIn("line 4: malformed timestamp", report.problems)

    def test_clean_transcript_keeps_structure(self):
        text = "[00:00:01] A:   Merhaba ,dÃ¼nya\n\n"
        self.assertEqual(clean_transcript(text), "[00:00:01] A: Merhaba, dünya\n")


if __name__ == "__main__":
    unittest.main()
