import cv2
import numpy as np
from PIL import Image
import pix2text
from typing import Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormulaRecognizer:
    """数学公式识别器"""
    
    def __init__(self):
        """初始化识别器"""
        try:
            self.p2t = pix2text.Pix2Text()
            logger.info("Pix2Text 初始化成功")
        except Exception as e:
            logger.error(f"Pix2Text 初始化失败: {e}")
            self.p2t = None
    
    def preprocess_image(self, image_path: str) -> str:
        """
        预处理图片以提高识别准确率
        
        Args:
            image_path: 图片路径
            
        Returns:
            预处理后的图片路径
        """
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊降噪
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作去除噪点
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 保存处理后的图片
            processed_path = image_path.replace('.', '_processed.')
            cv2.imwrite(processed_path, processed)
            
            logger.info(f"图片预处理完成: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"图片预处理失败: {e}")
            return image_path  # 如果预处理失败，返回原图
    
    def recognize_formula(self, image_path: str, preprocess: bool = True) -> Optional[str]:
        """
        识别数学公式
        
        Args:
            image_path: 图片路径
            preprocess: 是否进行预处理
            
        Returns:
            识别出的LaTeX公式，失败返回None
        """
        if not self.p2t:
            logger.error("Pix2Text 未初始化")
            return None
        
        try:
            # 图片预处理
            if preprocess:
                processed_path = self.preprocess_image(image_path)
            else:
                processed_path = image_path
            
            # 使用Pix2Text识别公式
            result = self.p2t.recognize(processed_path)
            
            if isinstance(result, dict):
                # 提取LaTeX公式
                latex_formula = result.get('text', '')
                if not latex_formula:
                    latex_formula = result.get('latex', '')
            else:
                latex_formula = str(result)
            
            if latex_formula:
                # 清理LaTeX公式，移除多余的$$符号
                cleaned_formula = self._clean_latex_formula(latex_formula)
                logger.info(f"公式识别成功: {cleaned_formula[:50]}...")
                return cleaned_formula
            else:
                logger.warning("未识别到公式内容")
                return None
                
        except Exception as e:
            logger.error(f"公式识别失败: {e}")
            return None
    
    def _clean_latex_formula(self, latex_formula: str) -> str:
        """
        清理LaTeX公式，移除多余的格式符号
        
        Args:
            latex_formula: 原始LaTeX公式
            
        Returns:
            清理后的LaTeX公式
        """
        if not latex_formula:
            return ""
        
        formula = latex_formula.strip()
        
        # 移除行首和行尾的$$符号
        if formula.startswith('$$') and formula.endswith('$$'):
            formula = formula[2:-2].strip()
        elif formula.startswith('$') and formula.endswith('$'):
            formula = formula[1:-1].strip()
        
        # 移除行首和行尾的\[ \]符号
        if formula.startswith(r'\[') and formula.endswith(r'\]'):
            formula = formula[2:-2].strip()
        
        # 移除行首和行尾的\( \)符号
        if formula.startswith(r'\(') and formula.endswith(r'\)'):
            formula = formula[2:-2].strip()
        
        # 清理错误的left和right命令（Pix2Text有时会错误地添加这些）
        # 将 \left( 替换为 (
        formula = formula.replace(r'\left(', '(')
        formula = formula.replace(r'\right)', ')')
        
        # 将 \left| 替换为 |
        formula = formula.replace(r'\left|', '|')
        formula = formula.replace(r'\right|', '|')
        
        # 清理其他left/right变体
        formula = formula.replace(r'\left{', '{')
        formula = formula.replace(r'\right}', '}')
        
        formula = formula.replace(r'\left[', '[')
        formula = formula.replace(r'\right]', ']')
        
        # 移除孤立的left和right命令（带反斜杠的）
        formula = formula.replace(r'\left', '')
        formula = formula.replace(r'\right', '')
        
        # 清理小写的left和right（Pix2Text有时会输出这些）
        formula = formula.replace('left(', '(')
        formula = formula.replace('right)', ')')
        formula = formula.replace('left|', '|')
        formula = formula.replace('right|', '|')
        formula = formula.replace('left', '')
        formula = formula.replace('right', '')
        
        return formula.strip()
    
    def batch_recognize(self, image_paths: list) -> list:
        """
        批量识别多个图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            识别结果列表
        """
        results = []
        for path in image_paths:
            result = self.recognize_formula(path)
            results.append({
                'image_path': path,
                'formula': result,
                'success': result is not None
            })
        return results
    
    def validate_formula(self, latex_formula: str) -> bool:
        """
        验证LaTeX公式的基本格式
        
        Args:
            latex_formula: LaTeX公式
            
        Returns:
            是否有效
        """
        if not latex_formula or not isinstance(latex_formula, str):
            return False
        
        # 基本验证：检查是否包含数学符号
        math_symbols = ['\\', '{', '}', '^', '_', r'\frac', r'\sum', r'\int', r'\lim']
        return any(symbol in latex_formula for symbol in math_symbols)


# 测试函数
def test_recognizer():
    """测试识别器功能"""
    recognizer = FormulaRecognizer()
    
    # 这里可以添加测试图片路径
    test_image = "test_formula.png"
    
    print("正在初始化公式识别器...")
    print("识别器状态:", "正常" if recognizer.p2t else "异常")
    
    if recognizer.p2t:
        print("公式识别器已准备就绪")
    else:
        print("公式识别器初始化失败，请检查依赖库")


if __name__ == "__main__":
    test_recognizer()