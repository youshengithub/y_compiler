import re
from src.token_ana import *

# ============ 循环上下文栈（用于 break/continue）============
_loop_stack = []  # 每个元素 = {"break_placeholders": [], "continue_placeholders": []}

def _push_loop():
    _loop_stack.append({"break_placeholders": [], "continue_placeholders": []})

def _pop_loop():
    return _loop_stack.pop()

def _in_loop():
    return len(_loop_stack) > 0

def call_function():
    pass

def process_var(code, op):
    if op.isdigit():
        return "int", "", op
    else:
        index = code.rfind('/')
        if index == -1:
            print("var处理错误")
            assert(1 == 0)
        return code[index+1:-1], code, "$EAX"

def _addr(area_tree, op):
    """把 oplist 的字符串元素翻译为 runner 能识别的操作数。"""
    s = str(op)
    if s == "" or s.isdigit():
        return s
    # 负数常量
    if len(s) > 1 and s[0] == '-' and s[1:].isdigit():
        return s
    # 已经是寄存器名
    if s in ("EAX", "EBX", "ESP", "EBP", "EIP", "EFG", "ETP"):
        return s
    if s[0] in ("$", "%", "@"):
        return s
    # 处理数组下标访问 a[0] 或 a[i]
    if '[' in s:
        # 解析变量名和下标
        bracket_pos = s.index('[')
        var_name = s[:bracket_pos]
        idx_str = s[bracket_pos+1:-1]  # 去掉 [ 和 ]
        tk = area_tree.find_token(var_name)
        if tk is not None and hasattr(tk, "start_pos"):
            if idx_str.isdigit():
                # 常量下标：直接计算偏移
                return "$" + str(tk.start_pos) + ":" + idx_str
            elif idx_str[0] == '-' and idx_str[1:].isdigit():
                return "$" + str(tk.start_pos) + ":" + idx_str
            else:
                # 变量下标：需要间接寻址 $base:$idx_var_pos
                idx_tk = area_tree.find_token(idx_str)
                if idx_tk is not None and hasattr(idx_tk, "start_pos"):
                    return "$" + str(tk.start_pos) + ":$" + str(idx_tk.start_pos)
        return s
    # 处理结构体成员访问 a.b.c
    if '.' in s:
        parts = s.split('.')
        tk = area_tree.find_token(parts[0])
        if tk is not None and hasattr(tk, "start_pos"):
            offset = 0
            current_type = tk.type
            for member_name in parts[1:]:
                struct_def = area_tree.find_token(current_type)
                if struct_def is None:
                    return s  # 找不到结构体定义，返回原始
                member_found = False
                for var in struct_def.vars:
                    if var.name == member_name:
                        offset += var.start_pos
                        current_type = var.type
                        member_found = True
                        break
                if not member_found:
                    return s
            return "$" + str(tk.start_pos) + ":" + str(offset)
    # 试图在符号表里找
    try:
        tk = area_tree.find_token(s)
    except Exception:
        tk = None
    if tk is not None and hasattr(tk, "start_pos"):
        # 判断变量是否在当前顶级域中
        # 当前顶级域
        current_top = area_tree.find_top_father()
        # 查找变量所在的顶级域（沿父链查找包含该变量的area）
        search = area_tree
        var_top = None
        while search is not None:
            if hasattr(search, "vars"):
                for v in search.vars:
                    if v is tk:
                        var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                        break
            if var_top:
                break
            search = search.father
        # 如果变量在不同的顶级域中（全局变量），使用绝对地址
        if var_top is not None and var_top is not current_top:
            return "%" + str(tk.start_pos)
        return "$" + str(tk.start_pos)
    return s


