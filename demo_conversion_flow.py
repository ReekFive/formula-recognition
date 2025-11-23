#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示完整的转换流程：图片 → LaTeX → MathML
"""

from recognizer import FormulaRecognizer
from converter import FormulaConverter
from final_converter import WordMathMLConverter
import os

def demonstrate_conversion_pipeline():
    """演示完整的转换流程"""
    
    print("🔄 公式识别器完整转换流程演示")
    print("=" * 60)
    
    # 1. 模拟OCR识别结果（跳过实际的图片处理）
    print("\n1️⃣ 模拟OCR识别结果:")
    print("-" * 30)
    
    # 假设这是从图片识别出来的LaTeX
    sample_latex_formulas = [
        r"M(x,y) = \sqrt{G_{x}^{2} + G_{y}^{2}}",
        r"\frac{a}{b} + \frac{c}{d}",
        r"\sum_{i=1}^{n} x_i^2",
        r"\int_{0}^{\infty} e^{-x^2} dx"
    ]
    
    # 2. 初始化转换器
    converter = FormulaConverter()
    word_converter = WordMathMLConverter()
    
    for i, latex_formula in enumerate(sample_latex_formulas, 1):
        print(f"\n📊 测试公式 {i}: {latex_formula}")
        print("-" * 40)
        
        # 3. 转换为MathML（基础版本）
        basic_mathml = converter.latex_to_mathml(latex_formula)
        print(f"\n📝 基础MathML:")
        print(basic_mathml if basic_mathml else "转换失败")
        
        # 4. 转换为Word兼容MathML（高级版本）
        advanced_mathml = word_converter.convert(latex_formula)
        print(f"\n🎯 Word兼容MathML:")
        print(advanced_mathml if advanced_mathml else "转换失败")
        
        # 5. 生成显示用LaTeX
        latex_display = f"$${latex_formula}$$"
        print(f"\n🖥️  显示用LaTeX:")
        print(latex_display)
        
        # 6. 完整输出格式
        full_result = converter.format_output(latex_formula, basic_mathml)
        print(f"\n📦 完整输出格式:")
        print(f"   LaTeX: {full_result['latex']}")
        print(f"   LaTeX显示: {full_result['latex_display']}")
        print(f"   Word MathML: {full_result['mathml_word_compatible'][:100]}...")
        
        print("\n" + "="*60)
    
    print("\n✅ 转换流程总结:")
    print("1. 图片 → Pix2Text OCR → LaTeX (识别阶段)")
    print("2. LaTeX → 基础MathML (基础转换)")
    print("3. LaTeX → Word兼容MathML (高级转换)")
    print("4. LaTeX → 显示用LaTeX (添加$$包装)")
    print("5. 前端: LaTeX + MathJax → 可视化公式")
    print("6. 复制: MathML → Word粘贴")

if __name__ == '__main__':
    demonstrate_conversion_pipeline()