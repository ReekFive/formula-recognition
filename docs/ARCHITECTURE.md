# 公式识别器架构文档

## 系统概述

公式识别器是一个基于Python的数学公式识别工具，能够将公式图片转换为LaTeX和MathML格式，特别优化了与Microsoft Word的兼容性。

## 技术架构

### 核心组件

1. **FormulaRecognizer** (`recognizer.py`)
   - 职责：图像预处理和公式识别
   - 技术：Pix2Text OCR引擎
   - 功能：图像降噪、阈值处理、LaTeX公式提取

2. **FormulaConverter** (`converter.py`)
   - 职责：公式格式转换
   - 功能：LaTeX ↔ MathML转换，Word兼容性优化

3. **WordMathMLConverter** (`final_converter.py`)
   - 职责：生成Word兼容的MathML
   - 技术：专业级LaTeX解析器
   - 特点：AST解析，精确的MathML结构

### Web界面

- **Flask应用** (`app.py`)：RESTful API服务
- **前端模板** (`templates/index.html`)：响应式Web界面
- **功能**：拖拽上传、剪贴板粘贴、实时预览

## 数据流

```
用户上传图片 → Flask接收 → FormulaRecognizer识别 → FormulaConverter转换 → 返回结果
```

## 关键技术

### OCR引擎
- **Pix2Text**：专门用于数学公式识别
- **图像预处理**：高斯模糊、自适应阈值
- **错误处理**：left/right命令清理

### 公式转换
- **LaTeX解析**：递归下降解析器
- **MathML生成**：Word兼容格式
- **符号映射**：希腊字母、数学符号

## 部署架构

```
前端 (HTML/CSS/JS) 
    ↓ HTTP
Flask后端 (Python)
    ↓ 函数调用
识别器 (Pix2Text)
    ↓ 转换
转换器 (LaTeX→MathML)
```

## 性能优化

1. **图像预处理**：提高识别准确率
2. **缓存机制**：避免重复识别
3. **错误恢复**：多种降级策略
4. **并发处理**：支持批量识别

## 扩展性

- **模块化设计**：各组件独立可替换
- **插件机制**：支持新的OCR引擎
- **格式扩展**：易于添加新输出格式