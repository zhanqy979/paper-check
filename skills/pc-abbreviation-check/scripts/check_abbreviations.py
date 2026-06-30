#!/usr/bin/env python3
"""Check abbreviation definitions and usage in a LaTeX paper."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


INCLUDE_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
ABSTRACT_RE = re.compile(
    r"\\begin\s*\{abstract\}(.*?)\\end\s*\{abstract\}",
    re.IGNORECASE | re.DOTALL,
)
ABBR_RE = re.compile(r"\((?P<abbr>[A-Za-z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)*)\)")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'’]*(?:-[A-Za-z][A-Za-z'’]*)*")
MASK_COMMAND_RE = re.compile(
    r"\\(?:cite\w*|ref|eqref|pageref|label|url|href|includegraphics)"
    r"(?:\s*\[[^\]]*\])?\s*\{[^{}]*\}(?:\s*\{[^{}]*\})?"
)
COMMAND_RE = re.compile(r"\\[A-Za-z@]+\*?(?:\s*\[[^\]]*\])?")
MATH_RE = re.compile(r"\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)", re.DOTALL)
WORD_BOUNDARY_TEMPLATE = r"(?<![A-Za-z0-9]){abbr}(?![A-Za-z0-9])"

PROPER_NAME_HINTS = {
    "academy",
    "association",
    "commission",
    "committee",
    "company",
    "conference",
    "corporation",
    "department",
    "institute",
    "laboratory",
    "ministry",
    "network",
    "organization",
    "society",
    "university",
}
LOWERCASE_CONNECTORS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "via",
    "with",
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
    if candidate.suffix.lower() != ".tex":
        candidate = candidate.with_suffix(".tex")
    return candidate


def expand_tex(path: Path, stack: tuple[Path, ...] = ()) -> tuple[str, list[tuple[str, int]]]:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(item) for item in (*stack, path))
        raise ValueError(f"Circular LaTeX include detected: {chain}")
    if not path.exists():
        raise FileNotFoundError(f"LaTeX file not found: {path}")

    output: list[str] = []
    locations: list[tuple[str, int]] = []
    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    for line_number, raw_line in enumerate(lines, 1):
        line = strip_comment(raw_line)
        cursor = 0
        for match in INCLUDE_RE.finditer(line):
            prefix = line[cursor : match.start()]
            output.append(prefix)
            locations.extend([(str(path), line_number)] * len(prefix))
            child = resolve_tex_path(path.parent, match.group(1))
            child_text, child_locations = expand_tex(child, (*stack, path))
            output.append(child_text)
            locations.extend(child_locations)
            cursor = match.end()
        suffix = line[cursor:]
        output.append(suffix)
        locations.extend([(str(path), line_number)] * len(suffix))
        if raw_line.endswith(("\n", "\r")) and not line.endswith(("\n", "\r")):
            output.append("\n")
            locations.append((str(path), line_number))
    return "".join(output), locations


def find_main_tex(target: Path) -> Path:
    target = target.resolve()
    if target.is_file():
        return target
    if not target.is_dir():
        raise FileNotFoundError(f"Path not found: {target}")
    candidates = sorted(target.glob("*.tex"))
    for candidate in candidates:
        if "\\documentclass" in candidate.read_text(encoding="utf-8-sig"):
            return candidate
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("Cannot determine the main TeX file; pass it explicitly.")


def mask_range(text: str, pattern: re.Pattern[str]) -> str:
    chars = list(text)
    for match in pattern.finditer(text):
        chars[match.start() : match.end()] = " " * (match.end() - match.start())
    return "".join(chars)


def sanitize_latex(text: str) -> str:
    clean = mask_range(text, MATH_RE)
    clean = mask_range(clean, MASK_COMMAND_RE)
    clean = COMMAND_RE.sub(lambda match: " " * (match.end() - match.start()), clean)
    clean = clean.translate(str.maketrans({"{": " ", "}": " ", "~": " "}))
    return clean


def document_slice(text: str) -> tuple[int, int]:
    begin = re.search(r"\\begin\s*\{document\}", text, re.IGNORECASE)
    end = re.search(r"\\end\s*\{document\}", text, re.IGNORECASE)
    return (begin.end() if begin else 0, end.start() if end else len(text))


def initial_letters(full_name: str) -> str:
    pieces: list[str] = []
    for token in TOKEN_RE.findall(full_name):
        for component in token.replace("’", "'").split("-"):
            if component.lower() not in LOWERCASE_CONNECTORS:
                pieces.append(component[0].upper())
    return "".join(pieces)


def normalized_abbreviation(abbreviation: str) -> str:
    value = abbreviation[:-1] if abbreviation.endswith("s") else abbreviation
    return "".join(char for char in value.upper() if char.isalnum())


def is_abbreviation_shape(abbreviation: str) -> bool:
    value = abbreviation[:-1] if abbreviation.endswith("s") else abbreviation
    letters = [char for char in value if char.isalpha()]
    return (
        2 <= len(value) <= 15
        and len(letters) >= 2
        and sum(char.isupper() for char in letters) >= 2
    )


def is_subsequence(shorter: str, longer: str) -> bool:
    iterator = iter(longer)
    return all(any(candidate == char for candidate in iterator) for char in shorter)


def abbreviation_match_kind(full_name: str, abbreviation: str) -> str | None:
    initials = initial_letters(full_name)
    target = normalized_abbreviation(abbreviation)
    if initials == target:
        return "strict"
    if (
        len(initials) >= 2
        and len(target) - len(initials) <= 2
        and is_subsequence(initials, target)
    ):
        return "candidate"
    return None


def candidate_full_name(
    text: str, open_paren: int, abbreviation: str
) -> tuple[str, int, str] | None:
    boundary = max(
        text.rfind(".", 0, open_paren),
        text.rfind("!", 0, open_paren),
        text.rfind("?", 0, open_paren),
        text.rfind(";", 0, open_paren),
        text.rfind(":", 0, open_paren),
        text.rfind("\n", 0, open_paren),
    )
    window_start = max(boundary + 1, open_paren - 240)
    window = text[window_start:open_paren]
    tokens = list(TOKEN_RE.finditer(window))
    target = normalized_abbreviation(abbreviation)
    candidates: list[tuple[int, int, str, int, str]] = []
    for count in range(1, min(len(tokens), 15) + 1):
        selected = tokens[-count:]
        start = window_start + selected[0].start()
        end = window_start + selected[-1].end()
        full_name = text[start:end].strip()
        kind = abbreviation_match_kind(full_name, abbreviation)
        if kind and len(selected) >= 2:
            missing = len(target) - len(initial_letters(full_name))
            priority = 0 if kind == "strict" else 1
            candidates.append((priority, missing, full_name, start, kind))
    if not candidates:
        return None
    _, _, full_name, start, kind = min(
        candidates, key=lambda item: (item[0], item[1], len(TOKEN_RE.findall(item[2])))
    )
    return full_name, start, kind


def section_for_offset(offset: int, abstract_spans: Iterable[tuple[int, int]]) -> str:
    return "abstract" if any(start <= offset < end for start, end in abstract_spans) else "other"


def locate(locations: list[tuple[str, int]], offset: int) -> dict[str, object]:
    if not locations:
        return {"file": "", "line": 0}
    file_name, line = locations[min(offset, len(locations) - 1)]
    return {"file": file_name, "line": line}


def capitalization_issue(full_name: str, abbreviation: str) -> str | None:
    words = TOKEN_RE.findall(full_name)
    if not words:
        return None
    lower_words = {part.lower() for word in words for part in word.split("-")}
    if lower_words & PROPER_NAME_HINTS:
        return None
    capitalized = [
        part
        for word in words
        for part in word.split("-")
        if part and part[0].isupper() and part.lower() not in LOWERCASE_CONNECTORS
    ]
    if len(capitalized) >= 2:
        return (
            "疑似使用了标题式大写；普通技术术语通常应使用小写。"
            "若该全称含人名、地名、机构名或标准专名，请人工确认。"
        )
    return None


def analyze_project(target: str | Path) -> dict[str, object]:
    main_file = find_main_tex(Path(target))
    raw_text, locations = expand_tex(main_file)
    body_start, body_end = document_slice(raw_text)
    raw_text = raw_text[body_start:body_end]
    locations = locations[body_start:body_end]
    clean_text = sanitize_latex(raw_text)
    abstract_spans = [(match.start(1), match.end(1)) for match in ABSTRACT_RE.finditer(raw_text)]

    definitions: list[dict[str, object]] = []
    definition_abbr_spans: list[tuple[int, int]] = []
    for match in ABBR_RE.finditer(clean_text):
        abbreviation = match.group("abbr")
        if not is_abbreviation_shape(abbreviation):
            continue
        candidate = candidate_full_name(clean_text, match.start(), abbreviation)
        if candidate is None:
            continue
        full_name, full_start, match_kind = candidate
        section = section_for_offset(match.start(), abstract_spans)
        item = {
            "full_name": re.sub(r"\s+", " ", full_name).strip(),
            "abbreviation": abbreviation,
            "section": section,
            "offset": match.start(),
            "full_start": full_start,
            "definition_span": (full_start, match.end()),
            "match_kind": match_kind,
            **locate(locations, full_start),
        }
        definitions.append(item)
        definition_abbr_spans.append((match.start("abbr"), match.end("abbr")))

    occurrences: dict[tuple[str, str], list[int]] = defaultdict(list)
    for abbreviation in {str(item["abbreviation"]) for item in definitions}:
        pattern = re.compile(WORD_BOUNDARY_TEMPLATE.format(abbr=re.escape(abbreviation)))
        for match in pattern.finditer(clean_text):
            if any(start <= match.start() < end for start, end in definition_abbr_spans):
                continue
            section = section_for_offset(match.start(), abstract_spans)
            occurrences[(section, abbreviation)].append(match.start())

    sections: dict[str, dict[str, object]] = {}
    for section_name in ("abstract", "other"):
        rows: list[dict[str, object]] = []
        unused: list[dict[str, object]] = []
        issues: list[dict[str, object]] = []
        section_definitions = [item for item in definitions if item["section"] == section_name]
        for index, item in enumerate(section_definitions, 1):
            abbreviation = str(item["abbreviation"])
            uses = occurrences[(section_name, abbreviation)]
            row = {
                "index": index,
                "full_name": item["full_name"],
                "abbreviation": abbreviation,
                "occurrences": len(uses),
                "file": item["file"],
                "line": item["line"],
            }
            rows.append(row)
            if not any(
                offset > int(item["offset"])
                for (key_section, key_abbreviation), offsets in occurrences.items()
                if key_abbreviation == abbreviation
                for offset in offsets
            ):
                unused.append(row.copy())
            issue = capitalization_issue(str(item["full_name"]), abbreviation)
            if issue:
                issues.append({**row, "reason": issue})
        sections[section_name] = {
            "definitions": rows,
            "unused": unused,
            "capitalization_issues": issues,
        }

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in definitions:
        grouped[str(item["abbreviation"])].append(item)
    duplicates = []
    for abbreviation, items in grouped.items():
        if len(items) > 1:
            duplicates.append(
                {
                    "abbreviation": abbreviation,
                    "definition_count": len(items),
                    "repeated_times": len(items) - 1,
                    "locations": [
                        {
                            "file": item["file"],
                            "line": item["line"],
                            "section": item["section"],
                            "full_name": item["full_name"],
                        }
                        for item in items
                    ],
                }
            )
    duplicates.sort(key=lambda item: int(grouped[str(item["abbreviation"])][0]["offset"]))

    return {
        "main_file": str(main_file),
        "sections": sections,
        "global": {
            "duplicate_definitions": duplicates,
            "candidate_definitions": [
                {
                    "full_name": item["full_name"],
                    "abbreviation": item["abbreviation"],
                    "section": item["section"],
                    "file": item["file"],
                    "line": item["line"],
                }
                for item in definitions
                if item["match_kind"] == "candidate"
            ],
        },
    }


def markdown_escape(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def render_table(rows: list[dict[str, object]]) -> list[str]:
    lines = ["| 序号 | 全称 | 缩写 | 出现次数 |", "|---:|---|---|---:|"]
    for row in rows:
        lines.append(
            f"| {row['index']} | {markdown_escape(row['full_name'])} | "
            f"{markdown_escape(row['abbreviation'])} | {row['occurrences']} |"
        )
    if not rows:
        lines.append("| — | 未发现缩写定义 | — | — |")
    return lines


def location_text(item: dict[str, object]) -> str:
    return f"`{item['file']}:{item['line']}`"


def render_markdown(report: dict[str, object]) -> str:
    sections = report["sections"]
    lines = [
        "# 论文缩写检查报告",
        "",
        f"主文件：`{report['main_file']}`",
        "",
        "> 说明：最终表中的严格匹配与候选扫描已合并；非严格候选另列供人工复核。",
        "",
    ]
    for key, title in (("abstract", "摘要"), ("other", "其他正文")):
        lines.extend([f"## {title}", "", *render_table(sections[key]["definitions"]), ""])

    lines.extend(["## 统计与规范检查", "", "### 重复定义的缩写", ""])
    duplicates = report["global"]["duplicate_definitions"]
    if duplicates:
        for item in duplicates:
            locations = "；".join(
                f"{location_text(location)}（{location['section']}，{location['full_name']}）"
                for location in item["locations"]
            )
            lines.append(
                f"- **{item['abbreviation']}**：共定义 {item['definition_count']} 次，"
                f"重复 {item['repeated_times']} 次。位置：{locations}"
            )
    else:
        lines.append("- 未发现重复定义。")

    lines.extend(["", "### 定义后未再出现的缩写", ""])
    unused_rows = [
        (title, row)
        for key, title in (("abstract", "摘要"), ("other", "其他正文"))
        for row in sections[key]["unused"]
    ]
    if unused_rows:
        for title, row in unused_rows:
            lines.append(
                f"- **{row['abbreviation']}**（{title}）：{row['full_name']}，定义于 {location_text(row)}。"
            )
    else:
        lines.append("- 未发现定义后不再使用的缩写。")

    lines.extend(["", "### 全称大小写规范检查", ""])
    issues = [
        (title, row)
        for key, title in (("abstract", "摘要"), ("other", "其他正文"))
        for row in sections[key]["capitalization_issues"]
    ]
    if issues:
        for title, row in issues:
            lines.append(
                f"- **{row['abbreviation']}**（{title}）：{row['full_name']}，"
                f"{location_text(row)}。{row['reason']}"
            )
    else:
        lines.append("- 未发现明显的全称大小写问题。")

    lines.extend(["", "### 非严格缩写定义候选", ""])
    candidates = report["global"]["candidate_definitions"]
    if candidates:
        for item in candidates:
            lines.append(
                f"- **{item['abbreviation']}**：{item['full_name']}，"
                f"{item['section']}，{location_text(item)}。"
            )
    else:
        lines.append("- 未发现需要人工确认的非严格缩写定义。")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Main .tex file or a directory containing the paper")
    parser.add_argument("-o", "--output", help="Write the report to this file")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    report = analyze_project(args.target)
    content = json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_markdown(report)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
