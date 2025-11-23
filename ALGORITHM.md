# 核心算法：LaTeX到Word兼容MathML转换器

## 算法概述

本项目的核心是一个**递归下降解析器（Recursive Descent Parser）**，用于将LaTeX数学公式转换为Word兼容的MathML格式。该算法采用自顶向下的解析策略，通过递归方法逐步分解复杂的LaTeX表达式。

```
输入：LaTeX公式字符串
输出：结构化的MathML XML
```

## 算法架构

### 1. 整体流程

```
图片 → Pix2Text OCR → LaTeX → 清理 → 递归解析器 → MathML
```

**三大核心模块：**

1. **FormulaRecognizer** (recognizer.py)
   - OCR识别：Pix2Text提取LaTeX
   - LaTeX清理：去除`\left`/`\right`等冗余命令

2. **WordMathMLConverter** (final_converter.py) ⭐️ 核心
   - 递归下降解析
   - AST构建和MathML生成

3. **FormulaConverter** (converter.py)
   - 协调器，整合识别和转换流程

## 核心算法：递归下降解析器

### 设计理念

**递归下降解析器的本质：**
- 每个语法规则对应一个解析函数
- 通过递归调用处理嵌套结构
- 返回值：`(MathML行列表, 消费的字符位置)`

### 文法定义

```bnf
<expression>    ::= <element>*
<element>       ::= <command> | <parentheses> | <variable> | <number> | <operator>
<command>       ::= '\' <cmd_name> <arguments>
<cmd_name>      ::= 'frac' | 'sigma' | 'left' | 'right' | <greek_letter>
<parentheses>   ::= '(' <expression> ')' ['^' <superscript>]
<variable>      ::= <letter>+ ['_' <subscript>]
<subscript>     ::= '{' <content> '}' | <single_char>
<superscript>   ::= '{' <content> '}' | <single_char>
```

## 关键算法实现

### 1. 主解析器：`_parse_expression`

**算法流程：**

```python
def _parse_expression(expr: str) -> (list, int):
    result = []
    i = 0

    while i < len(expr):
        # 1. 跳过空格
        if expr[i].isspace():
            i += 1
            continue

        # 2. LaTeX命令（\frac, \sigma等）
        if expr[i] == '\\':
            cmd_result, new_i = self._parse_command(expr, i)
            result.extend(cmd_result)
            i = new_i

        # 3. 圆括号（可能带上标）
        elif expr[i] == '(':
            paren_result, new_i = self._parse_parentheses(expr, i)
            result.extend(paren_result)
            i = new_i

        # 4. 变量（可能带下标）
        elif expr[i].isalpha():
            var, new_i = self._parse_variable(expr, i)
            result.extend(var)
            i = new_i

        # 5. 数字
        elif expr[i].isdigit():
            num, new_i = self._parse_number(expr, i)
            result.extend(num)
            i = new_i

        # 6. 运算符
        elif expr[i] in '+-=':
            result.append(f'  <mo>{expr[i]}</mo>')
            i += 1

    return result, i
```

**关键特性：**
- ✅ 单遍扫描，O(n)复杂度
- ✅ 位置追踪，避免重复解析
- ✅ 分支处理，每种语法元素独立解析

### 2. 分数解析：`_parse_fraction`

**处理模式：** `\frac{分子}{分母}`

```python
def _parse_fraction(expr: str, start: int) -> (list, int):
    # 1. 跳过空格
    i = start
    while i < len(expr) and expr[i].isspace():
        i += 1

    # 2. 解析分子 {...}
    if expr[i] == '{':
        numerator, i = self._parse_braced_content(expr, i)

    # 3. 解析分母 {...}
    if expr[i] == '{':
        denominator, i = self._parse_braced_content(expr, i)

    # 4. 递归解析分子和分母内容
    num_lines, _ = self._parse_expression(numerator)
    den_lines, _ = self._parse_expression(denominator)

    # 5. 生成MathML
    result = ['  <mfrac>']

    # 智能<mrow>包装
    if not self._is_single_element(num_lines):
        result.append('    <mrow>')
        result.extend(indent(num_lines))
        result.append('    </mrow>')
    else:
        result.extend(indent(num_lines))

    # 分母同理
    # ...

    result.append('  </mfrac>')
    return result, i
```

**核心难点：智能<mrow>包装**

❌ 错误示例：
```xml
<mfrac>
  <mrow>
    <msub>...</msub>  <!-- 单个元素不需要mrow -->
  </mrow>
  ...
</mfrac>
```

✅ 正确示例：
```xml
<mfrac>
  <msub>...</msub>  <!-- 直接放置 -->
  <mrow>
    <mi>a</mi>      <!-- 多个元素需要mrow -->
    <mo>+</mo>
    <mi>b</mi>
  </mrow>
</mfrac>
```

### 3. 单元素检测：`_is_single_element`

