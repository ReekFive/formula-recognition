#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更详细的调试MathML生成过程
"""

from final_converter import WordMathMLConverter

def debug_detailed():
    """详细调试解析过程"""
    converter = WordMathMLConverter()
    
    # 简单测试用例
    latex = r"\sqrt{G_{x}^{2}}"
    
    print("测试公式:", latex)
    print("\n预处理后的LaTeX:", converter._preprocess(latex))
    
    # 手动模拟解析过程
    formula = converter._preprocess(latex)
    
    # 解析\sqrt命令
    print("\n1. 找到\\sqrt命令，位置0")
    cmd, cmd_length = converter._parse_command(formula, 0)
    print(f"   命令: {cmd}, 长度: {cmd_length}")
    
    # 解析花括号内容
    content_start = 0 + cmd_length  # \sqrt后的位置
    print(f"\n2. 从位置{content_start}开始解析花括号内容")
    content, content_length = converter._parse_braced_content(formula, content_start)
    print(f"   花括号内容: '{content}'")
    print(f"   内容长度: {content_length}")
    
    # 解析花括号内部
    print(f"\n3. 解析花括号内部内容: '{content}'")
    inner_result, inner_pos = converter._parse_formula(content)
    print("   内部解析结果:")
    for i, line in enumerate(inner_result):
        print(f"   {i}: {line}")
    print(f"   内部解析位置: {inner_pos}")
    
    print(f"\n4. 完整公式长度: {len(formula)}")
    print(f"   应该处理到的位置: {content_start + content_length}")
    print(f"   剩余内容: '{formula[content_start + content_length:]}'")
    
    print("\n最终MathML:")
    mathml = converter.convert(latex)
    print(mathml)

if __name__ == '__main__':
    debug_detailed()