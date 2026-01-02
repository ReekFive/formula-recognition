#!/usr/bin/env python3
"""
Word兼容的MathML转换器
完全重新设计，使用递归下降解析
支持完整的LaTeX数学命令集
"""

import re


class WordMathMLConverter:
    def __init__(self):
        # 完整希腊字母表（小写 + 大写）
        self.greek_letters = {
            # 小写
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
            'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
            'nu': 'ν', 'xi': 'ξ', 'pi': 'π', 'rho': 'ρ',
            'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'φ',
            'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
            'varepsilon': 'ε', 'vartheta': 'ϑ', 'varpi': 'ϖ',
            'varrho': 'ϱ', 'varsigma': 'ς', 'varphi': 'ϕ',
            # 大写
            'Alpha': 'Α', 'Beta': 'Β', 'Gamma': 'Γ', 'Delta': 'Δ',
            'Epsilon': 'Ε', 'Zeta': 'Ζ', 'Eta': 'Η', 'Theta': 'Θ',
            'Iota': 'Ι', 'Kappa': 'Κ', 'Lambda': 'Λ', 'Mu': 'Μ',
            'Nu': 'Ν', 'Xi': 'Ξ', 'Pi': 'Π', 'Rho': 'Ρ',
            'Sigma': 'Σ', 'Tau': 'Τ', 'Upsilon': 'Υ', 'Phi': 'Φ',
            'Chi': 'Χ', 'Psi': 'Ψ', 'Omega': 'Ω',
        }
        
        # 完整运算符映射
        self.operator_map = {
            'cdot': '⋅', 'times': '×', 'div': '÷',
            'pm': '±', 'mp': '∓',
            'leq': '≤', 'le': '≤', 'geq': '≥', 'ge': '≥',
            'neq': '≠', 'ne': '≠', 'approx': '≈',
            'equiv': '≡', 'sim': '∼', 'simeq': '≃',
            'll': '≪', 'gg': '≫',
            'subset': '⊂', 'supset': '⊃', 'subseteq': '⊆', 'supseteq': '⊇',
            'in': '∈', 'notin': '∉', 'ni': '∋',
            'cap': '∩', 'cup': '∪', 'setminus': '∖',
            'land': '∧', 'lor': '∨', 'lnot': '¬', 'neg': '¬',
            'forall': '∀', 'exists': '∃', 'nexists': '∄',
            'partial': '∂', 'nabla': '∇',
            'infty': '∞', 'emptyset': '∅', 'varnothing': '∅',
            'to': '→', 'rightarrow': '→', 'leftarrow': '←',
            'Rightarrow': '⇒', 'Leftarrow': '⇐', 'Leftrightarrow': '⇔',
            'mapsto': '↦',
            'ldots': '…', 'cdots': '⋯', 'vdots': '⋮', 'ddots': '⋱',
            'angle': '∠', 'triangle': '△',
            'perp': '⊥', 'parallel': '∥',
            'prime': '′',
        }
        
        # 函数名映射
        self.function_names = {
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
            'sinh', 'cosh', 'tanh', 'coth',
            'arcsin', 'arccos', 'arctan',
            'log', 'ln', 'lg', 'exp',
            'lim', 'limsup', 'liminf',
            'max', 'min', 'sup', 'inf',
            'arg', 'det', 'dim', 'gcd', 'hom', 'ker',
            'deg', 'mod', 'Pr',
        }
        
        # 括号映射
        self.bracket_map = {
            'lbrace': '{', 'rbrace': '}',
            'lbrack': '[', 'rbrack': ']',
            'lparen': '(', 'rparen': ')',
            'langle': '⟨', 'rangle': '⟩',
            'lfloor': '⌊', 'rfloor': '⌋',
            'lceil': '⌈', 'rceil': '⌉',
            'vert': '|', 'Vert': '‖',
        }
        
        # 重音/修饰符映射
        self.accent_map = {
            'hat': '^', 'bar': '¯', 'vec': '→',
            'dot': '˙', 'ddot': '¨', 'tilde': '˜',
            'overline': '¯', 'underline': '_',
            'widehat': '^', 'widetilde': '˜',
        }
    
    def convert(self, formula):
        """转换LaTeX公式为MathML（Word兼容版）"""
        result = ['<math xmlns="http://www.w3.org/1998/Math/MathML">']
        
        # 处理整个公式
        content, _ = self._parse_expression(formula.strip())
        result.extend(content)
        
        result.append('</math>')
        output = '\n'.join(result)
        
        # 将非ASCII Unicode字符转换为XML实体，提高Word兼容性
        output = self._unicode_to_xml_entities(output)
        return output
    
    def _unicode_to_xml_entities(self, text):
        """将非ASCII Unicode字符转换为XML数字实体"""
        result = []
        for char in text:
            if ord(char) > 127:
                # 转换为十六进制XML实体
                result.append(f'&#x{ord(char):04X};')
            else:
                result.append(char)
        return ''.join(result)
    
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
                else:
                    i = new_i
                    continue
            
            # 花括号分组
            elif expr[i] == '{':
                content, new_i = self._parse_braced_content(expr, i)
                if content:
                    group_result, _ = self._parse_expression(content)
                    result.extend(group_result)
                i = new_i
                continue
            
            # 圆括号
            elif expr[i] == '(':
                paren_result, new_i = self._parse_parentheses(expr, i)
                if paren_result:
                    result.extend(paren_result)
                    i = new_i
                    continue
            
            # 方括号
            elif expr[i] == '[':
                bracket_result, new_i = self._parse_brackets(expr, i, '[', ']')
                if bracket_result:
                    result.extend(bracket_result)
                    i = new_i
                    continue
            
            # 字母变量
            elif expr[i].isalpha():
                var_result, new_i = self._parse_variable(expr, i)
                result.extend(var_result)
                i = new_i
                continue
            
            # 数字（包括小数和负数）
            elif expr[i].isdigit() or (expr[i] == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
                num, new_i = self._parse_number(expr, i)
                result.append(f'  <mn>{num}</mn>')
                i = new_i
                continue
            
            # 上标
            elif expr[i] == '^':
                # 独立上标（应该附加到前一个元素，但这里作为错误恢复处理）
                sup_content, new_i = self._parse_script_content(expr, i + 1)
                if sup_content and result:
                    # 将上标附加到前一个元素
                    last_elem = result.pop()
                    sup_lines, _ = self._parse_expression(sup_content)
                    result.append('  <msup>')
                    result.append(f'  {last_elem}')
                    if len(sup_lines) == 1:
                        result.append(f'  {sup_lines[0]}')
                    else:
                        result.append('    <mrow>')
                        result.extend([f'    {line}' for line in sup_lines])
                        result.append('    </mrow>')
                    result.append('  </msup>')
                i = new_i
                continue
            
            # 下标
            elif expr[i] == '_':
                sub_content, new_i = self._parse_script_content(expr, i + 1)
                if sub_content and result:
                    last_elem = result.pop()
                    sub_lines, _ = self._parse_expression(sub_content)
                    result.append('  <msub>')
                    result.append(f'  {last_elem}')
                    if len(sub_lines) == 1:
                        result.append(f'  {sub_lines[0]}')
                    else:
                        result.append('    <mrow>')
                        result.extend([f'    {line}' for line in sub_lines])
                        result.append('    </mrow>')
                    result.append('  </msub>')
                i = new_i
                continue
            
            # 运算符
            elif expr[i] in '+-=':
                result.append(f'  <mo>{expr[i]}</mo>')
                i += 1
                continue
            
            # 其他常见运算符
            elif expr[i] == '*':
                result.append('  <mo>×</mo>')
                i += 1
                continue
            
            elif expr[i] == '/':
                result.append('  <mo>/</mo>')
                i += 1
                continue
            
            elif expr[i] == '<':
                result.append('  <mo>&lt;</mo>')
                i += 1
                continue
            
            elif expr[i] == '>':
                result.append('  <mo>&gt;</mo>')
                i += 1
                continue
            
            elif expr[i] == '|':
                result.append('  <mo>|</mo>')
                i += 1
                continue
            
            elif expr[i] == ',':
                result.append('  <mo>,</mo>')
                i += 1
                continue
            
            elif expr[i] == ';':
                result.append('  <mo>;</mo>')
                i += 1
                continue
            
            elif expr[i] == ':':
                result.append('  <mo>:</mo>')
                i += 1
                continue
            
            elif expr[i] == '!':
                result.append('  <mo>!</mo>')
                i += 1
                continue
            
            elif expr[i] == "'":
                result.append('  <mo>′</mo>')
                i += 1
                continue
            
            # 跳过其他字符（如右括号等已处理的）
            else:
                i += 1
        
        return result, i
    
    def _parse_variable(self, expr, start):
        """解析变量，处理上下标"""
        i = start
        var = expr[i]
        i += 1
        
        # 不再贪婪匹配多字母（单字母变量更常见）
        # 检查是否有上下标
        has_sub = False
        has_sup = False
        subscript = ''
        superscript = ''
        
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查下标
        if i < len(expr) and expr[i] == '_':
            has_sub = True
            subscript, i = self._parse_script_content(expr, i + 1)
            # 跳过空格
            while i < len(expr) and expr[i].isspace():
                i += 1
        
        # 检查上标
        if i < len(expr) and expr[i] == '^':
            has_sup = True
            superscript, i = self._parse_script_content(expr, i + 1)
        
        # 生成MathML
        if has_sub and has_sup:
            # 同时有上下标
            sub_lines, _ = self._parse_expression(subscript)
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msubsup>', f'    <mi>{var}</mi>']
            if len(sub_lines) == 1:
                result.append(f'  {sub_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sub_lines])
                result.append('    </mrow>')
            if len(sup_lines) == 1:
                result.append(f'  {sup_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msubsup>')
            return result, i
        elif has_sub:
            sub_lines, _ = self._parse_expression(subscript)
            result = ['  <msub>', f'    <mi>{var}</mi>']
            if len(sub_lines) == 1:
                result.append(f'  {sub_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sub_lines])
                result.append('    </mrow>')
            result.append('  </msub>')
            return result, i
        elif has_sup:
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msup>', f'    <mi>{var}</mi>']
            if len(sup_lines) == 1:
                result.append(f'  {sup_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msup>')
            return result, i
        else:
            return [f'  <mi>{var}</mi>'], i
    
    def _parse_number(self, expr, start):
        """解析数字（包括小数）"""
        i = start
        num = ''
        has_dot = False
        
        while i < len(expr):
            if expr[i].isdigit():
                num += expr[i]
                i += 1
            elif expr[i] == '.' and not has_dot:
                has_dot = True
                num += expr[i]
                i += 1
            else:
                break
        
        return num, i
    
    def _parse_script_content(self, expr, start):
        """解析上标或下标内容"""
        i = start
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        if i >= len(expr):
            return '', i
        
        if expr[i] == '{':
            content, new_i = self._parse_braced_content(expr, i)
            return content, new_i
        else:
            # 单字符
            return expr[i], i + 1
    
    def _parse_command(self, expr, start):
        """解析LaTeX命令，返回(MathML行列表, 新位置)"""
        i = start + 1
        cmd = ''
        
        # 读取命令名
        while i < len(expr) and (expr[i].isalpha() or expr[i].isdigit()):
            cmd += expr[i]
            i += 1
        
        # 特殊处理：反斜杠后直接跟特殊字符
        if not cmd and i < len(expr):
            special_char = expr[i]
            i += 1
            if special_char in '{}':
                return [f'  <mo>{special_char}</mo>'], i
            elif special_char == ' ':
                return ['  <mspace width="0.3em"/>'], i
            elif special_char == ',':
                return ['  <mspace width="0.2em"/>'], i
            elif special_char == ';':
                return ['  <mspace width="0.3em"/>'], i
            elif special_char == '!':
                return ['  <mspace width="-0.1em"/>'], i
            elif special_char == '\\':
                return ['  <mspace linebreak="newline"/>'], i
            else:
                return [f'  <mo>{special_char}</mo>'], i
        
        # 分数
        if cmd == 'frac':
            return self._parse_fraction(expr, i)
        
        # 根号
        elif cmd == 'sqrt':
            return self._parse_sqrt(expr, i)
        
        # 求和、积分等大运算符
        elif cmd in ('sum', 'prod', 'coprod'):
            return self._parse_big_operator(expr, i, cmd)
        
        elif cmd in ('int', 'iint', 'iiint', 'oint'):
            return self._parse_integral(expr, i, cmd)
        
        elif cmd == 'lim':
            return self._parse_limit(expr, i)
        
        # left/right命令 - 跳过命令和后面的分隔符
        elif cmd == 'left' or cmd == 'right':
            # 跳过空格
            while i < len(expr) and expr[i].isspace():
                i += 1
            # 跳过分隔符字符
            if i < len(expr):
                if expr[i] == '\\':
                    # 处理 \left\{ 等情况
                    j = i + 1
                    bracket_cmd = ''
                    while j < len(expr) and expr[j].isalpha():
                        bracket_cmd += expr[j]
                        j += 1
                    if bracket_cmd in self.bracket_map:
                        i = j
                elif expr[i] in '()[]{}|.':
                    i += 1
            return [], i
        
        # 希腊字母
        elif cmd in self.greek_letters:
            return self._parse_greek_with_scripts(expr, i, self.greek_letters[cmd])
        
        # 运算符
        elif cmd in self.operator_map:
            return [f'  <mo>{self.operator_map[cmd]}</mo>'], i
        
        # 函数名
        elif cmd in self.function_names:
            return self._parse_function(expr, i, cmd)
        
        # 括号
        elif cmd in self.bracket_map:
            return [f'  <mo>{self.bracket_map[cmd]}</mo>'], i
        
        # 重音/修饰符
        elif cmd in self.accent_map:
            return self._parse_accent(expr, i, cmd)
        
        # text命令
        elif cmd == 'text':
            return self._parse_text(expr, i)
        
        elif cmd in ('mathrm', 'mathbf', 'mathit', 'mathsf', 'mathtt', 'mathbb', 'mathcal', 'mathfrak'):
            return self._parse_math_font(expr, i, cmd)
        
        # 其他命令当作普通文本
        else:
            return [f'  <mi>{cmd}</mi>'], i
    
    def _parse_greek_with_scripts(self, expr, start, symbol):
        """解析带上下标的希腊字母"""
        i = start
        has_sub = False
        has_sup = False
        subscript = ''
        superscript = ''
        
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查下标
        if i < len(expr) and expr[i] == '_':
            has_sub = True
            subscript, i = self._parse_script_content(expr, i + 1)
            while i < len(expr) and expr[i].isspace():
                i += 1
        
        # 检查上标
        if i < len(expr) and expr[i] == '^':
            has_sup = True
            superscript, i = self._parse_script_content(expr, i + 1)
        
        if has_sub and has_sup:
            sub_lines, _ = self._parse_expression(subscript)
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msubsup>', f'    <mi>{symbol}</mi>']
            if len(sub_lines) == 1:
                result.append(f'  {sub_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sub_lines])
                result.append('    </mrow>')
            if len(sup_lines) == 1:
                result.append(f'  {sup_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msubsup>')
            return result, i
        elif has_sub:
            sub_lines, _ = self._parse_expression(subscript)
            result = ['  <msub>', f'    <mi>{symbol}</mi>']
            if len(sub_lines) == 1:
                result.append(f'  {sub_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sub_lines])
                result.append('    </mrow>')
            result.append('  </msub>')
            return result, i
        elif has_sup:
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msup>', f'    <mi>{symbol}</mi>']
            if len(sup_lines) == 1:
                result.append(f'  {sup_lines[0]}')
            else:
                result.append('    <mrow>')
                result.extend([f'    {line}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msup>')
            return result, i
        else:
            return [f'  <mi>{symbol}</mi>'], i
    
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
                result.append(f'      {line.strip()}')
            result.append('    </mrow>')
        else:
            for line in num_lines:
                result.append(f'    {line.strip()}')

        # 分母 - 只在不是单个元素时用<mrow>包装
        if not self._is_single_element(den_lines):
            result.append('    <mrow>')
            for line in den_lines:
                result.append(f'      {line.strip()}')
            result.append('    </mrow>')
        else:
            for line in den_lines:
                result.append(f'    {line.strip()}')

        result.append('  </mfrac>')
        
        return result, i
    
    def _parse_sqrt(self, expr, start):
        """解析根号 \sqrt 或 \sqrt[n]"""
        i = start
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查是否有指数 [n]
        index = None
        if i < len(expr) and expr[i] == '[':
            # 找到匹配的 ]
            j = i + 1
            depth = 1
            while j < len(expr) and depth > 0:
                if expr[j] == '[':
                    depth += 1
                elif expr[j] == ']':
                    depth -= 1
                j += 1
            index = expr[i + 1:j - 1]
            i = j
            # 跳过空格
            while i < len(expr) and expr[i].isspace():
                i += 1
        
        # 解析根号内容
        if i < len(expr) and expr[i] == '{':
            content, i = self._parse_braced_content(expr, i)
        elif i < len(expr):
            # 单字符
            content = expr[i]
            i += 1
        else:
            return [], start
        
        content_lines, _ = self._parse_expression(content)
        
        if index:
            # n次根号
            index_lines, _ = self._parse_expression(index)
            result = ['  <mroot>']
            if self._is_single_element(content_lines):
                result.extend([f'    {line.strip()}' for line in content_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in content_lines])
                result.append('    </mrow>')
            if self._is_single_element(index_lines):
                result.extend([f'    {line.strip()}' for line in index_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in index_lines])
                result.append('    </mrow>')
            result.append('  </mroot>')
        else:
            # 平方根
            result = ['  <msqrt>']
            if self._is_single_element(content_lines):
                result.extend([f'    {line.strip()}' for line in content_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in content_lines])
                result.append('    </mrow>')
            result.append('  </msqrt>')
        
        return result, i
    
    def _parse_big_operator(self, expr, start, cmd):
        """解析大运算符（sum, prod等）- 使用 msubsup 格式以提高 Word 兼容性"""
        op_map = {
            'sum': '∑', 'prod': '∏', 'coprod': '∐',
        }
        symbol = op_map.get(cmd, cmd)
        
        i = start
        has_sub = False
        has_sup = False
        subscript = ''
        superscript = ''
        
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查下标
        if i < len(expr) and expr[i] == '_':
            has_sub = True
            subscript, i = self._parse_script_content(expr, i + 1)
            while i < len(expr) and expr[i].isspace():
                i += 1
        
        # 检查上标
        if i < len(expr) and expr[i] == '^':
            has_sup = True
            superscript, i = self._parse_script_content(expr, i + 1)
        
        # 使用 msubsup 替代 munderover 以提高 Word 兼容性
        if has_sub and has_sup:
            sub_lines, _ = self._parse_expression(subscript)
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msubsup>', f'    <mo>&#x{ord(symbol):04X};</mo>']
            if self._is_single_element(sub_lines):
                result.extend([f'    {line.strip()}' for line in sub_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sub_lines])
                result.append('    </mrow>')
            if self._is_single_element(sup_lines):
                result.extend([f'    {line.strip()}' for line in sup_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msubsup>')
            return result, i
        elif has_sub:
            sub_lines, _ = self._parse_expression(subscript)
            result = ['  <msub>', f'    <mo>&#x{ord(symbol):04X};</mo>']
            if self._is_single_element(sub_lines):
                result.extend([f'    {line.strip()}' for line in sub_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sub_lines])
                result.append('    </mrow>')
            result.append('  </msub>')
            return result, i
        elif has_sup:
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msup>', f'    <mo>&#x{ord(symbol):04X};</mo>']
            if self._is_single_element(sup_lines):
                result.extend([f'    {line.strip()}' for line in sup_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msup>')
            return result, i
        else:
            return [f'  <mo>&#x{ord(symbol):04X};</mo>'], i
    
    def _parse_integral(self, expr, start, cmd):
        """解析积分符号 - 使用 XML 实体编码以提高 Word 兼容性"""
        int_map = {
            'int': 0x222B, 'iint': 0x222C, 'iiint': 0x222D, 'oint': 0x222E,
        }
        symbol_code = int_map.get(cmd, 0x222B)
        
        i = start
        has_sub = False
        has_sup = False
        subscript = ''
        superscript = ''
        
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查下标
        if i < len(expr) and expr[i] == '_':
            has_sub = True
            subscript, i = self._parse_script_content(expr, i + 1)
            while i < len(expr) and expr[i].isspace():
                i += 1
        
        # 检查上标
        if i < len(expr) and expr[i] == '^':
            has_sup = True
            superscript, i = self._parse_script_content(expr, i + 1)
        
        if has_sub and has_sup:
            sub_lines, _ = self._parse_expression(subscript)
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msubsup>', f'    <mo>&#x{symbol_code:04X};</mo>']
            if self._is_single_element(sub_lines):
                result.extend([f'    {line.strip()}' for line in sub_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sub_lines])
                result.append('    </mrow>')
            if self._is_single_element(sup_lines):
                result.extend([f'    {line.strip()}' for line in sup_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msubsup>')
            return result, i
        elif has_sub:
            sub_lines, _ = self._parse_expression(subscript)
            result = ['  <msub>', f'    <mo>&#x{symbol_code:04X};</mo>']
            if self._is_single_element(sub_lines):
                result.extend([f'    {line.strip()}' for line in sub_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sub_lines])
                result.append('    </mrow>')
            result.append('  </msub>')
            return result, i
        elif has_sup:
            sup_lines, _ = self._parse_expression(superscript)
            result = ['  <msup>', f'    <mo>&#x{symbol_code:04X};</mo>']
            if self._is_single_element(sup_lines):
                result.extend([f'    {line.strip()}' for line in sup_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sup_lines])
                result.append('    </mrow>')
            result.append('  </msup>')
            return result, i
        else:
            return [f'  <mo>&#x{symbol_code:04X};</mo>'], i
    
    def _parse_limit(self, expr, start):
        """解析极限"""
        i = start
        has_sub = False
        subscript = ''
        
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 检查下标
        if i < len(expr) and expr[i] == '_':
            has_sub = True
            subscript, i = self._parse_script_content(expr, i + 1)
        
        if has_sub:
            sub_lines, _ = self._parse_expression(subscript)
            result = ['  <munder>', '    <mo>lim</mo>']
            if self._is_single_element(sub_lines):
                result.extend([f'    {line.strip()}' for line in sub_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in sub_lines])
                result.append('    </mrow>')
            result.append('  </munder>')
            return result, i
        else:
            return ['  <mo>lim</mo>'], i
    
    def _parse_function(self, expr, start, func_name):
        """解析函数名"""
        i = start
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 函数名使用 <mi> 标签，mathvariant="normal"
        return [f'  <mi mathvariant="normal">{func_name}</mi>'], i
    
    def _parse_accent(self, expr, start, accent_name):
        """解析重音符号"""
        i = start
        # 跳过空格
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        # 解析被修饰的内容
        if i < len(expr) and expr[i] == '{':
            content, i = self._parse_braced_content(expr, i)
        elif i < len(expr):
            content = expr[i]
            i += 1
        else:
            return [], start
        
        content_lines, _ = self._parse_expression(content)
        accent_char = self.accent_map.get(accent_name, '^')
        
        result = ['  <mover>']
        if self._is_single_element(content_lines):
            result.extend([f'    {line.strip()}' for line in content_lines])
        else:
            result.append('    <mrow>')
            result.extend([f'      {line.strip()}' for line in content_lines])
            result.append('    </mrow>')
        result.append(f'    <mo>{accent_char}</mo>')
        result.append('  </mover>')
        
        return result, i
    
    def _parse_text(self, expr, start):
        """解析 \text{...}"""
        i = start
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        if i < len(expr) and expr[i] == '{':
            content, i = self._parse_braced_content(expr, i)
            return [f'  <mtext>{content}</mtext>'], i
        else:
            return [], start
    
    def _parse_math_font(self, expr, start, font_cmd):
        """解析数学字体命令"""
        font_map = {
            'mathrm': 'normal',
            'mathbf': 'bold',
            'mathit': 'italic',
            'mathsf': 'sans-serif',
            'mathtt': 'monospace',
            'mathbb': 'double-struck',
            'mathcal': 'script',
            'mathfrak': 'fraktur',
        }
        variant = font_map.get(font_cmd, 'normal')
        
        i = start
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        if i < len(expr) and expr[i] == '{':
            content, i = self._parse_braced_content(expr, i)
            return [f'  <mi mathvariant="{variant}">{content}</mi>'], i
        else:
            return [], start
    
    def _parse_parentheses(self, expr, start):
        """解析圆括号及其内容"""
        if start >= len(expr) or expr[start] != '(':
            return [], start
        
        # 找到匹配的右括号
        content, end_pos = self._find_matching_paren(expr, start, '(', ')')
        if content is None:
            return ['  <mo>(</mo>'], start + 1
        
        # 检查是否有上标
        i = end_pos
        has_superscript = False
        superscript = ''
        
        while i < len(expr) and expr[i].isspace():
            i += 1
        
        if i < len(expr) and expr[i] == '^':
            has_superscript = True
            superscript, i = self._parse_script_content(expr, i + 1)
        
        # 解析括号内容
        content_lines, _ = self._parse_expression(content)
        
        if has_superscript and superscript:
            # 有上标的括号 - 使用 mrow + mo 替代 mfenced
            superscript_lines, _ = self._parse_expression(superscript)

            result = [
                '  <msup>',
                '    <mrow>',
                '      <mo>(</mo>'
            ]
            result.extend([f'      {line.strip()}' for line in content_lines])
            result.append('      <mo>)</mo>')
            result.append('    </mrow>')

            # 添加实际的上标内容
            if self._is_single_element(superscript_lines):
                result.extend([f'    {line.strip()}' for line in superscript_lines])
            else:
                result.append('    <mrow>')
                result.extend([f'      {line.strip()}' for line in superscript_lines])
                result.append('    </mrow>')
            result.append('  </msup>')
        else:
            # 普通括号 - 使用 mrow + mo 替代 mfenced
            result = [
                '  <mrow>',
                '    <mo>(</mo>'
            ]
            result.extend([f'    {line.strip()}' for line in content_lines])
            result.extend([
                '    <mo>)</mo>',
                '  </mrow>'
            ])
        
        return result, i
    
    def _parse_brackets(self, expr, start, open_char, close_char):
        """解析方括号等 - 使用 mrow + mo 替代 mfenced"""
        if start >= len(expr) or expr[start] != open_char:
            return [], start
        
        content, end_pos = self._find_matching_paren(expr, start, open_char, close_char)
        if content is None:
            return [f'  <mo>{open_char}</mo>'], start + 1
        
        content_lines, _ = self._parse_expression(content)
        
        result = [
            '  <mrow>',
            f'    <mo>{open_char}</mo>'
        ]
        result.extend([f'    {line.strip()}' for line in content_lines])
        result.extend([
            f'    <mo>{close_char}</mo>',
            '  </mrow>'
        ])
        
        return result, end_pos
    
    def _find_matching_paren(self, expr, start, open_char, close_char):
        """找到匹配的括号，返回(内容, 新位置)"""
        if start >= len(expr) or expr[start] != open_char:
            return None, start
        
        depth = 0
        content = ''
        i = start + 1
        
        while i < len(expr):
            if expr[i] == open_char:
                depth += 1
                content += expr[i]
            elif expr[i] == close_char:
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
    
    # 测试用例
    test_formulas = [
        r"x^2 + y^2 = z^2",
        r"\sqrt{x^2 + y^2}",
        r"\sqrt[3]{8}",
        r"\frac{a+b}{c}",
        r"\sum_{i=1}^{n} x_i",
        r"\int_{0}^{\infty} e^{-x} dx",
        r"\lim_{x \to 0} \frac{\sin x}{x}",
        r"\alpha + \beta = \gamma",
        r"a \times b \div c",
        r"x \leq y \geq z",
        r"\sin x + \cos y",
        r"S=\frac{4 ( l+R )^{2}} {( \frac{\sigma_{f}} {\sigma_{r}}+\frac{\sigma_{r}} {\sigma_{f}} )^{2} ( 1+R_{0} )^{2}}",
    ]
    
    print("测试增强版转换器：")
    print("=" * 60)
    
    for formula in test_formulas:
        print(f"\n公式: {formula}")
        print("-" * 40)
        result = converter.convert(formula)
        print(result[:500] + "..." if len(result) > 500 else result)