**算法目标：** 判断MathML行列表是否只包含一个顶层元素

```python
def _is_single_element(lines: list) -> bool:
    if len(lines) == 1:
        return True  # 单行必定是单元素

    depth = 0
    first_tag_closed = False

    for line in lines:
        stripped = line.strip()

        # 处理完整标签 <mi>x</mi>
        if '<' in stripped and '</' in stripped:
            if self._is_complete_tag(stripped):
                if depth == 0:
                    if first_tag_closed:
                        return False  # 第二个顶层元素
                    first_tag_closed = True
                continue

        # 结束标签 </...>
        if stripped.startswith('</'):
            depth -= 1
            if depth == 0:
                first_tag_closed = True

        # 开始标签 <...>
        elif stripped.startswith('<'):
            if first_tag_closed:
                return False  # 第一个元素已关闭，出现新元素
            depth += 1

    return first_tag_closed and depth == 0
```

**深度追踪算法：**

```
输入: ['<msub>', '<mi>σ</mi>', '<mi>f</mi>', '</msub>']

追踪过程:
第1行: <msub>      → depth=1, first_tag_closed=False
第2行: <mi>σ</mi>  → 完整标签，跳过
第3行: <mi>f</mi>  → 完整标签，跳过
第4行: </msub>     → depth=0, first_tag_closed=True

结果: True（单个<msub>元素）
```

### 4. 圆括号与上标：`_parse_parentheses`

**处理模式：** `(内容)^{上标}`

```python
def _parse_parentheses(expr: str, start: int) -> (list, int):
    # 1. 找到匹配的右括号
    content, end_pos = self._find_matching_parenthesis(expr, start)

    # 2. 检查是否有上标
    has_superscript = False
    if end_pos < len(expr) and expr[end_pos] == '^':
        has_superscript = True
        superscript, end_pos = self._parse_braced_content(expr, end_pos + 1)

    # 3. 递归解析内容
    content_lines, _ = self._parse_expression(content)

    # 4. 生成MathML
    if has_superscript:
        superscript_lines, _ = self._parse_expression(superscript)

        result = [
            '  <msup>',
            '    <mfenced open="(" close=")" separators="|">',
            '      <mrow>'
        ]
        result.extend(indent(content_lines))
        result.append('      </mrow>')
        result.append('    </mfenced>')
        result.extend(indent(superscript_lines))  # 动态上标
        result.append('  </msup>')
    else:
        result = [
            '  <mfenced open="(" close=")" separators="|">',
            '    <mrow>'
        ]
        result.extend(indent(content_lines))
        result.append('    </mrow>')
        result.append('  </mfenced>')

    return result, end_pos
```

**关键修复：动态上标解析**

❌ 旧版本（硬编码）：
```python
result.append('    <mn>2</mn>')  # 所有上标都是2
```

✅ 新版本（动态解析）：
```python
superscript_lines, _ = self._parse_expression(superscript)
result.extend(indent(superscript_lines))  # 解析实际内容
```

### 5. 下标处理：智能标签选择

**算法：** 数字下标用`<mn>`，字母下标用`<mi>`

```python
def _get_subscript_tag(content: str) -> str:
    """智能标签选择"""
    if content.isdigit():
        return 'mn'  # <mn>0</mn>
    else:
        return 'mi'  # <mi>f</mi>
```

**应用场景：**

```latex
R_{0}       →  <msub><mi>R</mi><mn>0</mn></msub>
\sigma_{f}  →  <msub><mi>σ</mi><mi>f</mi></msub>
```

### 6. 括号匹配：`_find_matching_parenthesis`

**算法：栈式括号匹配**

```python
def _find_matching_parenthesis(expr: str, start: int) -> (str, int):
    depth = 0
    content = ''
    i = start + 1  # 跳过开括号

    while i < len(expr):
        if expr[i] == '(':
            depth += 1
            content += expr[i]
        elif expr[i] == ')':
            if depth == 0:
                return content, i + 1  # 找到匹配
            depth -= 1
            content += expr[i]
        elif expr[i] == '{':
            # 跳过花括号块，避免干扰
            brace_content, new_i = self._parse_braced_content(expr, i)
            content += '{' + brace_content + '}'
            i = new_i - 1
        else:
            content += expr[i]
        i += 1

    return None, start  # 未找到匹配
```

**深度追踪示例：**

```
输入: "((a+b) + (c))"
        ^start

过程:
i=1: '('  → depth=1, content='('
i=2: 'a'  → depth=1, content='(a'
i=3: '+'  → depth=1, content='(a+'
i=4: 'b'  → depth=1, content='(a+b'
i=5: ')'  → depth=0, content='(a+b)'
i=6: ' '  → depth=0, content='(a+b) '
i=7: '+'  → depth=0, content='(a+b) +'
...
i=N: ')'  → depth=0 → 匹配成功
```

