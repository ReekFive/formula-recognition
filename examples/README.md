# 公式识别器示例

## 示例1：基础数学公式

### 输入图片
包含公式：`E = mc^2`

### 预期输出
- **LaTeX**: `E = mc^2`
- **MathML(Word)**: 
```xml
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>E</mi>
  <mo>=</mo>
  <mi>m</mi>
  <msup>
    <mrow><mi>c</mi></mrow>
    <mrow><mn>2</mn></mrow>
  </msup>
</math>
```

## 示例2：复杂公式

### 输入图片
包含公式：`C_total (p,d)=ω(p)⋅C_census (p,d)+(1-ω(p))⋅|d-D_geo (p)|`

### 预期输出
- **LaTeX**: `C_total (p,d)=ω(p)⋅C_census (p,d)+(1-ω(p))⋅|d-D_geo (p)|`
- **MathML(Word)**: 正确的Word兼容格式

## 示例3：分式和根号

### 输入图片
包含公式：`\frac{x^2 + y^2}{z^2} = \sqrt{a^2 + b^2}`

### 预期输出
- **LaTeX**: `\frac{x^2 + y^2}{z^2} = \sqrt{a^2 + b^2}`
- **MathML(Word)**: 包含mfrac和msqrt元素的格式

## 使用示例

### Python代码示例
```python
from recognizer import FormulaRecognizer
from converter import FormulaConverter

# 创建识别器
recognizer = FormulaRecognizer()

# 识别公式
latex = recognizer.recognize_formula("formula.png")

# 转换格式
converter = FormulaConverter()
result = converter.format_output(latex, "")

print("LaTeX:", result['latex'])
print("MathML:", result['mathml_word_compatible'])
```

### API使用示例
```bash
# 上传图片识别
curl -X POST -F "file=@formula.png" http://localhost:8081/api/recognize

# 预期响应
{
  "success": true,
  "latex": "E = mc^2",
  "mathml_word_compatible": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\">...</math>"
}
```