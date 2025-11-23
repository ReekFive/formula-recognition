import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from recognizer import FormulaRecognizer
from converter import FormulaConverter
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大文件大小16MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# 初始化识别器和转换器
recognizer = FormulaRecognizer()
converter = FormulaConverter()


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和公式识别"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 保存文件
        file.save(filepath)
        logger.info(f"文件已保存: {filepath}")
        
        # 识别公式
        latex_formula = recognizer.recognize_formula(filepath)
        
        if latex_formula:
            # 转换为MathML
            conversion_result = converter.convert_formula(latex_formula)
            
            result = {
                'success': True,
                'filename': filename,
                'latex': conversion_result['latex'],
                'mathml_word_compatible': conversion_result['mathml_word_compatible'],
                'latex_display': conversion_result['latex_display']
            }
            
            logger.info(f"公式识别成功: {latex_formula[:50]}...")
            return jsonify(result)
        else:
            logger.warning("公式识别失败")
            return jsonify({
                'success': False,
                'error': '无法识别图片中的公式，请确保图片清晰且包含有效的数学公式'
            }), 400
            
    except Exception as e:
        logger.error(f"处理上传文件时出错: {e}")
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500


@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    """API接口：识别公式"""
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({'error': '缺少image_path参数'}), 400
        
        image_path = data['image_path']
        if not os.path.exists(image_path):
            return jsonify({'error': '图片文件不存在'}), 400
        
        # 识别公式
        latex_formula = recognizer.recognize_formula(image_path)
        
        if latex_formula:
            conversion_result = converter.convert_formula(latex_formula)
            return jsonify({
                'success': True,
                'latex': conversion_result['latex'],
                'mathml': conversion_result['mathml'],
                'latex_display': conversion_result['latex_display'],
                'mathml_valid': conversion_result['mathml_valid']
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法识别公式'
            }), 400
            
    except Exception as e:
        logger.error(f"API调用出错: {e}")
        return jsonify({'error': f'API调用出错: {str(e)}'}), 500


@app.route('/api/convert', methods=['POST'])
def api_convert():
    """API接口：转换公式格式"""
    try:
        data = request.get_json()
        if not data or 'latex' not in data:
            return jsonify({'error': '缺少latex参数'}), 400
        
        latex_formula = data['latex']
        conversion_result = converter.convert_formula(latex_formula)
        
        return jsonify({
            'success': True,
            'latex': conversion_result['latex'],
            'mathml': conversion_result['mathml'],
            'latex_display': conversion_result['latex_display'],
            'mathml_valid': conversion_result['mathml_valid']
        })
        
    except Exception as e:
        logger.error(f"转换API调用出错: {e}")
        return jsonify({'error': f'转换出错: {str(e)}'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'recognizer_ready': recognizer.p2t is not None,
        'converter_ready': True
    })


@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，最大支持16MB'}), 413


if __name__ == '__main__':
    # 检查识别器状态
    if recognizer.p2t is None:
        logger.warning("Pix2Text未初始化，公式识别功能可能无法正常工作")
        print("警告: Pix2Text初始化失败，请确保已安装相关依赖库")
    
    print("正在启动公式识别器服务...")
    print("访问 http://localhost:8081 使用Web界面")
    
    app.run(host='0.0.0.0', port=8081, debug=True)