import re
import os


class Preprocesser:
    """预处理器 —— 处理 #include / #define / #ifdef / 注释 / 空格"""

    def __init__(self):
        # 标准库搜索路径（相对于项目根目录）
        self._lib_dirs = []
        self._included_files = set()  # 防止重复 include

    def set_lib_dirs(self, dirs):
        """设置标准库搜索路径列表"""
        self._lib_dirs = list(dirs)

    # ─────────────────────────────────────────────
    #  注释处理
    # ─────────────────────────────────────────────
    def process_note(self, text):
        # 先处理多行注释 /* ... */
        while '/*' in text:
            start = text.find('/*')
            end = text.find('*/', start + 2)
            if end == -1:
                text = text[:start]  # 未闭合则删到末尾
            else:
                text = text[:start] + text[end + 2:]
        # 再处理单行注释 //
        content = ""
        file = text.split("\n")
        for line in file:
            pos = line.find("//")
            if pos != -1:
                content += line[0:pos] + "\n"
            else:
                content += line + "\n"
        return content

    # ─────────────────────────────────────────────
    #  #include 处理（支持 <lib> 和 "path" 两种形式）
    # ─────────────────────────────────────────────
    def _resolve_include_path(self, raw_path):
        """解析 include 路径，支持 <lib> 和 "path" 格式"""
        raw_path = raw_path.strip()

        if raw_path.startswith('<') and raw_path.endswith('>'):
            # 标准库路径 <stdio.y> → 在 lib_dirs 中搜索
            lib_name = raw_path[1:-1]
            for lib_dir in self._lib_dirs:
                full_path = os.path.join(lib_dir, lib_name)
                if os.path.exists(full_path):
                    return full_path
            # 兼容旧格式：<lib/lib.txt> 直接作为相对路径
            if os.path.exists(lib_name):
                return lib_name
            return None
        elif raw_path.startswith('"') and raw_path.endswith('"'):
            # 用户路径 "path/to/file.y"
            path = raw_path[1:-1]
            if os.path.exists(path):
                return path
            return None
        else:
            # 兼容旧格式：#include<lib/lib.txt> 没有空格
            if os.path.exists(raw_path):
                return raw_path
            return None

    def process_include(self, text):
        lines = text.split("\n")
        code = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#include"):
                raw_path = stripped[len("#include"):]
                file_path = self._resolve_include_path(raw_path)

                if file_path is None:
                    print(f"错误：文件未找到。请检查文件路径是否正确: {raw_path}")
                    continue

                # 防止重复包含
                abs_path = os.path.abspath(file_path)
                if abs_path in self._included_files:
                    continue
                self._included_files.add(abs_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except (FileNotFoundError, IOError) as e:
                    print(f"错误：无法读取文件: {file_path} ({e})")
                    continue
                code += self.process_include(content)
            else:
                code += line + "\n"
        return code

    # ─────────────────────────────────────────────
    #  #define 处理（支持函数式宏、多行宏、#undef）
    # ─────────────────────────────────────────────
    def process_define(self, text):
        simple_macros = {}  # name → replacement_text
        func_macros = {}    # name → (param_list, body_template)
        lines = text.split("\n")
        code = ""
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # ── #define ──
            if stripped.startswith("#define"):
                define_body = stripped[len("#define"):].strip()

                # 处理多行宏（\ 续行）
                while define_body.endswith("\\") and i + 1 < len(lines):
                    define_body = define_body[:-1].strip()  # 去掉 \
                    i += 1
                    define_body += " " + lines[i].strip()

                # 判断是函数式宏还是简单宏
                # 函数式宏: NAME(a,b) body
                func_match = re.match(r'^(\w+)\(([^)]*)\)\s+(.*)', define_body)
                if func_match:
                    macro_name = func_match.group(1)
                    params = [p.strip() for p in func_match.group(2).split(",") if p.strip()]
                    body = func_match.group(3)
                    func_macros[macro_name] = (params, body)
                else:
                    # 简单宏: NAME value
                    parts = define_body.split(None, 1)
                    if len(parts) >= 2:
                        simple_macros[parts[0]] = parts[1]
                    elif len(parts) == 1:
                        # #define FLAG （无值，用于 #ifdef 检查）
                        simple_macros[parts[0]] = ""

            # ── #undef / #undefine ──
            elif stripped.startswith("#undef") or stripped.startswith("#undefine"):
                if stripped.startswith("#undefine"):
                    name = stripped[len("#undefine"):].strip()
                else:
                    name = stripped[len("#undef"):].strip()
                simple_macros.pop(name, None)
                func_macros.pop(name, None)

            # ── 普通代码行：执行宏替换 ──
            else:
                line = self._expand_macros(line, simple_macros, func_macros)
                code += line + "\n"

            i += 1
        return code

    def _expand_macros(self, line, simple_macros, func_macros):
        """在一行代码中展开所有宏（函数式宏优先，然后简单宏）"""
        # 展开函数式宏
        for name, (params, body) in func_macros.items():
            pattern = re.compile(r'\b' + re.escape(name) + r'\(')
            while True:
                m = pattern.search(line)
                if not m:
                    break
                start = m.start()
                # 找到匹配的右括号
                paren_depth = 1
                pos = m.end()
                args_start = pos
                args = []
                current_arg_start = pos
                while pos < len(line) and paren_depth > 0:
                    if line[pos] == '(':
                        paren_depth += 1
                    elif line[pos] == ')':
                        paren_depth -= 1
                        if paren_depth == 0:
                            args.append(line[current_arg_start:pos].strip())
                            break
                    elif line[pos] == ',' and paren_depth == 1:
                        args.append(line[current_arg_start:pos].strip())
                        current_arg_start = pos + 1
                    pos += 1

                if paren_depth != 0:
                    break  # 括号不匹配，跳过

                end = pos + 1  # 右括号之后
                # 参数替换
                expanded = body
                for j, param in enumerate(params):
                    if j < len(args):
                        expanded = re.sub(r'\b' + re.escape(param) + r'\b', args[j], expanded)
                line = line[:start] + expanded + line[end:]

        # 展开简单宏（按长度从长到短，避免短宏误替换长宏的前缀）
        for name in sorted(simple_macros.keys(), key=len, reverse=True):
            value = simple_macros[name]
            if value:  # 只替换有值的宏
                line = re.sub(r'\b' + re.escape(name) + r'\b', value, line)

        return line

    # ─────────────────────────────────────────────
    #  条件编译 #ifdef / #ifndef / #else / #endif
    # ─────────────────────────────────────────────
    def process_conditional(self, text):
        """处理条件编译指令（按顺序逐行处理）"""
        defined_names = set()
        lines = text.split("\n")
        result = []
        condition_stack = []  # [(active, seen_else)]

        for line in lines:
            stripped = line.strip()

            # 始终跟踪 #define / #undef（即使在非活跃块中也要跟踪顶层的）
            # 但只在活跃块中记录
            all_active = all(c[0] for c in condition_stack) if condition_stack else True

            if stripped.startswith("#ifdef"):
                name = stripped[len("#ifdef"):].strip()
                parent_active = all_active
                is_defined = name in defined_names
                condition_stack.append((parent_active and is_defined, False))
                continue

            elif stripped.startswith("#ifndef"):
                name = stripped[len("#ifndef"):].strip()
                parent_active = all_active
                is_defined = name in defined_names
                condition_stack.append((parent_active and not is_defined, False))
                continue

            elif stripped == "#else":
                if condition_stack:
                    active, seen_else = condition_stack[-1]
                    parent_active = all(c[0] for c in condition_stack[:-1]) if len(condition_stack) > 1 else True
                    condition_stack[-1] = (parent_active and not active, True)
                continue

            elif stripped == "#endif":
                if condition_stack:
                    condition_stack.pop()
                continue

            # 检查当前是否在活跃块中
            all_active = all(c[0] for c in condition_stack) if condition_stack else True

            if not all_active:
                continue

            # 在活跃块中跟踪 #define / #undef
            if stripped.startswith("#define"):
                parts = stripped[len("#define"):].strip().split(None, 1)
                if parts:
                    name = parts[0].split("(")[0]
                    defined_names.add(name)
            elif stripped.startswith("#undef") or stripped.startswith("#undefine"):
                if stripped.startswith("#undefine"):
                    name = stripped[len("#undefine"):].strip()
                else:
                    name = stripped[len("#undef"):].strip()
                defined_names.discard(name)

            result.append(line)

        return "\n".join(result)

    # ─────────────────────────────────────────────
    #  空格处理
    # ─────────────────────────────────────────────
    def remove_spaces_outside_quotes(self, text):
        """删除不在引号内的空格（引号内空格用占位符替代）"""
        in_quotes = False
        result = []
        for char in text:
            if char == '"':
                in_quotes = not in_quotes
            if char == ' ' and in_quotes:
                result.append('\x00')  # 占位符
            else:
                result.append(char)
        return ''.join(result)

    def remove_spaces_around_symbols(self, s):
        """只保留 "字母数字 字母数字" 之间的空格"""
        result = []
        i = 0
        while i < len(s):
            if s[i].isspace():
                if result and result[-1].isalnum():
                    j = i + 1
                    while j < len(s) and s[j].isspace():
                        j += 1
                    if j < len(s) and s[j].isalnum():
                        result.append(' ')
                i += 1
                while i < len(s) and s[i].isspace():
                    i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    def process_space(self, text):
        pre = self.remove_spaces_outside_quotes(text.replace('\n', '').replace('\t', ''))
        next = self.remove_spaces_around_symbols(pre)
        ans = next.replace('\x00', ' ')
        # 合并 else if → elif（方便语法解析）
        ans = ans.replace('else if', 'elif')
        # 将 && || 替换为特殊 token，避免与位运算 & | 冲突
        ans = ans.replace('&&', '~and~')
        ans = ans.replace('||', '~or~')
        return ans

    # ─────────────────────────────────────────────
    #  主入口
    # ─────────────────────────────────────────────
    def process(self, text):
        """完整预处理流水线"""
        text = self.process_include(text)
        text = self.process_conditional(text)   # 条件编译（#ifdef 等）
        text = self.process_define(text)
        text = self.process_note(text)
        text = self.process_space(text)
        return text
