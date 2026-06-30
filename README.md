# paper-check

`paper-check` is a Codex skills package for pre-submission paper checks and grounded academic review support.

## Included skills

- `paper-check`: entry skill for selecting PC paper-check workflows.
- `pc-abbreviation-check`: checks abbreviation definitions, usage counts, duplicate definitions, unused definitions, and full-name capitalization in LaTeX manuscripts.
- `pc-equation-punctuation-check`: checks displayed-equation punctuation and surrounding sentence flow in LaTeX manuscripts.
- `pc-paper-review-grounded`: generates, checks, or rewrites concise academic peer-review comments grounded in the manuscript or user-provided materials.

## Install

Copy the directories under `skills/` into your global Codex skills directory:

```powershell
Copy-Item -Path ".\skills\*" -Destination "$env:USERPROFILE\.codex\skills" -Recurse -Force
```

Or run:

```powershell
.\install.ps1
```

After installation, use `$paper-check` or call the specific `pc-*` skills directly.
