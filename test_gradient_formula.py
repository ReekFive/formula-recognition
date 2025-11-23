#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试梯度幅值公式的MathML生成
"""

from final_converter import WordMathMLConverter

def test_gradient_formula():
    """测试梯度幅值公式"""
    converter = WordMathMLConverter()
    
    # 你提到的公式 - 简化版本，使用正确的LaTeX语法
    latex_formula = r"M(x,y) = \sqrt{G_{x}^{2} + G_{y}^{2}}"
    
    print("测试公式:", latex_formula)
    print("\n生成的MathML:")
    mathml = converter.convert(latex_formula)
    print(mathml)
    
    # 让我们也测试一个更简单的版本
    latex_simple = r"\sqrt{a_{x}^{2}}"
    print("\n\n简单测试:", latex_simple)
    print("\n生成的MathML:")
    mathml_simple = converter.convert(latex_simple)
    print(mathml_simple)

if __name__ == '__main__':
    test_gradient_formula()