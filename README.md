# 公式识别器

一个基于Python的数学公式识别工具，可以将公式图片转换为LaTeX和MathML格式。

## 功能特点

- 🎯 高精度数学公式识别
- 🔄 支持LaTeX和MathML格式输出
- 🌐 Web界面操作
- 📱 支持图片拖拽上传
- ⚡ 快速识别响应

## 技术栈

- **后端**: Python, Flask
- **OCR引擎**: Pix2Text
- **图像处理**: Pillow, OpenCV
- **公式转换**: latex2mathml, SymPy

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python app.py
```

### 访问应用
打开浏览器访问 `http://localhost:5000`

## 使用说明

1. 上传包含数学公式的图片
2. 系统自动识别公式
3. 获取LaTeX和MathML格式的输出

## 项目结构

```
formula-recognition/
├── app.py                 # Flask Web应用
├── recognizer.py          # 公式识别核心模块
├── converter.py           # 格式转换模块
├── templates/             # HTML模板
├── static/               # 静态文件
├── uploads/              # 上传文件存储
└── requirements.txt      # 依赖列表
```

## 许可证

MIT License