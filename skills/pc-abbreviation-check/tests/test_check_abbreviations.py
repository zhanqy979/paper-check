import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_abbreviations.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_abbreviations", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AbbreviationCheckTests(unittest.TestCase):
    def test_splits_sections_counts_uses_and_reports_duplicates(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "main.tex"
            section = root / "section.tex"
            main.write_text(
                "\\begin{document}\n"
                "\\begin{abstract}\n"
                "orthogonal frequency-division multiplexing (OFDM) improves links. OFDM is useful.\n"
                "\\end{abstract}\n"
                "\\input{section}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            section.write_text(
                "\\section{Method}\n"
                "multiple-input multiple-output (MIMO) is used. MIMO and MIMO-based designs follow.\n"
                "orthogonal frequency-division multiplexing (OFDM) is defined again. OFDM follows.\n"
                "channel state information (CSI) is estimated.\n",
                encoding="utf-8",
            )

            report = checker.analyze_project(main)

        abstract = report["sections"]["abstract"]["definitions"]
        body = report["sections"]["other"]["definitions"]
        self.assertEqual([(row["abbreviation"], row["occurrences"]) for row in abstract], [("OFDM", 1)])
        self.assertEqual(
            [(row["abbreviation"], row["occurrences"]) for row in body],
            [("MIMO", 2), ("OFDM", 1), ("CSI", 0)],
        )
        self.assertEqual(report["sections"]["other"]["unused"][0]["abbreviation"], "CSI")
        duplicate = report["global"]["duplicate_definitions"][0]
        self.assertEqual((duplicate["abbreviation"], duplicate["definition_count"]), ("OFDM", 2))
        self.assertTrue(all(item["file"] and item["line"] > 0 for item in duplicate["locations"]))

    def test_flags_title_case_but_allows_known_proper_name_shape(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "\\begin{abstract}\n"
                "Orthogonal Frequency-Division Multiplexing (OFDM) is considered.\n"
                "New York University (NYU) participates.\n"
                "\\end{abstract}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            report = checker.analyze_project(main)

        issues = report["sections"]["abstract"]["capitalization_issues"]
        self.assertTrue(any(item["abbreviation"] == "OFDM" for item in issues))
        self.assertFalse(any(item["abbreviation"] == "NYU" for item in issues))

    def test_markdown_contains_two_required_tables_and_statistics(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "\\begin{abstract}\n"
                "orthogonal frequency-division multiplexing (OFDM) appears.\n"
                "\\end{abstract}\n"
                "multiple-input multiple-output (MIMO) appears.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            markdown = checker.render_markdown(checker.analyze_project(main))

        self.assertIn("## 摘要", markdown)
        self.assertIn("## 其他正文", markdown)
        self.assertEqual(markdown.count("| 序号 | 全称 | 缩写 | 出现次数 |"), 2)
        self.assertIn("### 重复定义的缩写", markdown)
        self.assertIn("### 定义后未再出现的缩写", markdown)
        self.assertIn("### 全称大小写规范检查", markdown)

    def test_ignores_comments_and_supports_plural_abbreviations(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "% fake access points (APs) APs APs\n"
                "access points (APs) are deployed. APs cooperate.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            report = checker.analyze_project(main)

        rows = report["sections"]["other"]["definitions"]
        self.assertEqual([(row["abbreviation"], row["occurrences"]) for row in rows], [("APs", 1)])

    def test_merges_non_strict_candidates_into_final_tables_and_duplicates(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "\\begin{abstract}\n"
                "low-rank adaptation (LoRA) is efficient. LoRA is reused.\n"
                "\\end{abstract}\n"
                "demodulation reference signals (DMRS) are inserted. DMRS assists estimation.\n"
                "Later, demodulation reference signals (DMRS) are described again. DMRS follows.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            report = checker.analyze_project(main)

        abstract = report["sections"]["abstract"]["definitions"]
        body = report["sections"]["other"]["definitions"]
        self.assertEqual(
            [(row["full_name"], row["abbreviation"], row["occurrences"]) for row in abstract],
            [("low-rank adaptation", "LoRA", 1)],
        )
        self.assertEqual(
            [(row["full_name"], row["abbreviation"], row["occurrences"]) for row in body],
            [
                ("demodulation reference signals", "DMRS", 2),
                ("demodulation reference signals", "DMRS", 2),
            ],
        )
        duplicate = next(
            item
            for item in report["global"]["duplicate_definitions"]
            if item["abbreviation"] == "DMRS"
        )
        self.assertEqual(duplicate["definition_count"], 2)
        candidates = report["global"]["candidate_definitions"]
        self.assertEqual(
            [item["abbreviation"] for item in candidates],
            ["LoRA", "DMRS", "DMRS"],
        )

    def test_candidate_scan_rejects_lowercase_parenthetical_prose(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "The cyclic prefix length (samples) is listed near the center frequency (center).\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            report = checker.analyze_project(main)

        self.assertEqual(report["sections"]["other"]["definitions"], [])

    def test_markdown_states_that_tables_merge_strict_and_candidate_definitions(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                "\\begin{document}\n"
                "demodulation reference signals (DMRS) are used.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            markdown = checker.render_markdown(checker.analyze_project(main))

        self.assertIn("严格匹配与候选扫描已合并", markdown)
        self.assertIn("| 1 | demodulation reference signals | DMRS | 0 |", markdown)
        self.assertIn("### 非严格缩写定义候选", markdown)


if __name__ == "__main__":
    unittest.main()
