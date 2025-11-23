from latex2mathml.converter import convert as latex_to_mathml
from typing import Optional
import sympy as sp
from sympy import latex, mathml
import logging
from final_converter import WordMathMLConverter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormulaConverter:
    """公式格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.advanced_word_converter = WordMathMLConverter()
    
    def latex_to_mathml(self, latex_formula: str) -> Optional[str]:
        """
        将LaTeX公式转换为MathML格式
        
        Args:
            latex_formula: LaTeX公式字符串
            
        Returns:
            MathML格式字符串，失败返回None
        """
        if not latex_formula or not isinstance(latex_formula, str):
            logger.error("无效的LaTeX公式")
            return None
        
        try:
            # 使用latex2mathml库转换
            mathml_result = latex_to_mathml(latex_formula)
            logger.info("LaTeX转MathML成功")
            return mathml_result
            
        except Exception as e:
            logger.error(f"LaTeX转MathML失败: {e}")
            
            # 备用方案：使用SymPy
            try:
                # 尝试用SymPy解析和转换
                sympy_expr = self._latex_to_sympy(latex_formula)
                if sympy_expr:
                    mathml_result = mathml(sympy_expr)
                    logger.info("使用SymPy转换成功")
                    return mathml_result
            except Exception as sympy_error:
                logger.error(f"SymPy转换也失败: {sympy_error}")
            
            return None
    
    def _latex_to_sympy(self, latex_formula: str) -> Optional[sp.Basic]:
        """
        将LaTeX公式转换为SymPy表达式
        
        Args:
            latex_formula: LaTeX公式字符串
            
        Returns:
            SymPy表达式，失败返回None
        """
        try:
            # 清理LaTeX公式
            cleaned_latex = self._clean_latex(latex_formula)
            
            # 使用SymPy解析LaTeX
            expr = sp.sympify(cleaned_latex)
            return expr
            
        except Exception as e:
            logger.error(f"SymPy解析失败: {e}")
            return None
    
    def _clean_latex(self, latex_formula: str) -> str:
        """
        清理LaTeX公式，移除不必要的格式
        
        Args:
            latex_formula: 原始LaTeX公式
            
        Returns:
            清理后的LaTeX公式
        """
        if not latex_formula:
            return ""
        
        # 移除公式环境标记
        cleaned = latex_formula.strip()
        
        # 移除常见的LaTeX环境
        environments_to_remove = [
            r'\begin{equation}',
            r'\end{equation}',
            r'\begin{equation*}',
            r'\end{equation*}',
            r'\[',
            r'\]',
            r'$',
            r'\begin{align}',
            r'\end{align}',
            r'\begin{align*}',
            r'\end{align*}'
        ]
        
        for env in environments_to_remove:
            cleaned = cleaned.replace(env, '')
        
        # 清理多余的空格
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def validate_word_mathml(self, mathml_string: str) -> bool:
        """
        验证Word兼容MathML格式的有效性
        
        Args:
            mathml_string: MathML字符串
            
        Returns:
            是否有效
        """
        if not mathml_string or not isinstance(mathml_string, str):
            return False
        
        # Word MathML验证：检查必要的XML声明和命名空间
        required_elements = [
            '<?xml version="1.0"',
            'xmlns="http://www.w3.org/1998/Math/MathML"',
            '<math',
            '</math>'
        ]
        
        return all(elem in mathml_string for elem in required_elements)
    
    def validate_mathml(self, mathml_string: str) -> bool:
        """
        验证MathML格式的基本有效性
        
        Args:
            mathml_string: MathML字符串
            
        Returns:
            是否有效
        """
        if not mathml_string or not isinstance(mathml_string, str):
            return False
        
        # 基本验证：检查MathML标签
        required_tags = ['<math', '</math>']
        return all(tag in mathml_string for tag in required_tags)
    
    def format_output(self, latex_formula: str, mathml_formula: str) -> dict:
        """
        格式化输出结果（简化版，只保留LaTeX和Word MathML）
        
        Args:
            latex_formula: LaTeX公式
            mathml_formula: MathML公式
            
        Returns:
            格式化后的结果字典
        """
        # 生成高级Word兼容MathML（更准确的格式）
        advanced_word_mathml = self.advanced_word_converter.convert(latex_formula) if latex_formula else ""
        
        return {
            'latex': latex_formula,
            'mathml_word_compatible': advanced_word_mathml or mathml_formula,
            'latex_display': f"$${latex_formula}$$" if latex_formula and not (latex_formula.startswith('$$') and latex_formula.endswith('$$')) else latex_formula if latex_formula else "",
        }
    
    def convert_formula(self, latex_formula: str) -> dict:
        """
        转换公式并返回完整结果
        
        Args:
            latex_formula: LaTeX公式
            
        Returns:
            转换结果字典
        """
        if not latex_formula:
            return self.format_output("", "")
        
        # 转换为MathML
        mathml_formula = self.latex_to_mathml(latex_formula)
        
        # 格式化输出
        result = self.format_output(latex_formula, mathml_formula or "")
        
        return result


# 测试函数
def test_converter():
    """测试转换器功能"""
    converter = FormulaConverter()
    
    # 测试用例
    test_formulas = [
        r"\frac{a+b}{c}",
        r"\sum_{i=1}^{n} x_i",
        r"\int_{0}^{\infty} e^{-x} dx",
        r"\alpha + \beta = \gamma"
    ]
    
    print("正在测试公式转换器...")
    
    for formula in test_formulas:
        print(f"\n测试公式: {formula}")
        result = converter.convert_formula(formula)
        
        print(f"LaTeX: {result['latex']}")
        print(f"MathML: {result['mathml'][:100]}...")
        print(f"MathML有效: {result['mathml_valid']}")


if __name__ == "__main__":
    test_converter()