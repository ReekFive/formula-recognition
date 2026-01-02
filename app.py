import os
import uuid
import time
import threading
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory, g
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
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

# 速率限制配置
RATE_LIMIT_WINDOW = 60  # 60秒
RATE_LIMIT_MAX_REQUESTS = 30  # 每窗口最大请求数
rate_limit_store = {}
rate_limit_lock = threading.Lock()

# 上传清理配置
UPLOAD_MAX_AGE = 3600  # 1小时后清理

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# 初始化识别器和转换器
recognizer = FormulaRecognizer()
converter = FormulaConverter()


def rate_limit(f):
    """速率限制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        with rate_limit_lock:
            if client_ip not in rate_limit_store:
                rate_limit_store[client_ip] = []
            
            # 清理过期请求记录
            rate_limit_store[client_ip] = [
                t for t in rate_limit_store[client_ip] 
                if current_time - t < RATE_LIMIT_WINDOW
            ]
            
            if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': RATE_LIMIT_WINDOW
                }), 429
            
            rate_limit_store[client_ip].append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function


def cleanup_old_uploads():
    """清理过期的上传文件"""
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        current_time = time.time()
        
        for filename in os.listdir(upload_folder):
            filepath = os.path.join(upload_folder, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > UPLOAD_MAX_AGE:
                    os.remove(filepath)
                    logger.info(f"清理过期文件: {filename}")
    except Exception as e:
        logger.error(f"清理文件失败: {e}")


def is_safe_path(basedir, path):
    """检查路径是否安全（防止路径遍历）"""
    # 解析绝对路径
    abs_base = os.path.abspath(basedir)
    abs_path = os.path.abspath(path)
    
    # 检查路径是否在允许的目录内
    return abs_path.startswith(abs_base + os.sep) or abs_path == abs_base


def validate_file_type(filepath):
    """验证文件真实类型（使用文件头魔数）"""
    # 图片文件魔数
    magic_numbers = {
        b'\x89PNG\r\n\x1a\n': 'png',
        b'\xff\xd8\xff': 'jpg',
        b'GIF87a': 'gif',
        b'GIF89a': 'gif',
        b'BM': 'bmp',
        b'II*\x00': 'tiff',
        b'MM\x00*': 'tiff',
        b'RIFF': 'webp',  # RIFF开头可能是webp
    }
    
    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)
        
        for magic, file_type in magic_numbers.items():
            if header.startswith(magic):
                return True, file_type
        
        # 额外检查 WEBP (RIFF....WEBP)
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return True, 'webp'
        
        return False, None
    except Exception as e:
        logger.error(f"文件类型验证失败: {e}")
        return False, None


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
@rate_limit
def upload_file():
    """处理文件上传和公式识别"""
    try:
        # 定期清理旧文件
        cleanup_old_uploads()
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型（扩展名）
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 保存文件
        file.save(filepath)
        logger.info(f"文件已保存: {filepath}")
        
        # 验证文件真实类型
        is_valid, detected_type = validate_file_type(filepath)
        if not is_valid:
            os.remove(filepath)  # 删除非法文件
            logger.warning(f"文件类型验证失败，已删除: {filepath}")
            return jsonify({'error': '文件类型验证失败，请上传有效的图片文件'}), 400
        
        # 识别公式
        latex_formula = recognizer.recognize_formula(filepath)
        
        # 识别完成后删除文件
        try:
            os.remove(filepath)
        except Exception as e:
            logger.warning(f"删除文件失败: {e}")
        
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
@rate_limit
def api_recognize():
    """API接口：识别公式（仅限上传目录内的文件）"""
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({'error': '缺少image_path参数'}), 400
        
        image_path = data['image_path']
        
        # 安全检查：路径必须在上传目录内
        if not is_safe_path(app.config['UPLOAD_FOLDER'], image_path):
            logger.warning(f"拒绝非法路径访问: {image_path}")
            return jsonify({'error': '非法路径，只允许访问上传目录内的文件'}), 403
        
        if not os.path.exists(image_path):
            return jsonify({'error': '图片文件不存在'}), 400
        
        # 验证文件类型
        is_valid, _ = validate_file_type(image_path)
        if not is_valid:
            return jsonify({'error': '无效的图片文件'}), 400
        
        # 识别公式
        latex_formula = recognizer.recognize_formula(image_path)
        
        if latex_formula:
            conversion_result = converter.convert_formula(latex_formula)
            return jsonify({
                'success': True,
                'latex': conversion_result['latex'],
                'mathml': conversion_result.get('mathml', ''),
                'mathml_word_compatible': conversion_result['mathml_word_compatible'],
                'latex_display': conversion_result['latex_display'],
                'mathml_valid': conversion_result.get('mathml_valid', False)
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
@rate_limit
def api_convert():
    """API接口：转换公式格式"""
    try:
        data = request.get_json()
        if not data or 'latex' not in data:
            return jsonify({'error': '缺少latex参数'}), 400
        
        latex_formula = data['latex']
        
        # 基本输入验证
        if len(latex_formula) > 10000:
            return jsonify({'error': 'LaTeX公式过长'}), 400
        
        conversion_result = converter.convert_formula(latex_formula)
        
        return jsonify({
            'success': True,
            'latex': conversion_result['latex'],
            'mathml': conversion_result.get('mathml', ''),
            'mathml_word_compatible': conversion_result['mathml_word_compatible'],
            'latex_display': conversion_result['latex_display'],
            'mathml_valid': conversion_result.get('mathml_valid', False)
        })
        
    except Exception as e:
        logger.error(f"转换API调用出错: {e}")
        return jsonify({'error': f'转换出错: {str(e)}'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件（安全检查）"""
    # 确保文件名安全
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 验证路径安全
    if not is_safe_path(app.config['UPLOAD_FOLDER'], filepath):
        return jsonify({'error': '非法路径'}), 403
    
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


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """速率限制错误处理"""
    return jsonify({'error': '请求过于频繁，请稍后再试'}), 429


if __name__ == '__main__':
    # 检查识别器状态
    if recognizer.p2t is None:
        logger.warning("Pix2Text未初始化，公式识别功能可能无法正常工作")
        print("警告: Pix2Text初始化失败，请确保已安装相关依赖库")
    
    print("正在启动公式识别器服务...")
    print("访问 http://localhost:8081 使用Web界面")
    
    # 生产环境应使用 gunicorn 或 uwsgi
    # 这里保留 debug=True 仅用于开发，通过环境变量控制
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=8081, debug=debug_mode)