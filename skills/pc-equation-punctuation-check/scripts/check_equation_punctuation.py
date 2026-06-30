#!/usr/bin/env python3
"""Check punctuation and sentence structure around displayed LaTeX equations."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


INCLUDE_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
DISPLAY_ENVIRONMENTS = (
    "equation",
    "align",
    "alignat",
    "gather",
    "multline",
    "flalign",
    "displaymath",
)
ENV_RE = re.compile(
    r"\\begin\s*\{(?P<env>(?:"
    + "|".join(DISPLAY_ENVIRONMENTS)
    + r")\*?)\}(?P<body>.*?)\\end\s*\{(?P=env)\}",
    re.IGNORECASE | re.DOTALL,
)
BRACKET_RE = re.compile(r"\\\[(?P<body>.*?)\\\]", re.DOTALL)
DOLLAR_RE = re.compile(r"\$\$(?P<body>.*?)\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"\$.*?\$|\\\(.*?\\\)", re.DOTALL)
COMMAND_RE = re.compile(
    r"\\(?:label|tag|notag|nonumber|qquad|quad|;|,|!|enspace|hspace)"
    r"(?:\s*\{[^{}]*\})?"
)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")

DIRECT_GOVERNORS = {
    "as",
    "by",
    "from",
    "through",
    "using",
    "via",
    "with",
}
LOWERCASE_CONTINUATIONS = {
    "and",
    "as",
    "because",
    "but",
    "for",
    "if",
    "or",
    "such",
    "then",
    "where",
    "whereas",
    "which",
    "while",
    "with",
}
CERTAIN_SENTENCE_STARTERS = {
    "Additionally",
    "Consequently",
    "Conversely",
    "Finally",
    "Furthermore",
    "Hence",
    "However",
    "It",
    "Moreover",
    "Next",
    "Nevertheless",
    "Otherwise",
    "Therefore",
    "These",
    "This",
    "Thus",
    "We",
}
PROPER_OR_TECHNICAL_HINTS = {
    "Bayesian",
    "Bernoulli",
    "Euclidean",
    "Fourier",
    "Gaussian",
    "Hermitian",
    "Jacobian",
    "Laplacian",
    "Markov",
    "Newton",
    "Poisson",
    "Riemannian",
    "Shannon",
}


def strip_comment(line: str) -> str:
    escaped = False
    for index, char in enumerate(line):
        if char == "%" and not escaped:
            return line[:index]
        if char == "\\":
            escaped = not escaped
        else:
            escaped = False
    return line


def resolve_tex_path(base: Path, value: str) -> Path:
    candidate = (base / value.strip()).resolve()
    return candidate if candidate.suffix.lower() == ".tex" else candidate.with_suffix(".tex")


def expand_tex(path: Path, stack: tuple[Path, ...] = ()) -> tuple[str, list[tuple[str, int]]]:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(item) for item in (*stack, path))
        raise ValueError(f"Circular LaTeX include detected: {chain}")
    if not path.exists():
        raise FileNotFoundError(f"LaTeX file not found: {path}")

    output: list[str] = []
    locations: list[tuple[str, int]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(keepends=True), 1
    ):
        line = strip_comment(raw_line)
        cursor = 0
        for match in INCLUDE_RE.finditer(line):
            prefix = line[cursor : match.start()]
            output.append(prefix)
            locations.extend([(str(path), line_number)] * len(prefix))
            child_text, child_locations = expand_tex(
                resolve_tex_path(path.parent, match.group(1)), (*stack, path)
            )
            output.append(child_text)
            locations.extend(child_locations)
            cursor = match.end()
        suffix = line[cursor:]
        output.append(suffix)
        locations.extend([(str(path), line_number)] * len(suffix))
        if raw_line.endswith(("\n", "\r")) and not suffix.endswith(("\n", "\r")):
            output.append("\n")
            locations.append((str(path), line_number))
    return "".join(output), locations


def find_main_tex(target: Path) -> Path:
    target = target.resolve()
    if target.is_file():
        return target
    candidates = sorted(target.glob("*.tex")) if target.is_dir() else []
    for candidate in candidates:
        if "\\documentclass" in candidate.read_text(encoding="utf-8-sig"):
            return candidate
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("Cannot determine the main TeX file; pass it explicitly.")


def document_slice(text: str) -> tuple[int, int]:
    begin = re.search(r"\\begin\s*\{document\}", text, re.IGNORECASE)
    end = re.search(r"\\end\s*\{document\}", text, re.IGNORECASE)
    return begin.end() if begin else 0, end.start() if end else len(text)


def visible_text(text: str) -> str:
    text = INLINE_MATH_RE.sub(" [math] ", text)
    text = re.sub(r"\\(?:cite\w*|ref|eqref|label|url|href)\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\s*\[[^\]]*\])?", " ", text)
    text = text.translate(str.maketrans({"{": " ", "}": " ", "~": " "}))
    return re.sub(r"\s+", " ", text).strip()


def equation_body_text(body: str) -> str:
    body = re.sub(r"%[^\n]*", "", body)
    body = COMMAND_RE.sub(" ", body)
    body = re.sub(r"\\(?:label|tag)\s*\{[^{}]*\}", " ", body)
    return body.strip()


def ending_punctuation(body: str) -> str:
    clean = equation_body_text(body)
    match = re.search(r"([.,;:])\s*$", clean)
    return match.group(1) if match else "none"


def extract_equations(text: str) -> list[dict[str, object]]:
    equations: list[dict[str, object]] = []
    for pattern, fallback_env in (
        (ENV_RE, None),
        (BRACKET_RE, r"\[...\]"),
        (DOLLAR_RE, "$$...$$"),
    ):
        for match in pattern.finditer(text):
            env = (
                match.group("env")
                if fallback_env is None
                else fallback_env
            )
            equations.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "body": match.group("body"),
                    "environment": env,
                }
            )
    equations.sort(key=lambda item: int(item["start"]))
    return equations


def context_before(text: str, start: int, limit: int = 180) -> str:
    return visible_text(text[max(0, start - limit) : start])


def context_after(text: str, end: int, limit: int = 180) -> tuple[str, bool]:
    raw = text[end : end + limit]
    paragraph_break = bool(re.match(r"[ \t]*\r?\n[ \t]*\r?\n", raw))
    return visible_text(raw), paragraph_break


def first_word(text: str) -> str:
    match = WORD_RE.search(text)
    return match.group(0) if match else ""


def location_at(locations: list[tuple[str, int]], offset: int) -> tuple[str, int]:
    if not locations:
        return "", 0
    return locations[min(offset, len(locations) - 1)]


def make_issue(
    equation: dict[str, object],
    locations: list[tuple[str, int]],
    pre: str,
    post: str,
    issue_type: str,
    actual: str,
    expected: str,
    suggestion: str,
    confidence: str,
) -> dict[str, object]:
    file_name, line = location_at(locations, int(equation["start"]))
    return {
        "file": file_name,
        "line": line,
        "environment": equation["environment"],
        "pre_text": pre[-100:],
        "ending": ending_punctuation(str(equation["body"])),
        "post_text": post[:100],
        "issue_type": issue_type,
        "actual": actual,
        "expected": expected,
        "suggestion": suggestion,
        "confidence": confidence,
    }


def expected_ending(
    post: str, paragraph_break: bool, style: str
) -> tuple[str | None, str, str]:
    word = first_word(post)
    if not word:
        return ".", "公式结束正文或文件，应以句号结束。", "高"
    if paragraph_break:
        return ".", "公式后另起一段，公式应结束前一句。", "高"
    if word[0].islower():
        if style == "ieee":
            return None, "IEEE 通常删除公式末尾逗号，除非逗号对句法至关重要。", "需人工确认"
        return ",", "后文以小写词续接同一句，公式通常应以逗号连接。", "高"
    if word in CERTAIN_SENTENCE_STARTERS:
        return ".", "后文明显开始新句，公式应以句号结束。", "高"
    if word in PROPER_OR_TECHNICAL_HINTS or word.isupper():
        return ".", "后文大写可能是专名、缩写或新句，需结合语义确认。", "需人工确认"
    return ".", "后文以大写词开始，疑似新句；需排除人名、地名和专名。", "需人工确认"


def analyze_project(target: str | Path, style: str = "generic") -> dict[str, object]:
    if style not in {"generic", "ieee"}:
        raise ValueError("style must be 'generic' or 'ieee'")
    main_file = find_main_tex(Path(target))
    raw_text, locations = expand_tex(main_file)
    body_start, body_end = document_slice(raw_text)
    text = raw_text[body_start:body_end]
    locations = locations[body_start:body_end]
    equations = extract_equations(text)
    issues: list[dict[str, object]] = []

    for equation in equations:
        start, end = int(equation["start"]), int(equation["end"])
        pre = context_before(text, start)
        post, paragraph_break = context_after(text, end)
        actual = ending_punctuation(str(equation["body"]))
        outside_match = re.match(r"[ \t]*([.,;:])", text[end:])
        outside_punctuation = outside_match.group(1) if outside_match else None
        effective_actual = outside_punctuation or actual

        if outside_punctuation:
            issues.append(
                make_issue(
                    equation,
                    locations,
                    pre,
                    post,
                    "punctuation-placement",
                    "outside equation",
                    "inside equation",
                    f"将 `{outside_punctuation}` 移到公式内容末尾、公式环境结束命令之前。",
                    "高",
                )
            )

        if str(equation["environment"]).lower().startswith(
            ("align", "alignat", "flalign")
        ):
            rows = re.split(r"\\\\(?:\s*\[[^\]]*\])?", str(equation["body"]))
            for row_number, row in enumerate(rows[:-1], 1):
                if ending_punctuation(row) == ".":
                    issue = make_issue(
                        equation,
                        locations,
                        pre,
                        post,
                        "derivation-chain-punctuation",
                        f"period on row {row_number}",
                        "continuing punctuation",
                        "中间推导行不应提前结束整句；结合推导关系改为逗号或删除句号。",
                        "中",
                    )
                    issues.append(issue)

        pre_match = re.search(
            r"\b(" + "|".join(sorted(DIRECT_GOVERNORS)) + r")\s*([,:;])\s*$",
            pre,
            re.IGNORECASE,
        )
        if pre_match:
            issues.append(
                make_issue(
                    equation,
                    locations,
                    pre,
                    post,
                    "punctuation-before-equation",
                    pre_match.group(2),
                    "none",
                    f"`{pre_match.group(1)}` 直接支配公式时，删除其后的标点。",
                    "高",
                )
            )

        expected, rationale, confidence = expected_ending(post, paragraph_break, style)
        if expected is not None and effective_actual != expected:
            issues.append(
                make_issue(
                    equation,
                    locations,
                    pre,
                    post,
                    "equation-ending",
                    effective_actual,
                    expected,
                    rationale,
                    confidence,
                )
            )
        elif style == "ieee" and effective_actual == ",":
            issues.append(
                make_issue(
                    equation,
                    locations,
                    pre,
                    post,
                    "ieee-comma-review",
                    ",",
                    "none or essential comma",
                    "IEEE 风格通常删除公式末尾逗号；仅在删除后句法含混时保留。",
                    "需人工确认",
                )
            )

        if actual == "." and first_word(post) and first_word(post)[0].islower():
            issues.append(
                make_issue(
                    equation,
                    locations,
                    pre,
                    post,
                    "sentence-after-equation",
                    "period + lowercase continuation",
                    "continuous sentence",
                    "公式后的文字仍在续接同一句；不要先用句号截断。",
                    "高",
                )
            )

    return {
        "main_file": str(main_file),
        "style": style,
        "equation_count": len(equations),
        "issues": issues,
        "summary": dict(Counter(str(item["issue_type"]) for item in issues)),
    }


def escape_markdown(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def issue_label(issue_type: str) -> str:
    return {
        "punctuation-before-equation": "公式前标点",
        "equation-ending": "公式末尾标点",
        "sentence-after-equation": "公式后句式",
        "ieee-comma-review": "IEEE 逗号复核",
        "derivation-chain-punctuation": "推导链标点",
        "punctuation-placement": "标点位置",
    }.get(issue_type, issue_type)


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# 公式标点与句式检查报告",
        "",
        f"主文件：`{report['main_file']}`",
        f"风格：`{report['style']}`",
        f"展示公式数：{report['equation_count']}",
        "",
        "| 序号 | 位置 | 公式环境 | 公式前文本 | 公式末尾标点 | 公式后文本 | 问题类型 | 修改建议 | 置信度 |",
        "|---:|---|---|---|---|---|---|---|---|",
    ]
    issues = report["issues"]
    if issues:
        for index, item in enumerate(issues, 1):
            location = f"`{item['file']}:{item['line']}`"
            lines.append(
                f"| {index} | {location} | {escape_markdown(item['environment'])} | "
                f"{escape_markdown(item['pre_text'])} | {escape_markdown(item['ending'])} | "
                f"{escape_markdown(item['post_text'])} | {issue_label(str(item['issue_type']))} | "
                f"{escape_markdown(item['suggestion'])} | {item['confidence']} |"
            )
    else:
        lines.append("| — | — | — | — | — | — | 未发现明显问题 | — | — |")

    lines.extend(["", "## 分类统计", ""])
    if report["summary"]:
        for key, count in sorted(report["summary"].items()):
            lines.append(f"- {issue_label(str(key))}：{count}")
    else:
        lines.append("- 未发现明显问题。")
    lines.extend(
        [
            "",
            "> 说明：公式必须作为句子的语法成分复核；“需人工确认”项目不得自动改稿。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Main .tex file or paper directory")
    parser.add_argument("--style", choices=("generic", "ieee"), default="generic")
    parser.add_argument("-o", "--output", help="Write report to this path")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    report = analyze_project(args.target, style=args.style)
    content = json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_markdown(report)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
