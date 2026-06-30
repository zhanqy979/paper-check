# 科研论文公式标点与句式规则

## 核心原则

展示公式在排版上独占一行，但在语法上仍属于所在句子。判断标点时，将“公式前文本 + 公式 + 公式后文本”还原为一个连续句子。

## 公式前

### 直接支配公式的词

介词或连接结构直接引出公式时，通常不要在该词后添加标点：

- `obtained by` + 公式
- `defined as` + 公式
- `computed from` + 公式
- `using` + 公式
- `with` + 公式

错误倾向：

```latex
The estimate is obtained by:
\begin{equation}
...
\end{equation}
```

若前文是完整独立分句并明确引出后续内容，冒号可能成立；不得仅按最后一个单词机械删除。

### 常见引导结构

- `is given by`、`is defined as`、`can be written as`：通常不加冒号。
- `as follows`：是否加冒号取决于目标期刊风格和句法；标记人工复核。
- `where` 位于公式前时，确认它确实引出条件或符号定义，避免残句。

## 公式末尾

### 通用科研写作风格

- 公式结束整个句子：使用句号。
- 公式后继续同一句，尤其后接 `where`、`which`、`with`、`and` 等小写词：通常使用逗号。
- 公式后另起一段：前一公式必须以句号结束。
- 公式后明显以新句开始：使用句号。
- 分号和冒号仅在整体句法确实需要时使用。

### IEEE 风格差异

IEEE Editorial Style Manual 要求公式结束句子时使用句号；公式末尾逗号通常删除，除非删除会影响句法或理解。因此：

- `generic` 模式可建议小写续句前使用逗号；
- `ieee` 模式不自动要求该逗号，而是对已有逗号进行人工复核；
- 用户提供目标期刊规则时，以目标期刊为准。

## 公式后

- 小写词通常表示原句继续，不能在公式中先用句号截断。
- 另起一段必然表示前句已结束。
- `The`、`This`、`We`、`However`、`Therefore` 等常见句首词通常表示新句。
- `Gaussian`、`Fourier`、`Bayesian`、人名、地名、机构名和全大写缩写可能只是专名，不足以单独证明新句开始。
- 公式后仅有符号解释但缺少主语或谓语时，检查是否形成残句。

## 连续推导与多行公式

- 将整个 `align`、`gather` 或 `multline` 视为一个句法单元。
- 中间推导行通常不应使用句号。
- 若各行是并列数学陈述，可按句法使用逗号或分号。
- 最后一行根据整个句子是否结束决定标点。
- `cases`、`split`、`aligned` 内部标点不能代替外层公式的句末标点。

## 标点位置

- 标点是句法的一部分，应置于数学内容末尾、展示公式环境结束之前。
- 公式编号、`\label{...}`、`\tag{...}`、`\nonumber` 都不是标点。
- 不要同时在公式内容末尾和环境结束后重复添加标点。

## 其他检查

- 避免无必要地以裸公式开始句子；优先用文字建立语法主干。
- `respectively` 必须清楚对应前述项目顺序。
- `such that` 应连接完整的约束结构。
- 符号定义应具有明确谓语，如 `denotes`、`represents`、`is`。
- 公式引用通常写作 `Eq. (1)` 或目标期刊指定形式，不要自行混用大小写和缩写。

## 置信度

- **高**：另起一段、明确小写续句、介词后明显误加标点、标点位于环境外。
- **中**：连续推导中间行句号、可由上下文判断但仍可能有特殊修辞。
- **需人工确认**：大写词可能是专名；`as follows` 等风格差异；IEEE 逗号例外；复杂宏或特殊数学语义。

## 依据

- IEEE Author Center, *IEEE Editorial Style Manual for Authors*:  
  https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf
- American Mathematical Society, Ellen Swanson, *Mathematics into Type*:  
  https://www.ams.org/publications/authors/mit-2.pdf

这些规范共同支持“公式是句子的一部分”；具体逗号策略应服从目标出版物的风格指南。