def _resolve_break_continue(code, loop_info, step_lines=0):
    """回填 break/continue 的 JMP 占位符
    step_lines: 步进代码的行数（FOR循环中continue需要跳到步进代码而非末尾JMP）
    """
    lines = code.split("\n")
    total_lines = len([l for l in lines if l != ""])
    result_lines = []
    line_idx = 0
    for line in lines:
        if line == "":
            result_lines.append(line)
            continue
        if line == "JMP BREAK_PLACEHOLDER":
            # break 跳到循环末尾之后
            jump_offset = total_lines - line_idx
            result_lines.append("JMP " + str(jump_offset))
        elif line == "JMP CONTINUE_PLACEHOLDER":
            # continue: 跳到步进代码开头（距末尾 step_lines + 1 行之前）
            # FOR: step_lines > 0, continue 跳到 total_lines - step_lines - 1
            # WHILE/DO: step_lines = 0, continue 跳到回跳JMP（total_lines - 1）
            target_line = total_lines - step_lines - 1
            jump_offset = target_line - line_idx
            result_lines.append("JMP " + str(jump_offset))
        else:
            result_lines.append(line)
        line_idx += 1
    return "\n".join(result_lines)


def Complie(name, rule, oplist, codelist, area_tree):
    code = ""
    if name == "VAR":
        if not oplist[0] in ["EAX", "EBX", "ESP", "EBP", "EIP", "EFG", "ETP"]:
            if "[" not in oplist[0] and "." not in oplist[0]:
                return code, area_tree
            var = y_token.trans_var(oplist[0])
            base = 0
            code += "MOV EAX 0\n"
            for id, i in enumerate(var):
                if id == 0:
                    find_var = area_tree.find_token(i[0])
                else:
                    find_flag = False
                    for v in find_type.vars:
                        if v.name == i[0]:
                            find_var = v
                            find_flag = True
                            break
                    if not find_flag:
                        print(f"类型{find_type.name}不包含{i[0]}变量")
                        assert(1 == 0)

                if find_var is None:
                    print("变量未定义", oplist[0], "--->", i[0])
                    assert(1 == 0)

                find_type = area_tree.find_token(find_var.type)
                assert(find_type is not None)
                if len(i[1:]) != len(find_var.muti_dimension):
                    print("维度不匹配 ", oplist[0], "--->", i[0])
                    assert(1 == 0)
                base = find_var.start_pos
                if base != 0:
                    code += "ADD EAX " + str(base) + "\n"
                accumulate_demension = []
                current = 1
                for demension in reversed(find_var.muti_dimension):
                    accumulate_demension.append(current)
                    current *= demension
                accumulate_demension = [i * find_type.size for i in reversed(accumulate_demension)]
                for index in range(len(find_var.muti_dimension)):
                    if i[index+1].isdigit():
                        if int(i[index+1]) >= find_var.muti_dimension[index]:
                            print("维度超过限制")
                            assert(1 == 0)
                        code += "MOV EBX " + i[index+1] + "\n"
                    else:
                        idx_var = area_tree.find_token(i[index+1])
                        if idx_var is None:
                            print("变量未定义", oplist[0], "--->", i[index+1])
                            assert(1 == 0)
                        code += "MOV EBX $" + str(idx_var.start_pos) + "\n"
                    code += "MUL EBX " + str(accumulate_demension[index]) + "\n"
                    code += "ADD EAX EBX\n"
            code = code[:-1] + "//" + find_type.name + "\n"

    elif name == "OPN":
        if rule == "$CONST$":
            pass
        elif rule == "$VAR$":
            pass
        elif rule == "($OP$)":
            for i in codelist:
                code += i
        elif rule == "$CALL$":
            for i in codelist:
                code += i
        pass

    elif name == "TOKEN":
        pass
    elif name == "CONST":
        pass
    elif name == "AREA":
        for i in codelist:
            code += i
        if rule == "$AREA_S$$AREA_E$":
            code += "NOP\n"
    elif name == "REGS":
        pass

    elif name == "DIM":
        type_name = oplist[0]
        var = y_token.trans_token(oplist[1])
        num = 1
        for i in var[1:]:
            num *= int(i)
        find_type = area_tree.find_token(type_name)
        if find_type is None:
            print("编译出错,类型未定义:", type_name)
            assert(1 == 0)

        if rule == "$TYPE$$EMPTY$$TOKEN$":
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, [int(i) for i in var[1:]])
            area_tree.append_var(t, t.size)
            code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$OPN$":
            # 常量/变量初始化: int a = 5; 或 int a = b;
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, [int(i) for i in var[1:]])
            area_tree.append_var(t, t.size)
            code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"
            code += "MOV $" + str(start_pos) + " " + _addr(area_tree, oplist[2]) + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$OP$":
            # 表达式初始化: int a = b + c; 或 int a = 65;
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, [int(i) for i in var[1:]])
            area_tree.append_var(t, t.size)
            code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"
            # OP 代码在 codelist 最后一个元素（前面是 TYPE/EMPTY/TOKEN 的空代码）
            real_code = codelist[-1] if codelist else ""
            if real_code.strip() not in ("", "NOP"):
                # 有实际表达式代码，结果在 EAX
                code += real_code
                code += "MOV $" + str(start_pos) + " EAX\n"
            else:
                # 简单常量/变量，直接 MOV
                code += "MOV $" + str(start_pos) + " " + _addr(area_tree, oplist[2]) + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$STRING$":
            assert(type_name == "int" or type_name == "double")
            string = oplist[2]
            length = num
            if length < len(string):
                length = len(string)
            code = "ALLOC " + str(length) + "//" + type_name + "\n"
            base = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, base, [int(i) for i in var[1:]])
            area_tree.append_var(t, length)
            code = "ALLOC " + str(base + length) + "//" + type_name + "\n"
            for i in range(len(string)):
                code += "MOV $" + str(base) + ":" + str(i) + " " + str(ord(string[i])) + "\n"
            code += "MOV $" + str(base) + ":" + str(len(string)) + " 0\n"
        else:
            print("DIM unhandled rule:", rule, oplist)

    elif name == "OP":
        for i in codelist:
            code += i
        pass
    elif name == "FACTOR":
        for i in codelist:
            code += i
    elif name == "UNARY":
        for i in codelist:
            code += i

    elif name == "ADD":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "ADD EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            # 右表达式(EAX)，左叶子 → ADD 交换律
            code = right_code
            code += "ADD EAX " + _addr(area_tree, oplist[0]) + "\n"
        elif left_has and not right_has:
            code = left_code
            code += "ADD EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "ADD EAX EBX\n"

    elif name == "SUB":
        # codelist[0]=左子树代码, codelist[1]=右子树代码（含空占位符）
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            # 两边都是叶子
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SUB EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            # 左叶子，右表达式(EAX) → left - EAX
            code = right_code
            code += "MOV EBX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SUB EBX EAX\n"
            code += "MOV EAX EBX\n"
        elif left_has and not right_has:
            # 左表达式(EAX)，右叶子
            code = left_code
            code += "SUB EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            # 两边都是表达式：先算右→EBX，再算左→EAX
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "SUB EAX EBX\n"

    elif name == "MUL":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "MUL EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            code = right_code
            code += "MUL EAX " + _addr(area_tree, oplist[0]) + "\n"
        elif left_has and not right_has:
            code = left_code
            code += "MUL EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "MUL EAX EBX\n"

    elif name == "DIV":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "DIV EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            # 左叶子 / 右表达式(EAX)
            code = right_code
            code += "MOV EBX " + _addr(area_tree, oplist[0]) + "\n"
            code += "DIV EBX EAX\n"
            code += "MOV EAX EBX\n"
        elif left_has and not right_has:
            code = left_code
            code += "DIV EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "DIV EAX EBX\n"

    elif(name=="AND" or name=="XOR" or name=="OR"):
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code="MOV EAX "+_addr(area_tree,oplist[0])+"\n"
            code+=name+" EAX "+_addr(area_tree,oplist[1])+"\n"
        elif not left_has and right_has:
            code=right_code
            code+=name+" EAX "+_addr(area_tree,oplist[0])+"\n"
        elif left_has and not right_has:
            code=left_code
            code+=name+" EAX "+_addr(area_tree,oplist[-1])+"\n"
        else:
            code=right_code
            code+="MOV EBX EAX\n"
            code+=left_code
            code+=name+" EAX EBX\n"

    elif name == "MOD":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "MOD EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            # 左叶子 % 右表达式(EAX)
            code = right_code
            code += "MOV EBX EAX\n"
            code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "MOD EAX EBX\n"
        elif left_has and not right_has:
            code = left_code
            code += "MOD EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "MOD EAX EBX\n"

    elif name == "NOT":
        if rule == "!$OPN$":
            code = "NOT EAX " + _addr(area_tree, oplist[0]) + "\n"
        elif rule == "!$OP$":
            code = codelist[0]
            code += "MOV EBX EAX\n"
            code += "NOT EAX EBX\n"
        pass

    elif name == "GETP":
        code += "LEA EAX " + str(oplist[0]) + "\n"
        pass

    elif name == "SETP":
        if rule == "*$OPN$":
            code += "PUSH " + str(oplist[0]) + "\n"
        elif rule == "*$OP$":
            for i in codelist:
                code += i
            code += "PUSH EAX\n"
        pass

    elif name == "EQUAL":
        real_codes = [c for c in codelist if c.strip() not in ("", "NOP")]

        # 复合赋值运算符
        if "+=" in rule:
            if len(real_codes) > 0:
                code = real_codes[-1]
                code += "ADD EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "ADD EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "-=" in rule:
            if len(real_codes) > 0:
                code = real_codes[-1]
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SUB EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SUB EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "*=" in rule:
            if len(real_codes) > 0:
                code = real_codes[-1]
                code += "MUL EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MUL EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "/=" in rule:
            if len(real_codes) > 0:
                code = real_codes[-1]
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "DIV EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "DIV EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "%=" in rule:
            if len(real_codes) > 0:
                code = real_codes[-1]
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOD EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOD EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "=$OPN$" in rule or (len(real_codes) == 0 and "$SETP$" not in rule):
            code = "MOV " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[-1]) + "\n"
        elif "$VAR$" in rule.split('=')[0]:
            # 右侧 OP 代码是 codelist 的最后一个元素
            op_code = codelist[-1] if codelist else ""
            if op_code.strip() and op_code.strip() != "NOP":
                # 右侧有实际表达式代码（结果在 EAX），直接 MOV 到左值
                code = op_code
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                # 右侧是简单常量/变量，直接 MOV
                code = "MOV " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[-1]) + "\n"
        elif "$SETP$" in rule.split('=')[0]:
            if len(real_codes) <= 1:
                for i in codelist:
                    code += i
                code += "POP EBX\n"
                code += "SEA EBX " + str(oplist[-1]) + "\n"
            else:
                for i in codelist:
                    code += i
                code += "POP EBX\n"
                code += "SEA EBX EAX\n"
        pass

    elif name == "INCR":
        # i++ → 变量值 +1
        addr = _addr(area_tree, oplist[0])
        code = "MOV EAX " + addr + "\n"
        code += "ADD EAX 1\n"
        code += "MOV " + addr + " EAX\n"

    elif name == "DECR":
        # i-- → 变量值 -1
        addr = _addr(area_tree, oplist[0])
        code = "MOV EAX " + addr + "\n"
        code += "SUB EAX 1\n"
        code += "MOV " + addr + " EAX\n"

    elif name == "BREAK":
        code = "JMP BREAK_PLACEHOLDER\n"

    elif name == "CONTINUE":
        code = "JMP CONTINUE_PLACEHOLDER\n"

    elif name == "SENTENCE":
        for i in codelist:
            code += i
        pass

    elif name == "JUDGE":
        # 顺序：先匹配 <=/>=/==/!= 再匹配 < / >
        if rule.find("<=") != -1:
            code = "LE " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
        elif rule.find(">=") != -1:
            code = "GE " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
        elif rule.find("==") != -1:
            code = "EQUAL " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
        elif rule.find("!=") != -1:
            code = "EQUAL " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
            code += "RF\n"
        elif rule.find("<") != -1:
            code = "LESS " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
        elif rule.find(">") != -1:
            code = "GREATER " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[1]) + "\n"
        elif rule.find("&&") != -1:
            code = codelist[0]
            code += "JPIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        elif rule.find("||") != -1:
            code = codelist[0]
            code += "JPNIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        else:
            for i in codelist:
                code += i

    elif name == "IF":
        code = codelist[0]
        if len(codelist) >= 3:
            code += "JPIF " + str((codelist[1]).count("\n") + 2) + "\n"
            code += codelist[1]
            code += "JMP " + str((codelist[2]).count("\n") + 1) + "\n"
            code += codelist[2]
        else:
            code += "JPIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        pass

    elif name == "DO":
        _push_loop()
        code = codelist[0] + codelist[1]
        code += "RF\n"
        code += "JPIF -" + str((codelist[0] + codelist[1]).count("\n") + 1) + "\n"
        loop_info = _pop_loop()
        code = _resolve_break_continue(code, loop_info)
        pass

    elif name == "WHILE":
        _push_loop()
        code = codelist[0]
        code += "JPIF " + str(codelist[1].count("\n") + 2) + "\n"
        code += codelist[1]
        code += "JMP -" + str((codelist[0] + codelist[1]).count("\n") + 1) + "\n"
        loop_info = _pop_loop()
        code = _resolve_break_continue(code, loop_info)
        pass

    elif name == "FOR":
        _push_loop()
        code = codelist[0] + codelist[1]
        code += "JPIF " + str((codelist[3] + codelist[2]).count("\n") + 2) + "\n"
        code += codelist[3] + codelist[2]
        code += "JMP -" + str((codelist[1] + codelist[3] + codelist[2]).count("\n") + 1) + "\n"
        loop_info = _pop_loop()
        step_lines = len([l for l in codelist[2].split("\n") if l.strip()])
        code = _resolve_break_continue(code, loop_info, step_lines=step_lines)
        pass

    elif name == "PRINT":
        # 支持 out($OP$) 和 out($OPN$)
        if len(codelist) > 0 and codelist[0].strip():
            code = codelist[0]
            code += "OUT EAX\n"
        else:
            code = "OUT " + _addr(area_tree, oplist[0]) + "\n"
        pass

    elif name == "OUTNUM":
        # 输出数字（需要转为字符串）
        if len(codelist) > 0 and codelist[0].strip():
            code = codelist[0]
            code += "OUTNUM EAX\n"
        else:
            code = "OUTNUM " + _addr(area_tree, oplist[0]) + "\n"
        pass

    elif name == "IN":
        code = "IN EAX\n"

    elif name == "FUNCNAME":
        sub_area = area_tree.new_area(True, oplist[0])
        area_tree = sub_area
        pass

    elif name == "FUNC":
        for i in codelist:
            code += i
        revise_code = code.split("\n")[:-1]
        code = ""
        for i in range(len(revise_code)):
            toend = len(revise_code) - i
            revise_code[i] = revise_code[i].replace("END", str(toend))
            code = code + revise_code[i] + "\n"
        # 函数尾声：恢复寄存器（注意：不恢复 EAX，EAX 作为返回值通道）
        code += "MOV ESP $0:-6\n"
        code += "MOV EBX $0:-3\n"
        code += "MOV EFG $0:-2\n"
        code += "MOV ETP $0:-1\n"
        code += "MOV EBP $0:-5\n"
        code += "MOV EIP ETP\n"
        code = "JMP " + str(code.count("\n") + 1) + "\n" + code
        code = "ALLOC @" + oplist[1] + "\n" + code
        area_tree = area_tree.father
        # 解析形参
        t = y_token()
        par = []
        for i in codelist[0].split("\n"):
            if i != "" and len(i.split("//")) == 2:
                par.append(i.split("//")[1])
        t.set_as_function(oplist[0], oplist[1], par)
        area_tree.append_var(t)
        pass

    elif name == "CALL":
        # 检测方法调用 obj.method()
        if rule == "$TOKEN$.$CALL$":
            # 成员方法调用 — obj.method(args)
            # oplist[0] 是对象名（外层TOKEN），内层CALL递归处理
            # 这里需要把对象基地址作为隐式参数传入
            obj_name = oplist[0]
            obj_tk = area_tree.find_token(obj_name)
            if obj_tk is not None:
                # 获取对象的结构体类型
                struct_tk = area_tree.find_token(obj_tk.type)
                if struct_tk is not None and struct_tk.kind == token_type.structure:
                    # 在 codelist[0] 中已经有了内层 CALL 的代码
                    # 我们需要先压入对象基地址作为隐式第一个参数
                    # 但当前架构下内层CALL已经生成了完整代码
                    # 简单处理：直接使用内层CALL代码
                    for i in codelist:
                        code += i
                else:
                    for i in codelist:
                        code += i
            else:
                for i in codelist:
                    code += i
        else:
            # 普通函数调用
            # 使用 PUSH 将保存区压入栈（避免 $0:EAX 格式被 runner 错误解析）
            code = "PUSH ESP\n"       # [0] 保存 ESP
            code += "PUSH EBP\n"      # [1] 保存 EBP
            code += "PUSH EAX\n"      # [2] 保存 EAX（被覆盖无大碍）
            code += "PUSH EBX\n"      # [3] 保存 EBX
            code += "PUSH EFG\n"      # [4] 保存 EFG
            code += "ADD ESP 1\n"     # [5] 为返回地址留位置
            code += "MOV ETP ESP\n"   # ETP = 新栈帧基址
            # 压入参数（codelist中可能有TOKEN的空代码和ARG的参数代码）
            for c_item in codelist:
                if c_item.strip() and c_item.strip() != "NOP":
                    code += c_item

            # 保存返回地址到保存区 [5]（ETP-1 的位置）
            code += "MOV EAX EIP\n"
            code += "ADD EAX 6\n"
            code += "MOV EBX ETP\n"
            code += "SUB EBX 1\n"
            code += "SEA EBX EAX\n"   # memory[memory[EBX]] = EAX → memory[ETP-1] = 返回地址

            code += "MOV EBP ETP\n"
            code += "JMP @" + oplist[0] + "\n"
        pass

    elif name == "tPAR":
        for i in codelist:
            code += i
        pass

    elif name == "PAR":
        # 形参声明：只保留符号表注册，过滤掉ALLOC（空间由CALL端分配）
        for i in codelist:
            filtered = "\n".join(
                line for line in i.split("\n")
                if not line.startswith("ALLOC")
            )
            if filtered.strip():
                code += filtered + "\n"
        code += "NOP\n"
        pass

    elif name == "ARG":
        # 实参处理：透传 tARG 的代码
        for i in codelist:
            code += i
        pass

    elif name == "tARG":
        # tARG 递归处理参数列表 — 用 PUSH 压栈
        if rule == "$OPN$":
            addr = _addr(area_tree, oplist[0])
            code = "PUSH " + addr + "\n"
        elif rule == "$OP$":
            # 表达式参数：先计算（结果在EAX），然后PUSH
            real_code = codelist[0] if codelist else ""
            if real_code.strip() and real_code.strip() != "NOP":
                code = real_code
                code += "PUSH EAX\n"
            else:
                # 简单常量/变量
                addr = _addr(area_tree, oplist[0])
                code = "PUSH " + addr + "\n"
        elif "$OPN$,$tARG$" in rule:
            # 先处理当前参数（OPN），再递归处理剩余参数
            addr = _addr(area_tree, oplist[0])
            code = "PUSH " + addr + "\n"
            # 递归部分
            if codelist:
                code += codelist[0]
        elif "$OP$,$tARG$" in rule:
            # 先计算表达式参数
            real_code = codelist[0] if codelist else ""
            if real_code.strip() and real_code.strip() != "NOP":
                code = real_code
                code += "PUSH EAX\n"
            else:
                # 简单常量/变量
                addr = _addr(area_tree, oplist[0])
                code = "PUSH " + addr + "\n"
            # 递归部分
            if len(codelist) > 1:
                code += codelist[1]
        else:
            for i in codelist:
                code += i
        pass

    elif name == "RETURN":
        if "$OP$" in rule:
            real_codes = [c_item for c_item in codelist if c_item.strip() and c_item.strip() != "NOP"]
            if real_codes:
                for c_item in real_codes:
                    code += c_item
                # 表达式结果已在 EAX 中
            else:
                # OP 是简单常量/变量，需要显式 MOV EAX
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
        elif "$OPN$" in rule:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
        else:
            pass
        code += "JMP END\n"
        pass

    elif name == "TYPE":
        pass

    elif name == "STRUCTURE":
        t = y_token()
        func = []
        vars_list = []
        struture = []
        for i in area_tree.vars:
            if i.kind == token_type.function:
                func.append(i)
            elif i.kind == token_type.structure:
                struture.append(i)
            else:
                vars_list.append(i)
        t.set_as_structure(oplist[0], area_tree.clac_current_pos(), func, vars_list)
        area_tree = area_tree.father
        if area_tree.find_token(t.name) is not None:
            print(t.name, "结构体已经被定义")
            assert(1 == 0)
        area_tree.append_var(t)

    elif name == "ASM":
        code += oplist[0].replace("\\n", "\n")
        pass

    return code, area_tree
