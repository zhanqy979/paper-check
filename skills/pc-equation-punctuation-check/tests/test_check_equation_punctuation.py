import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_equation_punctuation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_equation_punctuation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EquationPunctuationTests(unittest.TestCase):
    def analyze(self, text: str, style: str = "generic"):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(text, encoding="utf-8")
            return checker.analyze_project(main, style=style)

    def test_flags_punctuation_between_preposition_and_equation(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The estimate is obtained by:\n"
            "\\begin{equation}\n"
            "x = y.\n"
            "\\end{equation}\n"
            "\\end{document}\n"
        )
        issue_types = {item["issue_type"] for item in report["issues"]}
        self.assertIn("punctuation-before-equation", issue_types)

    def test_requires_comma_when_lowercase_where_continues_sentence(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The received signal is\n"
            "\\begin{equation}\n"
            "y = Hx + n\n"
            "\\end{equation}\n"
            "where $H$ is the channel matrix.\n"
            "\\end{document}\n"
        )
        issue = next(item for item in report["issues"] if item["issue_type"] == "equation-ending")
        self.assertEqual(issue["expected"], ",")
        self.assertEqual(issue["actual"], "none")

    def test_requires_period_before_new_paragraph_or_new_sentence(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The objective is\n"
            "\\begin{equation}\n"
            "f(x)=x^2,\n"
            "\\end{equation}\n"
            "\n"
            "The optimization is convex.\n"
            "\\end{document}\n"
        )
        issue = next(item for item in report["issues"] if item["issue_type"] == "equation-ending")
        self.assertEqual(issue["expected"], ".")
        self.assertEqual(issue["actual"], ",")

    def test_does_not_treat_proper_name_after_equation_as_certain_new_sentence(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The method follows\n"
            "\\begin{equation}\n"
            "z = g(x)\n"
            "\\end{equation}\n"
            "Gaussian noise is then added.\n"
            "\\end{document}\n"
        )
        ending = [item for item in report["issues"] if item["issue_type"] == "equation-ending"]
        self.assertTrue(ending)
        self.assertEqual(ending[0]["confidence"], "需人工确认")

    def test_ieee_profile_does_not_require_a_comma_before_where(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The model is\n"
            "\\begin{equation}\n"
            "y=x\n"
            "\\end{equation}\n"
            "where $x$ is the input.\n"
            "\\end{document}\n",
            style="ieee",
        )
        self.assertFalse(
            any(
                item["issue_type"] == "equation-ending" and item["expected"] == ","
                for item in report["issues"]
            )
        )

    def test_expands_input_and_reports_source_line(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "main.tex"
            section = root / "section.tex"
            main.write_text(
                "\\begin{document}\n\\input{section}\n\\end{document}\n",
                encoding="utf-8",
            )
            section.write_text(
                "The result is\n"
                "\\begin{equation}\n"
                "a=b\n"
                "\\end{equation}\n"
                "\n"
                "This starts a new paragraph.\n",
                encoding="utf-8",
            )
            report = checker.analyze_project(main)

        issue = next(item for item in report["issues"] if item["issue_type"] == "equation-ending")
        self.assertEqual(Path(issue["file"]).name, "section.tex")
        self.assertGreaterEqual(issue["line"], 2)

    def test_markdown_has_required_columns_and_summary(self):
        checker = load_checker()
        report = self.analyze(
            "\\begin{document}\n"
            "The value is\n"
            "\\[x=1\\]\n"
            "where $x$ is scalar.\n"
            "\\end{document}\n"
        )
        markdown = checker.render_markdown(report)
        self.assertIn(
            "| 序号 | 位置 | 公式环境 | 公式前文本 | 公式末尾标点 | 公式后文本 | 问题类型 | 修改建议 | 置信度 |",
            markdown,
        )
        self.assertIn("## 分类统计", markdown)

    def test_flags_period_on_intermediate_align_row(self):
        report = self.analyze(
            "\\begin{document}\n"
            "We obtain\n"
            "\\begin{align}\n"
            "a &= b. \\\\\n"
            "  &= c.\n"
            "\\end{align}\n"
            "\\end{document}\n"
        )
        self.assertTrue(
            any(item["issue_type"] == "derivation-chain-punctuation" for item in report["issues"])
        )

    def test_flags_punctuation_written_after_environment(self):
        report = self.analyze(
            "\\begin{document}\n"
            "The value is\n"
            "\\begin{equation}\n"
            "x=1\n"
            "\\end{equation}.\n"
            "\n"
            "This is a new paragraph.\n"
            "\\end{document}\n"
        )
        issue = next(
            item for item in report["issues"] if item["issue_type"] == "punctuation-placement"
        )
        self.assertEqual(issue["actual"], "outside equation")


if __name__ == "__main__":
    unittest.main()
