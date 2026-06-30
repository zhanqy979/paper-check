---
name: paper-check
description: Use when preparing a paper for submission and selecting a PC-prefixed pre-submission detail check.
---

# Paper Check

这是全局论文交稿前检查包的入口。包内实际检查 skill 统一采用 `pc-` 机器名前缀和 `PC-` 显示名前缀。

当前包含：

| Skill | 用途 |
|---|---|
| `pc-abbreviation-check` | 检查 LaTeX 摘要与其他正文中的缩写定义、使用次数、重复定义和全称大小写 |
| `pc-equation-punctuation-check` | 检查 LaTeX 展示公式前、公式内和公式后的标点、句式及推导链规范 |
| `pc-paper-review-grounded` | 基于论文原文、截图、表格或已有 review 草稿，生成、检查或改写客观、精简、可追溯的学术审稿意见 |

执行缩写检查时，必须加载并遵循 `pc-abbreviation-check`，不要在此入口中自行重写其统计规则。

执行公式检查时，必须加载并遵循 `pc-equation-punctuation-check`，不要脱离公式前后文本孤立判断标点。

执行学术审稿生成、检查或改写时，必须加载并遵循 `pc-paper-review-grounded`，不得凭空编造论文贡献、实验、数据、缺陷、引用或结论。
