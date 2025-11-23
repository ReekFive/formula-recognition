#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版LaTeX到MathML转换器
专门针对Word兼容性，生成精确的MathML格式
"""

import re

class WordMathMLConverter:
    """Word兼容的MathML转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.mathml_ns = "http://www.w3.org/1998/Math/MathML"
        
        # 希腊字母映射
        self.greek_letters = {
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
            'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
            'nu': 'ν', 'xi': 'ξ', 'pi': 'π', 'rho': 'ρ',
            'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'φ',
            'chi': 'χ', 'psi': 'ψ', 'omega': 'ω'
        }
        
        # 数学符号映射
        self.math_symbols = {
            'cdot': '·', 'times': '×', 'div': '÷',
            'pm': '±', 'mp': '∓', 'neq': '≠',
            'leq': '≤', 'geq': '≥', 'll': '≪', 'gg': '≫',
            'infty': '∞', 'propto': '∝', 'sim': '∼',
            'approx': '≈', 'subset': '⊂', 'supset': '⊃',
            'subseteq': '⊆', 'supseteq': '⊇'
        }
    
    def convert(self, latex: str) -> str:
        """转换LaTeX到MathML"""
        try:
            # 预处理
            latex = self._preprocess(latex)
            
            # 使用递归下降解析器
            result = self._parse_formula(latex)
            
            # 构建MathML
            mathml_lines = ['<math xmlns="http://www.w3.org/1998/Math/MathML">']
            mathml_lines.extend(result)
            mathml_lines.append('</math>')
            
            return '\n'.join(mathml_lines)
            
        except Exception as e:
            print(f"转换失败: {e}")
            return self._create_basic_mathml(latex)
    
    def _preprocess(self, latex: str) -> str:
        """预处理LaTeX"""
        latex = latex.strip()
        
        # 移除公式环境标记
        if latex.startswith('$$') and latex.endswith('$$'):
            latex = latex[2:-2].strip()
        elif latex.startswith('$') and latex.endswith('$'):
            latex = latex[1:-1].strip()
        elif latex.startswith(r'\[') and latex.endswith(r'\]'):
            latex = latex[2:-2].strip()
        
        return latex
    
    def _parse_formula(self, formula: str) -> list:
        """解析公式"""
        result = []
        i = 0
        
        while i < len(formula):
            char = formula[i]
            
            # 跳过空格
            if char.isspace():
                i += 1
                continue
            
            # LaTeX命令
            if char == '\\':
                cmd, length = self._parse_command(formula, i)
                result.extend(self._handle_command(cmd, formula, i + length))
                i += length
            
            # 上标
            elif char == '^':
                if result:
                    # 获取底数
                    base = result.pop()
                    
                    # 解析上标内容
                    if i + 1 < len(formula) and formula[i + 1] == '{':
                        superscript, length = self._parse_braced_content(formula, i + 1)
                        i += length
                    else:
                        superscript = formula[i + 1] if i + 1 < len(formula) else ''
                        i += 1
                    
                    # 生成上标MathML
                    result.append('  <msup>')
                    result.append('    <mrow>')
                    result.append(f'      {base}')
                    result.append('    </mrow>')
                    result.append('    <mrow>')
                    result.extend(self._parse_formula(superscript))
                    result.append('    </mrow>')
                    result.append('  </msup>')
                i += 1
            
            # 下标
            elif char == '_':
                if result:
                    # 获取底数
                    base = result.pop()
                    
                    # 解析下标内容
                    if i + 1 < len(formula) and formula[i + 1] == '{':
                        subscript, length = self._parse_braced_content(formula, i + 1)
                        i += length
                    else:
                        subscript = formula[i + 1] if i + 1 < len(formula) else ''
                        i += 1
                    
                    # 生成下标MathML（严格按照Word格式）
                    result.append('   <msub>')
                    result.append('     <mrow>')
                    result.append(f'       {base}')
                    result.append('     </mrow>')
                    result.append('     <mrow>')
                    result.extend(self._parse_formula(subscript))
                    result.append('     </mrow>')
                    result.append('   </msub>')
                i += 1
            
            # 数学运算符
            elif char in '+-=<>≠≤≥×÷·()[]|,':
                op_map = {
                    '+': '+', '-': '-', '=': '=',
                    '(': '(', ')': ')', '[': '[', ']': ']',
                    '|': '|', ',': ',', '.': '.'
                }
                op_text = op_map.get(char, char)
                result.append(f'  <mo>{op_text}</mo>')
                i += 1
            
            # 数字
            elif char.isdigit() or char == '.':
                num = char
                i += 1
                while i < len(formula) and (formula[i].isdigit() or formula[i] == '.'):
                    num += formula[i]
                    i += 1
                result.append(f'  <mn>{num}</mn>')
            
            # 字母变量
            elif char.isalpha():
                var = char
                i += 1
                while i < len(formula) and formula[i].isalpha():
                    var += formula[i]
                    i += 1
                
                # 将多字符变量名拆分为单个字符（Word要求）
                for c in var:
                    result.append(f'  <mi>{c}</mi>')
            
            # 其他字符
            else:
                result.append(f'  <mi>{char}</mi>')
                i += 1
        
        return result
    
    def _parse_command(self, formula: str, start: int) -> tuple:
        """解析LaTeX命令"""
        i = start + 1  # 跳过反斜杠
        cmd = ''
        
        while i < len(formula) and formula[i].isalpha():
            cmd += formula[i]
            i += 1
        
        return f'\\{cmd}', i - start
    
    def _parse_braced_content(self, formula: str, start: int) -> tuple:
        """解析花括号内容"""
        if start >= len(formula) or formula[start] != '{':
            return '', 1
        
        brace_count = 0
        content = ''
        i = start + 1
        
        while i < len(formula):
            if formula[i] == '{':
                brace_count += 1
            elif formula[i] == '}':
                if brace_count == 0:
                    break
                brace_count -= 1
            content += formula[i]
            i += 1
        
        return content, i - start + 1
    
    def _handle_command(self, cmd: str, formula: str, start: int) -> list:
        """处理LaTeX命令"""
        cmd_name = cmd[1:]  # 移除反斜杠
        
        # 希腊字母
        if cmd_name in self.greek_letters:
            return [f'  <mi>{self.greek_letters[cmd_name]}</mi>']
        
        # 数学符号
        elif cmd_name in self.math_symbols:
            return [f'  <mo>{self.math_symbols[cmd_name]}</mo>']
        
        # 分数
        elif cmd_name == 'frac':
            # 解析分子和分母
            numerator, len1 = self._parse_braced_content(formula, start)
            denominator, len2 = self._parse_braced_content(formula, start + len1)
            
            result = ['  <mfrac>']
            result.append('    <mrow>')
            result.extend(self._parse_formula(numerator))
            result.append('    </mrow>')
            result.append('    <mrow>')
            result.extend(self._parse_formula(denominator))
            result.append('    </mrow>')
            result.append('  </mfrac>')
            
            return result
        
        # 平方根
        elif cmd_name == 'sqrt':
            content, length = self._parse_braced_content(formula, start)
            
            result = ['  <msqrt>']
            result.append('    <mrow>')
            result.extend(self._parse_formula(content))
            result.append('    </mrow>')
            result.append('  </msqrt>')
            
            return result
        
        # 求和符号
        elif cmd_name == 'sum':
            result = ['  <msubsup>']
            result.append('    <mi>∑</mi>')
            
            # 检查是否有下标
            if start < len(formula) and formula[start] == '_':
                if start + 1 < len(formula) and formula[start + 1] == '{':
                    subscript, length = self._parse_braced_content(formula, start + 1)
                    result.append('    <mrow>')
                    result.extend(self._parse_formula(subscript))
                    result.append('    </mrow>')
                else:
                    result.append('    <mrow/>')
            else:
                result.append('    <mrow/>')
            
            # 检查是否有上标
            next_pos = start
            if start < len(formula) and formula[start] == '_':
                # 跳过下标部分
                if start + 1 < len(formula) and formula[start + 1] == '{':
                    _, length = self._parse_braced_content(formula, start + 1)
                    next_pos = start + length
                else:
                    next_pos = start + 2
            
            if next_pos < len(formula) and formula[next_pos] == '^':
                if next_pos + 1 < len(formula) and formula[next_pos + 1] == '{':
                    superscript, length = self._parse_braced_content(formula, next_pos + 1)
                    result.append('    <mrow>')
                    result.extend(self._parse_formula(superscript))
                    result.append('    </mrow>')
                else:
                    result.append('    <mrow/>')
            else:
                result.append('    <mrow/>')
            
            result.append('  </msubsup>')
            return result
        
        # 未知命令
        else:
            # 将命令名拆分为单个字符
            result = []
            for c in cmd_name:
                result.append(f'  <mi>{c}</mi>')
            return result
    
    def _create_basic_mathml(self, latex: str) -> str:
        """创建基本MathML"""
        return f'''<math xmlns="{self.mathml_ns}">
  <mrow>
    <mi>{latex[:100]}</mi>
  </mrow>
</math>'''

def test_final_converter():
    """测试最终版转换器"""
    converter = WordMathMLConverter()
    
    test_cases = [
        'C_{total}',
        'E = mc^{2}',
        'x^2 + y^2 = z^2',
        '\\frac{a}{b}',
        '\\sqrt{x}',
        '\\alpha + \\beta',
        '\\sum_{i=1}^{n} x_i',
        'a_{1} + a_{2}',
    ]
    
    print("最终版Word兼容MathML转换器测试")
    print("=" * 60)
    
    for latex in test_cases:
        print(f"\nLaTeX: {latex}")
        mathml = converter.convert(latex)
        print("MathML:")
        print(mathml)
        print("-" * 40)

if __name__ == '__main__':
    test_final_converter()