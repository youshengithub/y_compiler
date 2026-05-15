import re
from src.token_ana import *

# ============ 循环上下文栈（用于 break/continue）============
_loop_stack = []  # 每个元素 = {"break_placeholders": [], "continue_placeholders": []}

# ============ 方法上下文栈（用于成员函数中的 this 指针）============
_method_stack = []  # 每个元素 = {"struct_vars": list, "this_pos": int}

# ============ 形参声明标志（用于数组参数的指针语义）============
_in_param_declaration = False

def _push_method(struct_vars, this_pos):
    """进入结构体方法时压栈"""
    _method_stack.append({"struct_vars": struct_vars, "this_pos": this_pos})

def _pop_method():
    """离开结构体方法时弹栈"""
    return _method_stack.pop()

def _in_method():
    """是否在结构体方法内"""
    return len(_method_stack) > 0

def _current_method_info():
    """获取当前方法的结构体信息"""
    return _method_stack[-1] if _method_stack else None

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
            # 检查是否在方法内且变量是结构体成员
            if _in_method():
                method_info = _current_method_info()
                struct_vars = method_info["struct_vars"]
                is_member = False
                for member in struct_vars:
                    if member is tk:
                        is_member = True
                        break
                if is_member:
                    this_pos = method_info["this_pos"]
                    # 数组成员通过 this 间接访问
                    if idx_str.isdigit():
                        return "@" + str(this_pos) + ":" + str(tk.start_pos + int(idx_str))
                    elif idx_str[0] == '-' and idx_str[1:].isdigit():
                        return "@" + str(this_pos) + ":" + str(tk.start_pos + int(idx_str))
                    else:
                        # 变量下标也可能是结构体成员
                        idx_tk = area_tree.find_token(idx_str)
                        if idx_tk is not None and hasattr(idx_tk, "start_pos"):
                            idx_is_member = False
                            for m in struct_vars:
                                if m is idx_tk:
                                    idx_is_member = True
                                    break
                            if idx_is_member:
                                return "@" + str(this_pos) + ":" + str(tk.start_pos) + ":@" + str(idx_tk.start_pos)
                            else:
                                return "@" + str(this_pos) + ":" + str(tk.start_pos) + ":$" + str(idx_tk.start_pos)
                    return s

            # 检测是否是全局变量
            prefix = "$"
            current_top = area_tree.find_top_father()
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
            if var_top is not None and var_top is not current_top:
                prefix = "%"

            # 检测是否是参数数组（指针语义）
            if getattr(tk, 'is_param_array', False):
                # 参数数组：tk.start_pos 存储的是传入的基地址
                # 访问 arr[i] = memory[memory[EBP + tk.start_pos] + i]
                if idx_str.isdigit():
                    return "~" + str(tk.start_pos) + ":" + idx_str
                elif idx_str[0] == '-' and idx_str[1:].isdigit():
                    return "~" + str(tk.start_pos) + ":" + idx_str
                else:
                    idx_tk = area_tree.find_token(idx_str)
                    if idx_tk is not None and hasattr(idx_tk, "start_pos"):
                        return "~" + str(tk.start_pos) + ":$" + str(idx_tk.start_pos)
                return s

            if idx_str.isdigit():
                # 常量下标：直接计算偏移
                return prefix + str(tk.start_pos) + ":" + idx_str
            elif idx_str[0] == '-' and idx_str[1:].isdigit():
                return prefix + str(tk.start_pos) + ":" + idx_str
            else:
                # 变量下标：需要间接寻址 $base:$idx_var_pos
                idx_tk = area_tree.find_token(idx_str)
                if idx_tk is not None and hasattr(idx_tk, "start_pos"):
                    return prefix + str(tk.start_pos) + ":$" + str(idx_tk.start_pos)
        return s
    # 处理结构体成员访问 a.b.c
    if '.' in s:
        parts = s.split('.')
        tk = area_tree.find_token(parts[0])
        if tk is not None and hasattr(tk, "start_pos"):
            # 检测是否是全局变量
            prefix = "$"
            current_top = area_tree.find_top_father()
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
            if var_top is not None and var_top is not current_top:
                prefix = "%"
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
            return prefix + str(tk.start_pos) + ":" + str(offset)
    # 试图在符号表里找
    try:
        tk = area_tree.find_token(s)
    except Exception:
        tk = None
    if tk is not None and hasattr(tk, "start_pos"):
        # 检查是否是结构体定义中的成员（在方法内通过 this 间接访问）
        if _in_method():
            method_info = _current_method_info()
            struct_vars = method_info["struct_vars"]
            for member in struct_vars:
                if member is tk:
                    # 这是结构体成员，需要通过 this 指针间接访问
                    this_pos = method_info["this_pos"]
                    return "@" + str(this_pos) + ":" + str(tk.start_pos)
        # 判断变量是否在当前顶级域中
        current_top = area_tree.find_top_father()
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
        elif rule == "$ARRIDX$":
            for i in codelist:
                code += i
        elif rule == "($OP$)":
            for i in codelist:
                code += i
        elif rule == "$CALL$":
            for i in codelist:
                code += i
        elif rule == "$TERNARY$":
            for i in codelist:
                code += i
        elif rule == "$DEREF$":
            for i in codelist:
                code += i
        elif rule == "$ADDROF$":
            for i in codelist:
                code += i
        elif rule == "$SIZEOF$":
            for i in codelist:
                code += i
        elif rule == "$NULLPTR$":
            pass
        pass

    elif name == "TERNARY":
        # (COND)?true_val:false_val
        # codelist[0]=条件代码, codelist[1]=true表达式代码, codelist[2]=false表达式代码
        cond_code = codelist[0] if len(codelist) > 0 else ""
        true_code = codelist[1] if len(codelist) > 1 else ""
        false_code = codelist[2] if len(codelist) > 2 else ""
        cond_has = cond_code.strip() not in ("", "NOP")
        true_has = true_code.strip() not in ("", "NOP")
        false_has = false_code.strip() not in ("", "NOP")
        # 条件判断
        code = cond_code
        # true/false 分支代码块
        true_block = ""
        if true_has:
            true_block = true_code
        else:
            true_block = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
        false_block = ""
        if false_has:
            false_block = false_code
        else:
            false_block = "MOV EAX " + _addr(area_tree, oplist[-1]) + "\n"
        # JPIF 跳过 true_block + JMP（+2：JMP自身和true_block行数）
        code += "JPIF " + str(true_block.count("\n") + 2) + "\n"
        code += true_block
        code += "JMP " + str(false_block.count("\n") + 1) + "\n"
        code += false_block
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
        # Check if this is a passthrough rule ($PTRDIM$ or $ARRINIT$)
        if rule == "$PTRDIM$" or rule == "$ARRINIT$":
            for i in codelist:
                code += i

        elif rule == "$TYPE$$EMPTY$$TOKEN$":
            type_name = oplist[0]
            var = y_token.trans_token(oplist[1])
            num = 1
            for i in var[1:]:
                num *= int(i)
            find_type = area_tree.find_token(type_name)
            if find_type is None:
                print("编译出错,类型未定义:", type_name)
                assert(1 == 0)
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            dimensions = [int(i) for i in var[1:]]
            if _in_param_declaration and len(dimensions) > 0:
                t.set_as_variable(var[0], 1, type_name, start_pos, dimensions)
                t.is_param_array = True
                area_tree.append_var(t, 1)
                code = "ALLOC " + str(start_pos + 1) + "//" + type_name + "\n"
            else:
                t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, dimensions)
                area_tree.append_var(t, t.size)
                code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$OPN$":
            type_name = oplist[0]
            var = y_token.trans_token(oplist[1])
            num = 1
            for i in var[1:]:
                num *= int(i)
            find_type = area_tree.find_token(type_name)
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, [int(i) for i in var[1:]])
            area_tree.append_var(t, t.size)
            code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"
            code += "MOV $" + str(start_pos) + " " + _addr(area_tree, oplist[2]) + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$OP$":
            type_name = oplist[0]
            var = y_token.trans_token(oplist[1])
            num = 1
            for i in var[1:]:
                num *= int(i)
            find_type = area_tree.find_token(type_name)
            start_pos = area_tree.clac_current_pos()
            t = y_token()
            t.set_as_variable(var[0], find_type.size * num, type_name, start_pos, [int(i) for i in var[1:]])
            area_tree.append_var(t, t.size)
            code = "ALLOC " + str(start_pos + t.size) + "//" + type_name + "\n"
            real_code = codelist[-1] if codelist else ""
            if real_code.strip() not in ("", "NOP"):
                code += real_code
                code += "MOV $" + str(start_pos) + " EAX\n"
            else:
                code += "MOV $" + str(start_pos) + " " + _addr(area_tree, oplist[2]) + "\n"

        elif rule == "$TYPE$$EMPTY$$TOKEN$=$STRING$":
            type_name = oplist[0]
            var = y_token.trans_token(oplist[1])
            num = 1
            for i in var[1:]:
                num *= int(i)
            find_type = area_tree.find_token(type_name)
            assert(type_name == "int" or type_name == "double")
            string = oplist[2]
            length = num
            if length < len(string):
                length = len(string)
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

    elif name == "SHL":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SHL EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            code = right_code
            code += "MOV EBX EAX\n"
            code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SHL EAX EBX\n"
        elif left_has and not right_has:
            code = left_code
            code += "SHL EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "SHL EAX EBX\n"

    elif name == "SHR":
        left_code = codelist[0] if len(codelist) > 0 else ""
        right_code = codelist[1] if len(codelist) > 1 else ""
        left_has = left_code.strip() not in ("", "NOP")
        right_has = right_code.strip() not in ("", "NOP")
        if not left_has and not right_has:
            code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SHR EAX " + _addr(area_tree, oplist[1]) + "\n"
        elif not left_has and right_has:
            code = right_code
            code += "MOV EBX EAX\n"
            code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
            code += "SHR EAX EBX\n"
        elif left_has and not right_has:
            code = left_code
            code += "SHR EAX " + _addr(area_tree, oplist[-1]) + "\n"
        else:
            code = right_code
            code += "MOV EBX EAX\n"
            code += left_code
            code += "SHR EAX EBX\n"

    elif name == "NOT":
        if rule == "!$OPN$":
            code = "NOT EAX " + _addr(area_tree, oplist[0]) + "\n"
        elif rule == "!$OP$":
            code = codelist[0]
            code += "MOV EBX EAX\n"
            code += "NOT EAX EBX\n"
        pass

    elif name == "NULLPTR":
        # NULL → 0
        code = "MOV EAX 0\n"

    elif name == "SIZEOF":
        # sizeof(type) → 返回类型大小
        type_name = oplist[0]
        find_type = area_tree.find_token(type_name)
        if find_type is not None:
            code = "MOV EAX " + str(find_type.size) + "\n"
        else:
            code = "MOV EAX 1\n"  # 默认大小为1

    elif name == "DEREF":
        # *ptr → 读取指针指向的值: memory[ptr_value]
        if rule == "*$OPN$":
            addr = _addr(area_tree, oplist[0])
            code = "MOV EAX " + addr + "\n"
            code += "LEA EAX EAX\n"  # EAX = memory[EAX]
        elif rule == "*$OP$":
            inner_code = codelist[0] if codelist else ""
            if inner_code.strip() and inner_code.strip() != "NOP":
                code = inner_code
                code += "LEA EAX EAX\n"
            else:
                # OP with no code (simple variable/constant)
                addr = _addr(area_tree, oplist[0])
                code = "MOV EAX " + addr + "\n"
                code += "LEA EAX EAX\n"

    elif name == "ADDROF":
        # &var → 获取变量的绝对地址
        var_name = oplist[0]
        tk = area_tree.find_token(var_name)
        if tk is not None and hasattr(tk, "start_pos"):
            # 检查是否全局变量
            current_top = area_tree.find_top_father()
            search = area_tree
            var_top = None
            while search is not None:
                if hasattr(search, "vars"):
                    for v in search.vars:
                        if v is tk:
                            var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                            break
                if var_top: break
                search = search.father
            is_global = (var_top is not None and var_top is not current_top)
            if is_global:
                code = "MOV EAX " + str(tk.start_pos) + "\n"
            else:
                code = "MOV EAX EBP\n"
                code += "ADD EAX " + str(tk.start_pos) + "\n"
        else:
            code = "MOV EAX 0\n"

    elif name == "GETP":
        # &var → 获取变量的绝对地址（等同于 ADDROF）
        var_name = oplist[0]
        tk = area_tree.find_token(var_name)
        if tk is not None and hasattr(tk, "start_pos"):
            # 检查是否全局变量
            current_top = area_tree.find_top_father()
            search = area_tree
            var_top = None
            while search is not None:
                if hasattr(search, "vars"):
                    for v in search.vars:
                        if v is tk:
                            var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                            break
                if var_top: break
                search = search.father
            is_global = (var_top is not None and var_top is not current_top)
            if is_global:
                code = "MOV EAX " + str(tk.start_pos) + "\n"
            else:
                code = "MOV EAX EBP\n"
                code += "ADD EAX " + str(tk.start_pos) + "\n"
        else:
            code = "MOV EAX 0\n"

    elif name == "SETP":
        if rule == "*$OPN$":
            code += "PUSH " + _addr(area_tree, oplist[0]) + "\n"
        elif rule == "*$OP$":
            inner_code = ""
            for i in codelist:
                inner_code += i
            if inner_code.strip() and inner_code.strip() != "NOP":
                code = inner_code
                code += "PUSH EAX\n"
            else:
                # Simple variable through OP path
                code = "PUSH " + _addr(area_tree, oplist[0]) + "\n"
        pass

    elif name == "EQUAL":
        # 获取右值代码（codelist的最后一个元素对应右侧表达式）
        rhs_code = codelist[-1] if codelist else ""
        rhs_has_code = rhs_code.strip() not in ("", "NOP")

        # 复合赋值运算符
        if "+=" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "ADD EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "ADD EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "-=" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SUB EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SUB EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "*=" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MUL EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MUL EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "/=" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "DIV EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "DIV EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "%=" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOD EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "MOD EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "~shla~" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SHL EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SHL EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "~shra~" in rule:
            if rhs_has_code:
                code = rhs_code
                code += "MOV EBX EAX\n"
                code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SHR EAX EBX\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
            else:
                code = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
                code += "SHR EAX " + _addr(area_tree, oplist[-1]) + "\n"
                code += "MOV " + _addr(area_tree, oplist[0]) + " EAX\n"
        elif "=$OPN$" in rule or (not rhs_has_code and "$SETP$" not in rule and "$ARRIDX$" not in rule):
            code = "MOV " + _addr(area_tree, oplist[0]) + " " + _addr(area_tree, oplist[-1]) + "\n"
        elif "$ARRIDX$" in rule.split('=')[0]:
            # 数组表达式下标赋值: a[expr] = rhs
            arr_name = oplist[0]
            tk = area_tree.find_token(arr_name)
            base_pos = tk.start_pos if tk and hasattr(tk, "start_pos") else 0
            # 检查全局
            current_top = area_tree.find_top_father()
            search = area_tree
            var_top = None
            while search is not None:
                if hasattr(search, "vars"):
                    for v in search.vars:
                        if v is tk:
                            var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                            break
                if var_top: break
                search = search.father
            is_global = (var_top is not None and var_top is not current_top)
            
            # ARRIDX 的索引表达式代码在 codelist[0] 中（ARRIDX 编译结果）
            # 但 ARRIDX 编译结果包含 LEA（读取值），我们需要的是地址
            # 直接从 codelist 获取索引代码
            idx_code = codelist[0] if len(codelist) > 0 else ""
            rhs_code_part = codelist[-1] if len(codelist) > 1 else ""
            rhs_has = rhs_code_part.strip() not in ("", "NOP")
            # 只有当 ARRIDX 代码包含 LEA（表达式下标地址计算）时才走地址模式
            # 简单下标的 ARRIDX 代码只是 "MOV EAX value"，不含 LEA
            idx_has_addr = idx_code.strip() not in ("", "NOP") and "LEA EAX EAX" in idx_code
            
            if idx_has_addr:
                # 去掉 ARRIDX 生成的 LEA（获取地址而非值）
                addr_code = idx_code.replace("LEA EAX EAX\n", "")
                if rhs_has:
                    # 先算右值
                    code = rhs_code_part
                    code += "PUSH EAX\n"
                    # 再算地址
                    code += addr_code  # EAX = 地址
                    code += "POP EBX\n"
                    code += "SEA EAX EBX\n"
                else:
                    code = addr_code  # EAX = 地址
                    code += "SEA EAX " + _addr(area_tree, oplist[-1]) + "\n"
            else:
                # 简单索引：走原始 _addr 路径
                idx_val = oplist[1] if len(oplist) > 1 else "0"
                full_ref = _addr(area_tree, arr_name + "[" + idx_val + "]")
                if rhs_has:
                    code = rhs_code_part
                    code += "MOV " + full_ref + " EAX\n"
                else:
                    code = "MOV " + full_ref + " " + _addr(area_tree, oplist[-1]) + "\n"
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
            if not rhs_has_code:
                for i in codelist:
                    code += i
                code += "POP EBX\n"
                code += "SEA EBX " + _addr(area_tree, oplist[-1]) + "\n"
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
    elif name == "PTRDIM":
        # 指针变量声明：int *p = expr; 或 int *p;
        type_name = oplist[0]
        var_name = oplist[1] if len(oplist) > 1 else oplist[0]
        # 在 oplist 中找到变量名（TYPE 之后的 TOKEN）
        # oplist: [type, var_name] 或 [type, var_name, init_value]
        # 指针只占 1 个内存单元（存储地址）
        start_pos = area_tree.clac_current_pos()
        t = y_token()
        t.set_as_variable(var_name, 1, type_name + "*", start_pos, [])
        t.is_pointer = True
        area_tree.append_var(t, 1)
        code = "ALLOC " + str(start_pos + 1) + "//" + type_name + "*\n"
        # 如果有初始化表达式
        if len(codelist) > 0:
            init_code = codelist[-1] if codelist else ""
            if init_code.strip() and init_code.strip() != "NOP":
                code += init_code
                code += "MOV $" + str(start_pos) + " EAX\n"
            elif len(oplist) > 2:
                code += "MOV $" + str(start_pos) + " " + _addr(area_tree, oplist[-1]) + "\n"

    elif name == "ARRINIT":
        # 数组字面量初始化：int a[] = {1, 2, 3};
        type_name = oplist[0]
        var = y_token.trans_token(oplist[1])
        var_name = var[0]
        find_type = area_tree.find_token(type_name)
        if find_type is None:
            print("编译出错,类型未定义:", type_name)
            assert(1 == 0)
        # 收集初始化列表中的值
        init_vals = oplist[2:]  # INITLIST 中的值
        arr_size = len(init_vals)
        if len(var) > 1 and var[1].isdigit():
            declared_size = int(var[1])
            arr_size = max(arr_size, declared_size)
        start_pos = area_tree.clac_current_pos()
        t = y_token()
        t.set_as_variable(var_name, arr_size, type_name, start_pos, [arr_size])
        area_tree.append_var(t, arr_size)
        code = "ALLOC " + str(start_pos + arr_size) + "//" + type_name + "\n"
        # 逐个初始化
        for idx, val in enumerate(init_vals):
            # 检查是否有对应的代码（表达式初始化）
            if idx < len(codelist) and codelist[idx].strip() and codelist[idx].strip() != "NOP":
                code += codelist[idx]
                code += "MOV $" + str(start_pos) + ":" + str(idx) + " EAX\n"
            else:
                code += "MOV $" + str(start_pos) + ":" + str(idx) + " " + _addr(area_tree, val) + "\n"

    elif name == "INITLIST":
        # 透传初始化列表中的表达式代码
        for i in codelist:
            code += i

    elif name == "FREESTMT":
        # free(ptr) — 释放指针指向的内存
        if len(codelist) > 0 and codelist[0].strip() and codelist[0].strip() != "NOP":
            code = codelist[0]
            code += "FREE EAX\n"
        else:
            code = "FREE " + _addr(area_tree, oplist[0]) + "\n"

    elif name == "FUNCDECL":
        # 函数前置声明：只注册签名到符号表，不生成代码
        t = y_token()
        par = []
        for i in codelist[0].split("\n") if codelist else []:
            if i != "" and len(i.split("//")) == 2:
                par.append(i.split("//")[1])
        t.set_as_function(oplist[0], oplist[1], par)
        area_tree.append_var(t)

    elif name == "ARRIDX":
        # $VAR$[$OP$] — oplist[0] = 数组名, codelist[1] = 索引表达式代码
        arr_name = oplist[0]
        idx_code = codelist[1] if len(codelist) > 1 else ""
        idx_has = idx_code.strip() not in ("", "NOP")
        
        # 获取数组基地址信息
        tk = area_tree.find_token(arr_name)
        if tk is not None and hasattr(tk, "start_pos"):
            base_pos = tk.start_pos
            # 检查是否全局变量
            current_top = area_tree.find_top_father()
            search = area_tree
            var_top = None
            while search is not None:
                if hasattr(search, "vars"):
                    for v in search.vars:
                        if v is tk:
                            var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                            break
                if var_top: break
                search = search.father
            is_global = (var_top is not None and var_top is not current_top)
            is_param_arr = getattr(tk, 'is_param_array', False)
        else:
            base_pos = 0
            is_global = False
            is_param_arr = False
        
        if idx_has:
            if is_param_arr:
                # 参数数组+表达式下标：EAX = memory[memory[EBP+base_pos] + idx_expr]
                code = idx_code  # EAX = 索引表达式的值
                code += "MOV EBX $" + str(base_pos) + "\n"  # EBX = 传入的基地址
                code += "ADD EAX EBX\n"  # EAX = 基地址 + 索引
                code += "LEA EAX EAX\n"  # EAX = memory[EAX]
            elif is_global:
                # 全局数组+表达式下标
                code = idx_code
                code += "ADD EAX " + str(base_pos) + "\n"
                code += "LEA EAX EAX\n"
            else:
                # 局部数组+表达式下标：EAX = memory[EBP + base_pos + idx_expr]
                code = idx_code  # EAX = 索引表达式的值
                code += "ADD EAX EBP\n"
                if base_pos != 0:
                    code += "ADD EAX " + str(base_pos) + "\n"
                code += "LEA EAX EAX\n"
        else:
            # 索引是简单变量/常量：直接用 _addr 格式
            idx_val = oplist[1] if len(oplist) > 1 else "0"
            arr_ref = _addr(area_tree, arr_name + "[" + idx_val + "]")
            code = "MOV EAX " + arr_ref + "\n"
    elif name == "JUDGE":
        # JUDGE 的子规则: $OP$==$OP$ / $OP$>=$OP$ / ($COND$) 等
        if rule.find("<=") != -1 or rule.find(">=") != -1 or rule.find("==") != -1 or rule.find("!=") != -1 or rule.find("<") != -1 or rule.find(">") != -1:
            # 比较运算：左OP codelist[0], 右OP codelist[1]
            left_code = codelist[0] if len(codelist) > 0 else ""
            right_code = codelist[1] if len(codelist) > 1 else ""
            left_has = left_code.strip() not in ("", "NOP")
            right_has = right_code.strip() not in ("", "NOP")

            if not left_has and not right_has:
                left_addr = _addr(area_tree, oplist[0])
                right_addr = _addr(area_tree, oplist[1]) if len(oplist) > 1 else _addr(area_tree, oplist[0])
            elif left_has and not right_has:
                code = left_code
                left_addr = "EAX"
                right_addr = _addr(area_tree, oplist[-1])
            elif not left_has and right_has:
                code = right_code
                left_addr = _addr(area_tree, oplist[0])
                right_addr = "EAX"
            else:
                code = right_code
                code += "MOV EBX EAX\n"
                code += left_code
                left_addr = "EAX"
                right_addr = "EBX"

            if rule.find("<=") != -1:
                cmp_code = "LE " + left_addr + " " + right_addr + "\n"
            elif rule.find(">=") != -1:
                cmp_code = "GE " + left_addr + " " + right_addr + "\n"
            elif rule.find("==") != -1:
                cmp_code = "EQUAL " + left_addr + " " + right_addr + "\n"
            elif rule.find("!=") != -1:
                cmp_code = "EQUAL " + left_addr + " " + right_addr + "\n"
                cmp_code += "RF\n"
            elif rule.find("<") != -1:
                cmp_code = "LESS " + left_addr + " " + right_addr + "\n"
            elif rule.find(">") != -1:
                cmp_code = "GREATER " + left_addr + " " + right_addr + "\n"
            else:
                cmp_code = ""
            code += cmp_code
        else:
            # 检查是否是逻辑非 !$<OP|OPN>$
            if "!" in rule and "$COND$" not in rule:
                # !expr → EQUAL expr 0 (expr == 0 时 EFG=False, JPIF 不跳 = 条件真)
                # 但 JPIF 在 EFG==True 时跳转... 
                # 实际上：EQUAL $x 0 → EFG = not (x == 0) → 如果 x==0 则 EFG=False（不跳转）
                # 我们需要：!x 为真（x==0）时 EFG=False（不跳转）→ EQUAL x 0 正好
                expr_code = codelist[0] if len(codelist) > 0 else ""
                expr_has = expr_code.strip() not in ("", "NOP")
                if expr_has:
                    code = expr_code
                    code += "EQUAL EAX 0\n"
                else:
                    code = "EQUAL " + _addr(area_tree, oplist[0]) + " 0\n"
            else:
                # ($COND$) — 括号条件，透传
                for i in codelist:
                    code += i

    elif name == "COND":
        # COND: $JUDGE$~and~$COND$ / $JUDGE$~or~$COND$ / $JUDGE$
        if rule.find("~and~") != -1:
            code = codelist[0]
            code += "JPIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        elif rule.find("~or~") != -1:
            code = codelist[0]
            code += "JPNIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        else:
            # 单纯的 $JUDGE$ 透传
            for i in codelist:
                code += i

    elif name == "IF":
        code = codelist[0]
        if len(codelist) >= 3:
            # if-else 或 if-elif
            code += "JPIF " + str((codelist[1]).count("\n") + 2) + "\n"
            code += codelist[1]
            code += "JMP " + str((codelist[2]).count("\n") + 1) + "\n"
            code += codelist[2]
        elif len(codelist) >= 2:
            code += "JPIF " + str((codelist[1]).count("\n") + 1) + "\n"
            code += codelist[1]
        pass

    elif name == "ELIF":
        # ELIF 结构类似 IF：JUDGE + AREA + 可选(递归ELIF 或 else AREA)
        code = codelist[0]  # JUDGE 条件代码
        if len(codelist) >= 3:
            # elif(cond){body} + 递归ELIF/else
            code += "JPIF " + str((codelist[1]).count("\n") + 2) + "\n"
            code += codelist[1]
            code += "JMP " + str((codelist[2]).count("\n") + 1) + "\n"
            code += codelist[2]
        elif len(codelist) >= 2:
            # elif(cond){body} 无else
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
        # 检查是否在结构体定义内
        # 结构体AREA子域中定义的FUNC，其parent是结构体的AREA子域
        parent = sub_area.father
        if parent is not None:
            is_in_struct = False
            struct_name_found = ""
            if parent.name != "Main" and parent.name != " ":
                for v in parent.vars:
                    if v.kind == token_type.variable:
                        is_in_struct = True
                        struct_name_found = parent.name
                        break
            if is_in_struct:
                # 在结构体方法内，注入隐式 _this 参数
                this_pos = sub_area.clac_current_pos()
                this_token = y_token()
                this_token.set_as_variable("_this", 1, "int", this_pos, [])
                sub_area.append_var(this_token, 1)
                # 收集结构体成员变量（排除函数）
                struct_member_vars = [v for v in parent.vars if v.kind == token_type.variable]
                _push_method(struct_member_vars, this_pos)
        pass

    elif name == "FUNC":
        # 检查当前函数是否在结构体内定义（方法）
        # 通过检查 area_tree.father 是否有结构体的特征来判断
        is_method = False
        struct_name = ""
        parent_area = area_tree.father
        if parent_area is not None:
            # 检查父域中是否有结构体类型（即我们在结构体定义的 AREA 中）
            # 结构体的 AREA 不是 top_area
            if not parent_area.is_top_area or (parent_area.father is not None and hasattr(parent_area, 'name')):
                # 更可靠的检测：检查 area_tree 的 name 是否被注册为某个结构体的方法
                # 简化方案：如果 STRUCTURE 规则正在处理，那么 FUNC 在其子域中
                # 我们通过检查 grandparent 是否正在构建结构体来判断
                # 实际上用 area_tree.father 的 vars 里是否有结构体定义来判断
                pass

        for i in codelist:
            code += i

        # 如果是方法，弹出方法上下文
        if _in_method():
            _pop_method()

        revise_code = code.split("\n")[:-1]
        code = ""
        for i in range(len(revise_code)):
            toend = len(revise_code) - i
            revise_code[i] = revise_code[i].replace("END", str(toend))
            code = code + revise_code[i] + "\n"
        # 函数尾声：恢复寄存器
        # 保存区布局 [-7]:ESP [-6]:EBP [-5]:EAX [-4]:EBX [-3]:EFG [-2]:ETP [-1]:返回地址
        code += "MOV ESP $0:-7\n"   # 恢复 ESP
        code += "MOV EBX $0:-4\n"   # 恢复 EBX
        code += "MOV EFG $0:-1\n"   # 暂存返回地址到 EFG（EFG旧值不重要）
        code += "MOV ETP $0:-2\n"   # 恢复 ETP
        code += "MOV EBP $0:-6\n"   # 恢复 EBP
        code += "MOV EIP EFG\n"     # 绝对跳转到返回地址
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
        # 检测指针方法调用 ptr->method()
        if rule == "$TOKEN$~arrow~$CALL$":
            # ptr->method() — 解引用指针然后调用方法
            ptr_name = oplist[0]
            ptr_tk = area_tree.find_token(ptr_name)
            if ptr_tk is not None:
                # 获取指针指向的结构体类型
                ptr_type = getattr(ptr_tk, 'type', '')
                struct_type_name = ptr_type.replace('*', '') if ptr_type else ''
                struct_tk = area_tree.find_token(struct_type_name)
                if struct_tk is not None and struct_tk.kind == token_type.structure:
                    inner_code = ""
                    for i in codelist:
                        inner_code += i
                    marker = "MOV ETP ESP\n"
                    if marker in inner_code:
                        idx = inner_code.index(marker) + len(marker)
                        ptr_addr = _addr(area_tree, ptr_name)
                        this_push = "PUSH " + ptr_addr + "\n"
                        code = inner_code[:idx] + this_push + inner_code[idx:]
                    else:
                        code = inner_code
                else:
                    for i in codelist:
                        code += i
            else:
                for i in codelist:
                    code += i
        # 检测方法调用 obj.method()
        elif rule == "$TOKEN$.$CALL$":
            # 成员方法调用 — obj.method(args)
            # oplist[0] 是对象名（外层TOKEN）
            # codelist 中包含内层 CALL 已经完整生成的调用代码
            obj_name = oplist[0]
            obj_tk = area_tree.find_token(obj_name)
            if obj_tk is not None:
                struct_tk = area_tree.find_token(obj_tk.type)
                if struct_tk is not None and struct_tk.kind == token_type.structure:
                    # 内层 CALL 已经生成了完整的函数调用代码
                    # 我们需要在保存区建立之后、参数压栈之前，插入隐式 this (对象基地址)
                    inner_code = ""
                    for i in codelist:
                        inner_code += i
                    # 找到 "MOV ETP ESP\n" 的位置，在其后插入 PUSH 对象地址
                    marker = "MOV ETP ESP\n"
                    if marker in inner_code:
                        idx = inner_code.index(marker) + len(marker)
                        obj_addr = _addr(area_tree, obj_name)
                        # 如果对象是相对地址($N)，我们需要传递实际地址 = EBP + N
                        if obj_addr.startswith("$"):
                            this_push = "MOV EAX EBP\nADD EAX " + obj_addr[1:] + "\nPUSH EAX\n"
                        elif obj_addr.startswith("%"):
                            this_push = "PUSH " + obj_addr[1:] + "\n"
                        else:
                            this_push = "PUSH " + obj_addr + "\n"
                        code = inner_code[:idx] + this_push + inner_code[idx:]
                    else:
                        code = inner_code
                else:
                    for i in codelist:
                        code += i
            else:
                for i in codelist:
                    code += i
        else:
            # 检查是否为内置函数
            func_name = oplist[0]
            if func_name == "malloc":
                # malloc(size) — 内置堆分配，返回地址在EAX
                # tARG 生成的代码是 PUSH xxx，我们需要提取参数值
                arg_code = ""
                for c_item in codelist:
                    if c_item.strip() and c_item.strip() != "NOP":
                        arg_code += c_item
                # 把 PUSH 替换为 MOV EBX（我们需要参数值而非压栈）
                if arg_code:
                    # 将所有 PUSH xxx\n 改为 MOV EBX xxx\n
                    import re
                    code = re.sub(r'PUSH (.+)\n', r'MOV EBX \1\n', arg_code)
                    code += "MALLOC EAX EBX\n"
                else:
                    code = "MALLOC EAX " + _addr(area_tree, oplist[-1]) + "\n"
            elif func_name == "free":
                # free(ptr)
                arg_code = ""
                for c_item in codelist:
                    if c_item.strip() and c_item.strip() != "NOP":
                        arg_code += c_item
                if arg_code:
                    import re
                    code = re.sub(r'PUSH (.+)\n', r'MOV EAX \1\n', arg_code)
                    code += "FREE EAX\n"
                else:
                    code = "MOV EAX " + _addr(area_tree, oplist[-1]) + "\n"
                    code += "FREE EAX\n"
            elif func_name == "printf":
                # printf(fmt, args...) — 格式化输出
                # 这里简化处理：将所有参数压栈后调用 PRINTF
                # 实际上 printf 的第一个参数是格式字符串地址
                arg_code = ""
                for c_item in codelist:
                    if c_item.strip() and c_item.strip() != "NOP":
                        arg_code += c_item
                # 计算参数个数（通过 PUSH 指令数量）
                push_count = arg_code.count("PUSH ")
                # 格式字符串地址在第一个参数
                code = arg_code
                # 用简化的 OUTNUM/OUT 序列代替（因为我们无法在编译期解析格式串）
                # 实际 printf 支持需要运行时解析，此处直接透传参数
                code += "PRINTF EAX " + str(push_count) + "\n"
            else:
                # 普通函数调用
                # 保存区布局（相对 EBP 的负偏移）：
                # [-7]: ESP, [-6]: EBP, [-5]: EAX, [-4]: EBX, [-3]: EFG, [-2]: ETP, [-1]: 返回地址
                code = "PUSH ESP\n"       # [-7]
                code += "PUSH EBP\n"      # [-6]
                code += "PUSH EAX\n"      # [-5]
                code += "PUSH EBX\n"      # [-4]
                code += "PUSH EFG\n"      # [-3]
                code += "PUSH ETP\n"      # [-2]
                code += "ADD ESP 1\n"     # [-1] 为返回地址预留
                code += "MOV ETP ESP\n"   # ETP = 新栈帧基址
                # 压入参数
                for c_item in codelist:
                    if c_item.strip() and c_item.strip() != "NOP":
                        code += c_item

                # 保存返回地址
                code += "MOV EAX EIP\n"
                code += "ADD EAX 7\n"
                code += "MOV EBX ETP\n"
                code += "SUB EBX 1\n"
                code += "SEA EBX EAX\n"

                code += "MOV EBP ETP\n"
                code += "JMP @" + func_name + "\n"
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
        # 标记数组形参为 is_param_array（指针语义）
        for v in area_tree.vars:
            if v.kind == token_type.variable and hasattr(v, 'muti_dimension') and len(v.muti_dimension) > 0:
                v.is_param_array = True
                # 数组形参只占 1 个位置（存储基地址），不需要 N 个位置
                # 但由于 DIM 已经分配了 N 个位置，这里调整大小
                # 实际不影响正确性：ALLOC 被过滤了，调用端只 PUSH 了 1 个值
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
            # 检查是否是数组名（传引用）
            tk = area_tree.find_token(oplist[0])
            if tk is not None and hasattr(tk, 'muti_dimension') and len(tk.muti_dimension) > 0:
                # 数组参数：传递绝对地址 = EBP + start_pos
                # 检查是否是全局变量
                current_top = area_tree.find_top_father()
                search = area_tree
                var_top = None
                while search is not None:
                    if hasattr(search, "vars"):
                        for v in search.vars:
                            if v is tk:
                                var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                                break
                    if var_top: break
                    search = search.father
                is_global = (var_top is not None and var_top is not current_top)
                if is_global:
                    # 全局数组：直接传绝对地址
                    code = "PUSH " + str(tk.start_pos) + "\n"
                elif getattr(tk, 'is_param_array', False):
                    # 参数数组再次传递：直接传存储的基地址值
                    code = "PUSH $" + str(tk.start_pos) + "\n"
                else:
                    # 局部数组：计算绝对地址 = EBP + start_pos
                    code = "MOV EAX EBP\n"
                    code += "ADD EAX " + str(tk.start_pos) + "\n"
                    code += "PUSH EAX\n"
            else:
                code = "PUSH " + addr + "\n"
        elif rule == "$OP$":
            # 表达式参数：先计算（结果在EAX），然后PUSH
            real_code = codelist[0] if codelist else ""
            if real_code.strip() and real_code.strip() != "NOP":
                code = real_code
                code += "PUSH EAX\n"
            else:
                # 简单常量/变量 — 检查是否是数组名
                tk = area_tree.find_token(oplist[0])
                if tk is not None and hasattr(tk, 'muti_dimension') and len(tk.muti_dimension) > 0:
                    # 数组参数：传递绝对地址
                    current_top = area_tree.find_top_father()
                    search = area_tree
                    var_top = None
                    while search is not None:
                        if hasattr(search, "vars"):
                            for v in search.vars:
                                if v is tk:
                                    var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                                    break
                        if var_top: break
                        search = search.father
                    is_global = (var_top is not None and var_top is not current_top)
                    if is_global:
                        code = "PUSH " + str(tk.start_pos) + "\n"
                    elif getattr(tk, 'is_param_array', False):
                        code = "PUSH $" + str(tk.start_pos) + "\n"
                    else:
                        code = "MOV EAX EBP\n"
                        code += "ADD EAX " + str(tk.start_pos) + "\n"
                        code += "PUSH EAX\n"
                else:
                    addr = _addr(area_tree, oplist[0])
                    code = "PUSH " + addr + "\n"
        elif "$OPN$,$tARG$" in rule:
            # 先处理当前参数（OPN），再递归处理剩余参数
            # 检查是否是数组名（传引用）
            tk = area_tree.find_token(oplist[0])
            if tk is not None and hasattr(tk, 'muti_dimension') and len(tk.muti_dimension) > 0:
                # 数组参数：传递绝对地址
                current_top = area_tree.find_top_father()
                search = area_tree
                var_top = None
                while search is not None:
                    if hasattr(search, "vars"):
                        for v in search.vars:
                            if v is tk:
                                var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                                break
                    if var_top: break
                    search = search.father
                is_global = (var_top is not None and var_top is not current_top)
                if is_global:
                    code = "PUSH " + str(tk.start_pos) + "\n"
                elif getattr(tk, 'is_param_array', False):
                    code = "PUSH $" + str(tk.start_pos) + "\n"
                else:
                    code = "MOV EAX EBP\n"
                    code += "ADD EAX " + str(tk.start_pos) + "\n"
                    code += "PUSH EAX\n"
            else:
                addr = _addr(area_tree, oplist[0])
                code = "PUSH " + addr + "\n"
            # 递归部分
            if codelist:
                code += codelist[0]
        elif "$OP$,$tARG$" in rule:
            # 先计算表达式参数
            real_code = codelist[0] if codelist else ""
            if real_code.strip() and real_code.strip() != "NOP":
                # 可能是数组名通过 OP→FACTOR→UNARY→OPN→VAR 路径（无实际代码）
                # 但此处 real_code 非空，说明是真正的表达式
                code = real_code
                code += "PUSH EAX\n"
            else:
                # 简单常量/变量 — 检查是否是数组名
                tk = area_tree.find_token(oplist[0])
                if tk is not None and hasattr(tk, 'muti_dimension') and len(tk.muti_dimension) > 0:
                    # 数组参数：传递绝对地址
                    current_top = area_tree.find_top_father()
                    search = area_tree
                    var_top = None
                    while search is not None:
                        if hasattr(search, "vars"):
                            for v in search.vars:
                                if v is tk:
                                    var_top = search.find_top_father() if hasattr(search, 'find_top_father') else search
                                    break
                        if var_top: break
                        search = search.father
                    is_global = (var_top is not None and var_top is not current_top)
                    if is_global:
                        code = "PUSH " + str(tk.start_pos) + "\n"
                    elif getattr(tk, 'is_param_array', False):
                        code = "PUSH $" + str(tk.start_pos) + "\n"
                    else:
                        code = "MOV EAX EBP\n"
                        code += "ADD EAX " + str(tk.start_pos) + "\n"
                        code += "PUSH EAX\n"
                else:
                    addr = _addr(area_tree, oplist[0])
                    code = "PUSH " + addr + "\n"
            # 递归部分
            if len(codelist) > 1:
                code += codelist[1]
        else:
            for i in codelist:
                code += i
        pass

    elif name == "SWITCH":
        # switch(expr) { case ... }
        # oplist[0] = 被比较的变量
        # codelist: [OPN_code(空), CASELIST_code]，CASELIST在最后
        switch_var = _addr(area_tree, oplist[0])
        case_code = codelist[-1] if codelist else ""
        # 替换占位符为实际变量地址
        case_code = case_code.replace("SWITCH_VAR", switch_var)
        code = case_code

    elif name == "CASELIST":
        if "case" in rule and "$CASELIST$" in rule:
            # case EMPTY CONST : SENTENCE CASELIST → 链式递归
            # codelist: [EMPTY_code, CONST_code, SENTENCE_code, CASELIST_code]
            # 由于保留空占位符，SENTENCE和CASELIST分别在最后两个位置
            case_val = oplist[0]
            # 找到有效的 SENTENCE 和 CASELIST 代码
            # SENTENCE 是倒数第二个，CASELIST 是倒数第一个
            body_code = codelist[-2] if len(codelist) >= 2 else ""
            rest_code = codelist[-1] if len(codelist) >= 1 else ""
            body_lines = len([l for l in body_code.split("\n") if l.strip()])
            rest_lines = len([l for l in rest_code.split("\n") if l.strip()])
            has_break = "JMP BREAK_PLACEHOLDER" in body_code
            if has_break:
                body_code_clean = body_code.replace("JMP BREAK_PLACEHOLDER\n", "")
                body_lines_clean = len([l for l in body_code_clean.split("\n") if l.strip()])
                code = "EQUAL SWITCH_VAR " + case_val + "\n"
                code += "JPIF " + str(body_lines_clean + 2) + "\n"
                code += body_code_clean
                code += "JMP " + str(rest_lines + 1) + "\n"
                code += rest_code
            else:
                code = "EQUAL SWITCH_VAR " + case_val + "\n"
                code += "JPIF " + str(body_lines + 1) + "\n"
                code += body_code
                code += rest_code
        elif "case" in rule and "$CASELIST$" not in rule:
            # case EMPTY CONST : SENTENCE → 最后一个 case
            case_val = oplist[0]
            body_code = codelist[-1] if codelist else ""
            body_code = body_code.replace("JMP BREAK_PLACEHOLDER\n", "")
            body_lines = len([l for l in body_code.split("\n") if l.strip()])
            code = "EQUAL SWITCH_VAR " + case_val + "\n"
            code += "JPIF " + str(body_lines + 1) + "\n"
            code += body_code
        elif "default" in rule:
            body_code = codelist[-1] if codelist else ""
            body_code = body_code.replace("JMP BREAK_PLACEHOLDER\n", "")
            code = body_code
        else:
            for i in codelist:
                code += i

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
        # 收集方法的 IR 代码（在 codelist 中）
        for i in codelist:
            if i.strip() and i.strip() != "NOP":
                code += i

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