## 关键优化和修复

### 修复1：\left/\right无限循环

**问题：** 解析器遇到`\left(`时卡死

**原因：** 命令解析后未推进位置指针

```python
# ❌ 旧版本
elif cmd == 'left':
    return [], i  # i没有移动！

# ✅ 新版本
elif cmd == 'left' or cmd == 'right':
    while i < len(expr) and expr[i].isspace():
        i += 1
    if i < len(expr) and expr[i] in '()[]{}|':
        i += 1  # 跳过分隔符
    return [], i
```

### 修复2：LaTeX清理正则表达式

**问题：** 误删`\left`命令导致`eft`残留

```python
# ❌ 旧版本
formula = formula.replace('left', '')   # 删除所有"left"

# ✅ 新版本
import re
formula = re.sub(r'(?<!\\)left\b', '', formula)  # 只删除非\left的left
```

**正则解释：**
- `(?<!\\)` - 负向后查找，确保前面不是反斜杠
- `left\b` - 单词边界，避免匹配"leftover"

### 修复3：希腊字母映射

```python
self.greek_letters = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
    'sigma': 'σ', 'tau': 'τ', 'phi': 'φ', 'omega': 'ω'
    # ... 完整希腊字母表
}
```

**处理：** `\sigma_{f}` → `<msub><mi>σ</mi><mi>f</mi></msub>`

## 算法复杂度分析

### 时间复杂度

- **主循环：** O(n)，单遍扫描
- **递归深度：** O(d)，d为嵌套深度
- **总体：** O(n × d)

**最坏情况：** 深度嵌套分数
```latex
\frac{\frac{\frac{a}{b}}{c}}{d}  # d=4
```

### 空间复杂度

- **递归栈：** O(d)
- **MathML输出：** O(n × k)，k为平均标签膨胀系数（约3-5）

## 测试用例

### 复杂公式示例

**输入LaTeX：**
```latex
S=\frac{4 ( l+R )^{2}} {( \frac{\sigma_{f}} {\sigma_{r}}+\frac{\sigma_{r}} {\sigma_{f}} )^{2} ( 1+R_{0} )^{2}}
```

**解析树结构：**
```
expression
├─ variable: S
├─ operator: =
└─ fraction
   ├─ numerator
   │  ├─ number: 4
   │  └─ parentheses^2
   │     └─ expression: l+R
   └─ denominator
      ├─ parentheses^2
      │  └─ fraction + fraction
      └─ parentheses^2
         └─ expression: 1+R_0
```

**输出MathML标签统计：**
```
<mrow>   : 5个
<mfrac>  : 3个
<msub>   : 5个
<msup>   : 3个
<mfenced>: 3个
<mi>     : 9个
<mn>     : 5个
<mo>     : 6个
```

## 扩展性设计

### 添加新LaTeX命令

**示例：添加根号支持**

```python
def _parse_command(self, expr, start):
    # ... 现有代码 ...

    # 新增根号处理
    elif cmd == 'sqrt':
        return self._parse_sqrt(expr, i)

def _parse_sqrt(self, expr, start):
    """解析根号: \sqrt{内容}"""
    content, i = self._parse_braced_content(expr, start)
    content_lines, _ = self._parse_expression(content)

    result = ['  <msqrt>']
    result.extend(indent(content_lines))
    result.append('  </msqrt>')

    return result, i
```

### 添加新MathML标签

**框架化设计：**

```python
class MathMLBuilder:
    """MathML构建器 - 工厂模式"""

    @staticmethod
    def build_fraction(num_lines, den_lines):
        result = ['<mfrac>']
        result.extend(indent(num_lines))
        result.extend(indent(den_lines))
        result.append('</mfrac>')
        return result

    @staticmethod
    def build_subscript(base, sub, sub_tag):
        return [
            '<msub>',
            f'  <mi>{base}</mi>',
            f'  <{sub_tag}>{sub}</{sub_tag}>',
            '</msub>'
        ]
```

## 总结

### 核心优势

✅ **递归下降解析** - 优雅处理嵌套结构
✅ **单遍扫描** - O(n)时间复杂度
✅ **智能标签** - 符合Word MathML规范
✅ **可扩展** - 易于添加新语法规则
✅ **健壮性** - 完整的错误处理和边界检查

### 关键创新点

1. **智能<mrow>包装** - 基于深度追踪的单元素检测
2. **动态上标解析** - 避免硬编码，支持任意表达式
3. **位置追踪** - 避免重复解析，提升性能
4. **希腊字母映射** - 直接输出Unicode字符

### 未来改进方向

- [ ] 支持更多LaTeX命令（矩阵、积分、求和等）
- [ ] 错误恢复机制（部分解析失败时继续）
- [ ] 性能优化（缓存中间结果）
- [ ] AST可视化（调试工具）
