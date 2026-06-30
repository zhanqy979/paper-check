---
name: pc-equation-punctuation-check
description: Use when checking punctuation, capitalization, sentence continuity, or prose structure around displayed equations in LaTeX research papers before submission.
---

# PC-Equation Punctuation Check

把展示公式视为句子的语法成分，联合检查公式前文本、公式末尾标点和公式后文本。不要因为公式独占一行就默认它结束句子。

## 工作流

1. 确定论文主 `.tex` 文件。
2. 选择风格：

   - `generic`：默认；按句法连续性要求逗号或句号。
   - `ieee`：遵循 IEEE 对公式末尾逗号更严格的限制。

3. 运行：

   ```powershell
   python scripts/check_equation_punctuation.py <main.tex> --style generic -o equation-punctuation-report.md
   ```

4. 读取 [references/equation-writing-rules.md](references/equation-writing-rules.md)，逐项复核报告。
5. 返回报告路径，并汇总公式前标点、公式末尾标点、公式后句式、推导链和需人工确认项目。

## 强制判断原则

- 若 `as`、`by`、`from`、`using`、`with`、`via` 等词直接支配公式，不要在该词和公式之间插入逗号、冒号或分号。
- 若公式后以普通小写词继续同一句，`generic` 风格通常要求公式以逗号结束。
- 若公式后另起一段，或明显开始一个新句，公式应以句号结束。
- 若后文以大写词开始，先排除人名、地名、机构名、缩写和技术专名；无法确定时标记“需人工确认”。
- 公式编号不能代替句法标点。
- 标点应放在公式内容末尾、公式环境结束命令之前；不得仅写在 `\end{equation}` 后面。
- 连续推导的中间行不得无理由用句号提前结束整句。

## 输出

使用固定表头：

| 序号 | 位置 | 公式环境 | 公式前文本 | 公式末尾标点 | 公式后文本 | 问题类型 | 修改建议 | 置信度 |
|---:|---|---|---|---|---|---|---|---|

每项必须包含 `文件:行号`。报告只提出建议，不自动编辑论文。

## 支持范围

- 支持 `equation`、`align`、`alignat`、`gather`、`multline`、`flalign`、`displaymath`、`\[...\]` 和 `$$...$$`。
- 递归展开 `\input` 与 `\include`，忽略 `%` 注释。
- `split`、`aligned`、`cases` 作为外层展示公式的一部分检查。
- 复杂宏、条件编译、自定义环境和依赖深层语义的句法必须人工补查。

## 常见错误

- 只看公式末尾，不看前后句子的语法关系。
- 把所有小写后文机械判为逗号，而不考虑投稿风格。
- 把所有大写后文机械判为新句。
- 把公式编号当作句号。
- 在 `\end{equation}` 后补标点，却让公式本身仍无标点。
- 直接依据低置信度提示修改专名或数学表达。
