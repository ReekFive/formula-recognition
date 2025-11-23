#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本
运行核心功能测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_functionality():
    """测试基础功能"""
    print("🧪 开始基础功能测试...")
    
    try:
        # 测试导入
        from recognizer import FormulaRecognizer
        from converter import FormulaConverter
        from final_converter import WordMathMLConverter
        print("✅ 模块导入成功")
        
        # 测试转换器
        converter = WordMathMLConverter()
        test_formula = "E = mc^2"
        result = converter.convert(test_formula)
        
        if result and "<math" in result:
            print(f"✅ 公式转换成功: {test_formula}")
        else:
            print(f"❌ 公式转换失败: {test_formula}")
            return False
            
        # 测试简单LaTeX公式
        test_cases = [
            "x^2 + y^2 = z^2",
            "\frac{a}{b}",
            "\alpha + \beta",
            "\sqrt{x}",
            "a_{1} + a_{2}"
        ]
        
        for formula in test_cases:
            result = converter.convert(formula)
            if result and "<math" in result:
                print(f"✅ 测试通过: {formula}")
            else:
                print(f"❌ 测试失败: {formula}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("公式识别器 - 快速测试")
    print("=" * 60)
    
    if test_basic_functionality():
        print("\n🎉 所有测试通过！系统运行正常")
    else:
        print("\n❌ 测试失败，请检查环境配置")
        sys.exit(1)

if __name__ == '__main__':
    main()