# paper-check

`paper-check` is a reusable Agent Skills package for academic paper polishing, pre-submission checks, and grounded peer-review assistance.

It is designed for researchers who repeatedly need to check LaTeX manuscripts before submission or write reviewer-style feedback from a manuscript without inventing unsupported claims.

## What this skills package does

This package contains one entry skill and three paper-checking skills:

| Skill | Purpose |
|---|---|
| `paper-check` | Entry skill for selecting the paper-check workflows. |
| `pc-abbreviation-check` | Checks abbreviation definitions in LaTeX manuscripts, including abstract/body separation, definition tables, usage counts, duplicate definitions, unused abbreviations, and full-name capitalization. |
| `pc-equation-punctuation-check` | Checks displayed-equation punctuation and surrounding sentence flow in LaTeX manuscripts, especially whether equations are punctuated as part of the sentence. |
| `pc-paper-review-grounded` | Generates, checks, or rewrites concise academic peer-review comments grounded only in the manuscript, screenshots, tables, forms, or review drafts provided by the user. |

Typical use cases:

- Before submission, check whether abbreviations such as `orthogonal frequency-division multiplexing (OFDM)` are defined and reused correctly.
- Check whether displayed equations use appropriate commas, periods, and surrounding sentence structure.
- Convert manuscript evidence into concise reviewer comments.
- Check an existing review draft for unsupported claims, wrong table numbers, exaggerated criticism, or recommendation mismatch.

The review skill is intentionally conservative: it requires factual grounding and tells the agent to use phrases such as `not reported`, `unclear`, or `cannot be verified from the manuscript` when evidence is missing.

## Repository layout

```text
paper-check/
├── README.md
├── install.ps1
└── skills/
    ├── paper-check/
    ├── pc-abbreviation-check/
    ├── pc-equation-punctuation-check/
    └── pc-paper-review-grounded/
```

Each skill directory contains a `SKILL.md` file. Some skills also include scripts, tests, references, and UI metadata.

## Installation

First clone the repository:

```bash
git clone https://github.com/zhanqy979/paper-check.git
cd paper-check
```

Then copy the folders inside `skills/` into the skills directory used by your agent.

### Codex on Windows

Recommended user-level Codex skills location:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Path ".\skills\*" -Destination "$env:USERPROFILE\.agents\skills" -Recurse -Force
```

If your Codex setup uses the older/global Codex path, install there instead:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Path ".\skills\*" -Destination "$env:USERPROFILE\.codex\skills" -Recurse -Force
```

This repository also includes a convenience script for the `.codex\skills` layout:

```powershell
.\install.ps1
```

Restart Codex if the new skills do not appear immediately.

### Codex on macOS

Recommended user-level Codex skills location:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skills/* "$HOME/.agents/skills/"
```

If your Codex setup uses the older/global Codex path, install there instead:

```bash
mkdir -p "$HOME/.codex/skills"
cp -R skills/* "$HOME/.codex/skills/"
```

Restart Codex if the new skills do not appear immediately.

### Claude Code on Windows

Install as personal Claude Code skills:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Path ".\skills\*" -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
```

For a project-local installation, copy the skills into the target repository:

```powershell
New-Item -ItemType Directory -Force -Path ".\.claude\skills" | Out-Null
Copy-Item -Path ".\skills\*" -Destination ".\.claude\skills" -Recurse -Force
```

Start or restart Claude Code in the project. You can invoke skills directly with slash commands such as:

```text
/paper-check
/pc-abbreviation-check
/pc-equation-punctuation-check
/pc-paper-review-grounded
```

### Claude Code on macOS

Install as personal Claude Code skills:

```bash
mkdir -p "$HOME/.claude/skills"
cp -R skills/* "$HOME/.claude/skills/"
```

For a project-local installation, copy the skills into the target repository:

```bash
mkdir -p ".claude/skills"
cp -R skills/* ".claude/skills/"
```

Start or restart Claude Code in the project. You can invoke skills directly with slash commands such as:

```text
/paper-check
/pc-abbreviation-check
/pc-equation-punctuation-check
/pc-paper-review-grounded
```

## How to use

In Codex, mention the entry skill or a specific skill:

```text
$paper-check Check this LaTeX manuscript before submission.
$pc-abbreviation-check Check abbreviation definitions in v5.tex.
$pc-equation-punctuation-check Check equation punctuation in v5.tex.
$pc-paper-review-grounded Rewrite this review so it is concise and fully grounded in the manuscript.
```

In Claude Code, invoke the corresponding slash command:

```text
/paper-check
/pc-abbreviation-check
/pc-equation-punctuation-check
/pc-paper-review-grounded
```

You can also ask naturally; the agent may load the relevant skill automatically when the task matches the skill description.

## Notes

- The abbreviation and equation skills are optimized for LaTeX manuscripts.
- The review skill works with manuscripts, screenshots, tables, review forms, or existing review drafts.
- The package does not replace human technical judgment. It is a structured assistant for catching consistency, wording, and evidence-grounding issues.
- Skills copied into personal directories are available globally. Skills copied into project directories apply only to that project.

## References

- Codex Agent Skills documentation: https://developers.openai.com/codex/skills
- Claude Code Skills documentation: https://code.claude.com/docs/en/skills
