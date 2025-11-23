#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试MathML生成过程
"""

from final_converter import WordMathMLConverter

def debug_parsing():
    """调试解析过程"""
    converter = WordMathMLConverter()
    
    # 简单测试用例
    latex = r"\sqrt{G_{x}^{2}}"
    
    print("测试公式:", latex)
    print("\n预处理后的LaTeX:", converter._preprocess(latex))
    
    # 手动调用解析步骤来调试
    result = converter._parse_formula(converter._preprocess(latex))
    
    print("\n解析结果:")
    for i, line in enumerate(result):
        print(f"{i}: {line}")
    
    print("\n最终MathML:")
    mathml = converter.convert(latex)
    print(mathml)

if __name__ == '__main__':
    debug_parsing()