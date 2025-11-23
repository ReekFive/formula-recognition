#!/usr/bin/env python3
"""
Word兼容的MathML转换器
完全重新设计，使用递归下降解析
"""

class WordMathMLConverter:
    def __init__(self):
        self.greek_letters = {
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
            'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
            'nu': 'ν', 'xi': 'ξ', 'pi': 'π', 'rho': 'ρ',
            'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'φ',
            'chi': 'χ', 'psi': 'ψ', 'omega': 'ω'
        }
    
    def convert(self, formula):
        """转换LaTeX公式为MathML"""
        result = ['<math xmlns="http://www.w3.org/1998/Math/MathML">']
        
        # 处理整个公式
        content, _ = self._parse_expression(formula.strip())
        result.extend(content)
        
        result.append('</math>')
        return '\n'.join(result)
    
    def _parse_expression(self, expr):
        """解析表达式，返回(MathML行列表, 新位置)"""
        result = []
        i = 0
        
        while i < len(expr):
            # 跳过空格
            if expr[i].isspace():
                i += 1
                continue
            
            # LaTeX命令
            if expr[i] == '\\':
                cmd_result, new_i = self._parse_command(expr, i)
                if cmd_result:
                    result.extend(cmd_result)
                    i = new_i
                    continue
            
            # 圆括号
            elif expr[i] == '(':
                paren_result, new_i = self._parse_parentheses(expr, i)
                if paren_result:
                    result.extend(paren_result)
                    i = new_i
                    continue
            
            # 字母变量
            elif expr[i].isalpha():
                var = expr[i]
                i += 1
                while i < len(expr) and expr[i].isalpha():
                    var += expr[i]
                    i += 1
                
                # 检查是否有下标
                if i < len(expr) and expr[i] == '_':
                    subscript, new_i = self._parse_subscript(expr, i + 1)
                    if subscript:
                        sub_tag = self._get_subscript_tag(subscript)
                        result.extend([
                            '  <msub>',
                            f'    <mi>{var}</mi>',
                            f'    <{sub_tag}>{subscript}</{sub_tag}>',
                            '  </msub>'
                        ])
                        i = new_i
                        continue
                
                result.append(f'  <mi>{var}</mi>')
                continue
            
            # 数字
            elif expr[i].isdigit():
                num = expr[i]
                i += 1
                while i < len(expr) and expr[i].isdigit():
                    num += expr[i]
                    i += 1
                result.append(f'  <mn>{num}</mn>')
                continue
            
            # 运算符
            elif expr[i] in '+-=':
                result.append(f'  <mo>{expr[i]}</mo>')
                i += 1
                continue
            
            # 跳过其他字符
            else:
                i += 1
        
        return result, i
    
    def _parse_command(self, expr, start):
        """解析LaTeX命令，返回(MathML行列表, 新位置)"""
        i = start + 1
        cmd = ''
        
        # 读取命令名
        while i < len(expr) and expr[i].isalpha():
            cmd += expr[i]
            i += 1
        
        # 分数
        if cmd == 'frac':
            return self._parse_fraction(expr, i)
        
        # left/right命令 - 跳过命令和后面的分隔符
        elif cmd == 'left' or cmd == 'right':
            # 跳过空格
            while i < len(expr) and expr[i].isspace():
                i += 1
            # 跳过分隔符字符 (如 (, ), |, [, ], {, } 等)
            if i < len(expr) and expr[i] in '()[]{}|':
                i += 1
            return [], i
        
        # 希腊字母
        elif cmd in self.greek_letters:
            # 检查是否有下标
            if i < len(expr) and expr[i] == '_':
                subscript, new_i = self._parse_subscript(expr, i + 1)
                if subscript:
                    sub_tag = self._get_subscript_tag(subscript)
                    return [
                        '  <msub>',
                        f'    <mi>{self.greek_letters[cmd]}</mi>',
                        f'    <{sub_tag}>{subscript}</{sub_tag}>',
                        '  </msub>'
                    ], new_i

            return [f'  <mi>{self.greek_letters[cmd]}</mi>'], i
        
        # 其他命令
        else:
            return [f'  <mi>{cmd}</mi>'], i
    
    def _parse_fraction(self, expr, start):
        """解析分数，返回(MathML行列表, 新位置)"""
        # 跳过前导空格
        i = start
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 解析分子
        if i < len(expr) and expr[i] == '{':
            numerator, i = self._parse_braced_content(expr, i)
        else:
            return [], start
        
        # 跳过中间的空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 解析分母
        if i < len(expr) and expr[i] == '{':
            denominator, i = self._parse_braced_content(expr, i)
        else:
            return [], start
        
        # 生成分子MathML
        num_lines, _ = self._parse_expression(numerator)
        
        # 生成分母MathML
        den_lines, _ = self._parse_expression(denominator)
        
        result = ['  <mfrac>']

        # 分子 - 只在不是单个元素时用<mrow>包装
        if not self._is_single_element(num_lines):
            result.append('    <mrow>')
            for line in num_lines:
                result.append(f'      {line[2:]}')  # 移除前导空格并增加缩进
            result.append('    </mrow>')
        else:
            for line in num_lines:
                result.append(f'    {line[2:]}')  # 移除前导空格

        # 分母 - 只在不是单个元素时用<mrow>包装
        if not self._is_single_element(den_lines):
            result.append('    <mrow>')
            for line in den_lines:
                result.append(f'      {line[2:]}')  # 移除前导空格并增加缩进
            result.append('    </mrow>')
        else:
            for line in den_lines:
                result.append(f'    {line[2:]}')  # 移除前导空格

        result.append('  </mfrac>')
        
        return result, i
    
    def _parse_parentheses(self, expr, start):
        """解析圆括号及其内容"""
        if start >= len(expr) or expr[start] != '(':
            return [], start
        
        # 找到匹配的右括号
        content, end_pos = self._find_matching_parenthesis(expr, start)
        if content is None:
            return ['  <mo>(</mo>'], start + 1
        
        # 检查是否有上标
        i = end_pos
        has_superscript = False
        superscript = ''
        
        if i < len(expr) and expr[i] == '^':
            has_superscript = True
            superscript, i = self._parse_braced_content(expr, i + 1)
        
        # 解析括号内容
        content_lines, _ = self._parse_expression(content)
        
        if has_superscript and superscript:
            # 有上标的括号
            superscript_lines, _ = self._parse_expression(superscript)

            result = [
                '  <msup>',
                '    <mfenced open="(" close=")" separators="|">',
                '      <mrow>'
            ]
            result.extend([f'        {line[2:]}' for line in content_lines])
            result.append('      </mrow>')
            result.append('    </mfenced>')

            # 添加实际的上标内容
            for line in superscript_lines:
                result.append(f'    {line[2:]}')

            result.append('  </msup>')
        else:
            # 普通括号
            result = [
                '  <mfenced open="(" close=")" separators="|">',
                '    <mrow>'
            ]
            result.extend([f'      {line[2:]}' for line in content_lines])
            result.extend([
                '    </mrow>',
                '  </mfenced>'
            ])
        
        return result, i
    
    def _find_matching_parenthesis(self, expr, start):
        """找到匹配的圆括号，返回(内容, 新位置)"""
        if start >= len(expr) or expr[start] != '(':
            return None, start
        
        depth = 0
        content = ''
        i = start + 1
        
        while i < len(expr):
            if expr[i] == '(':
                depth += 1
                content += expr[i]
            elif expr[i] == ')':
                if depth == 0:
                    return content, i + 1
                depth -= 1
                content += expr[i]
            elif expr[i] == '{':
                # 跳过花括号内容，避免干扰圆括号匹配
                brace_content, new_i = self._parse_braced_content(expr, i)
                content += '{' + brace_content + '}'
                i = new_i - 1  # -1 因为循环会+1
            else:
                content += expr[i]
            i += 1
        
        return None, start
    
    def _parse_braced_content(self, expr, start):
        """解析花括号内容，返回(内容, 新位置)"""
        # 跳过前导空格
        while start < len(expr) and expr[start].isspace():
            start += 1
        
        if start >= len(expr) or expr[start] != '{':
            return '', start
        
        brace_count = 1
        content = ''
        i = start + 1
        
        while i < len(expr) and brace_count > 0:
            if expr[i] == '{':
                brace_count += 1
                content += expr[i]
            elif expr[i] == '}':
                brace_count -= 1
                if brace_count > 0:
                    content += expr[i]
            else:
                content += expr[i]
            i += 1
        
        if brace_count == 0:
            return content.strip(), i
        else:
            return content.strip(), i
    
    def _parse_subscript(self, expr, start):
        """解析下标，返回(内容, 新位置)"""
        if start < len(expr) and expr[start] == '{':
            content, new_i = self._parse_braced_content(expr, start)
            return content, new_i
        elif start < len(expr):
            return expr[start], start + 1
        else:
            return '', start

    def _get_subscript_tag(self, content):
        """根据内容决定使用<mi>还是<mn>标签"""
        if content.isdigit():
            return 'mn'
        else:
            return 'mi'

    def _is_single_element(self, lines):
        """检查MathML行列表是否表示单个元素"""
        if not lines:
            return False
        if len(lines) == 1:
            # 单行，必定是单个元素
            return True

        # 多行时，通过标签深度追踪来确定是否只有一个顶层元素
        depth = 0
        first_tag_closed = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # 处理自闭合标签或注释
            if stripped.startswith('<!--') or '/>' in stripped:
                if depth == 0 and first_tag_closed:
                    return False  # 第一个元素后还有元素
                continue

            # 处理同一行包含完整标签的情况 (如 <mi>x</mi>)
            if '<' in stripped and '>' in stripped and '</' in stripped:
                # 提取开始标签名
                start_idx = stripped.find('<')
                end_idx = stripped.find('>', start_idx)
                if end_idx > start_idx:
                    tag_part = stripped[start_idx+1:end_idx]
                    tag_name = tag_part.split()[0] if tag_part else ''

                    # 检查是否有对应的结束标签在同一行
                    close_tag = f'</{tag_name}>'
                    if close_tag in stripped:
                        # 这是一个自包含的标签，depth不变
                        if depth == 0:
                            if first_tag_closed:
                                return False  # 多个顶层元素
                            first_tag_closed = True
                        continue

            # 结束标签
            if stripped.startswith('</'):
                depth -= 1
                if depth == 0:
                    first_tag_closed = True
                elif depth < 0:
                    # 深度为负，说明结构有问题
                    return False
            # 开始标签
            elif stripped.startswith('<'):
                if first_tag_closed:
                    # 第一个顶层元素已经关闭，但又遇到新的开始标签
                    # 说明有多个顶层元素
                    return False
                depth += 1

        # 只有一个顶层元素当且仅当第一个标签被正确关闭，且没有其他顶层元素
        return first_tag_closed and depth == 0

# 测试
if __name__ == "__main__":
    converter = WordMathMLConverter()
    
    # 测试复杂公式
    test_formula = r"S=\frac{4 ( l+R )^{2}} {( \frac{\sigma_{f}} {\sigma_{r}}+\frac{\sigma_{r}} {\sigma_{f}} )^{2} ( 1+R_{0} )^{2}}"
    
    print("测试修复后的转换器：")
    print("=" * 60)
    print(f"公式: {test_formula}")
    print("\n生成的MathML:")
    result = converter.convert(test_formula)
    print(result)