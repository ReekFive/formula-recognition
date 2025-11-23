# 公式识别器

一个基于Python的数学公式识别工具，可以将公式图片转换为LaTeX和MathML格式，特别优化了与Microsoft Word的兼容性。

## 🎯 功能特点

- **高精度识别**：基于Pix2Text OCR引擎，专门用于数学公式识别
- **多格式输出**：支持LaTeX和MathML(Word兼容)格式
- **便捷操作**：支持拖拽上传、点击上传和剪贴板粘贴(Ctrl+V)
- **桌面优化**：横版布局设计，专为桌面端优化
- **快速响应**：实时识别和转换，支持复杂数学公式

## 🚀 快速开始

### 方法一：使用设置脚本（推荐）
```bash
# 设置开发环境
python scripts/setup.py

# 启动应用
python scripts/run.py
```

### 方法二：手动安装
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

### 访问应用
打开浏览器访问 `http://localhost:8081`

## 📋 使用说明

1. **上传图片**：拖拽、点击或粘贴(Ctrl+V)包含数学公式的图片
2. **自动识别**：系统自动识别图片中的数学公式
3. **获取结果**：获得LaTeX和MathML(Word)格式的公式
4. **复制使用**：点击复制按钮，粘贴到目标应用中

## 🏗️ 项目结构

```
formula-recognition/
├── app.py                    # Flask Web应用主入口
├── recognizer.py            # 公式识别核心模块
├── converter.py             # 格式转换模块
├── final_converter.py       # Word兼容MathML转换器
├── requirements.txt          # 项目依赖
├── scripts/                  # 工具脚本
│   ├── setup.py             # 环境设置脚本
│   ├── run.py               # 应用启动脚本
│   └── test.py              # 快速测试脚本
├── tests/                    # 测试文件
│   ├── test_cleaning.py     # 清理功能测试
│   ├── test_complete_conversion.py  # 完整转换测试
│   ├── test_complex_formula.py      # 复杂公式测试
│   └── test_full_pipeline.py        # 完整流程测试
├── docs/                     # 项目文档
│   ├── ARCHITECTURE.md      # 架构文档
│   └── USAGE.md             # 使用指南
├── examples/                 # 使用示例
│   └── README.md            # 示例说明
└── templates/
    └── index.html           # Web界面模板
```

## 🔧 技术栈

- **后端**: Python 3.8+, Flask
- **OCR引擎**: Pix2Text（专门用于数学公式识别）
- **图像处理**: Pillow, OpenCV
- **公式转换**: 自定义LaTeX到MathML转换器
- **前端**: HTML5, CSS3, JavaScript

## 🧪 测试

```bash
# 运行快速测试
python scripts/test.py

# 运行具体测试
python tests/test_complex_formula.py
```

## 📖 文档

- [架构文档](docs/ARCHITECTURE.md) - 系统设计和架构说明
- [使用指南](docs/USAGE.md) - 详细使用说明和故障排除
- [示例](examples/README.md) - 使用示例和API文档

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License