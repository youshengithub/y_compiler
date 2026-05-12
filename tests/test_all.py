#!/usr/bin/env python3
"""
=== 全面回归测试 ===

本文件覆盖：
  Part 1: 所有 IR 指令（runner 级别直接测试）
  Part 2: 编译器翻译模块功能测试
  Part 3: 端到端集成测试（源码→编译→运行→验证输出）

运行方式：
  cd y_compiler
  python tests/test_all.py
"""
import os
import sys
import io
import contextlib
import traceback

# ============ 环境准备 ============
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.harness import run_ir, reg, compile_and_run, REG_SLOTS

# ============ 测试框架 ============
_passed = 0
_failed = 0
_errors = []


def check(name, condition, msg=""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  ✅ {name}")
    else:
        _failed += 1
        detail = f"  ❌ {name}: {msg}" if msg else f"  ❌ {name}"
        print(detail)
        _errors.append(detail)


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ================================================================
#                    PART 1: IR 指令级测试
# ================================================================

def test_ir_alloc():
    """ALLOC: 分配内存，ESP 应增长"""
    r, _ = run_ir("ALLOC 5")
    check("ALLOC 5 → ESP=6", reg(r, "ESP") == 6)  # 初始 ESP=0, ALLOC 5 → ESP=5+1=6? 实际 ALLOC 只是设ESP=op1+1
    # 实际行为：ALLOC n → ESP = n + 1（这是runner实现）
    # 不对，看runner源码：self.memory[REGS["ESP"]]=op1+1  op1=5 → ESP=6
    check("ALLOC 5 → ESP=6", reg(r, "ESP") == 6)


def test_ir_mov():
    """MOV: 数据传送"""
    # MOV 立即数
    r, _ = run_ir("ALLOC 3\nMOV $0 42")
    check("MOV $0 42", r.memory[r.memory[-3] + 0] == 42)  # $0 = memory[EBP+0]
    # MOV 寄存器间
    r, _ = run_ir("ALLOC 2\nMOV $0 99\nMOV $1 $0")
    ebp = r.memory[-3]
    check("MOV $1 $0 (内存复制)", r.memory[ebp + 1] == 99)


def test_ir_add():
    """ADD: 加法"""
    r, _ = run_ir("ALLOC 2\nMOV $0 10\nADD $0 5")
    ebp = r.memory[-3]
    check("ADD $0 5 → 15", r.memory[ebp + 0] == 15)

    r, _ = run_ir("ALLOC 2\nMOV $0 10\nMOV $1 7\nADD $0 $1")
    ebp = r.memory[-3]
    check("ADD $0 $1 → 17", r.memory[ebp + 0] == 17)


def test_ir_sub():
    """SUB: 减法"""
    r, _ = run_ir("ALLOC 2\nMOV $0 20\nSUB $0 8")
    ebp = r.memory[-3]
    check("SUB $0 8 → 12", r.memory[ebp + 0] == 12)

    r, _ = run_ir("ALLOC 2\nMOV $0 20\nMOV $1 3\nSUB $0 $1")
    ebp = r.memory[-3]
    check("SUB $0 $1 → 17", r.memory[ebp + 0] == 17)


def test_ir_mul():
    """MUL: 乘法"""
    r, _ = run_ir("ALLOC 2\nMOV $0 6\nMUL $0 7")
    ebp = r.memory[-3]
    check("MUL $0 7 → 42", r.memory[ebp + 0] == 42)

    r, _ = run_ir("ALLOC 2\nMOV $0 3\nMOV $1 9\nMUL $0 $1")
    ebp = r.memory[-3]
    check("MUL $0 $1 → 27", r.memory[ebp + 0] == 27)


def test_ir_div():
    """DIV: 除法"""
    r, _ = run_ir("ALLOC 2\nMOV $0 20\nDIV $0 4")
    ebp = r.memory[-3]
    check("DIV $0 4 → 5", r.memory[ebp + 0] == 5.0)

    r, _ = run_ir("ALLOC 2\nMOV $0 15\nMOV $1 3\nDIV $0 $1")
    ebp = r.memory[-3]
    check("DIV $0 $1 → 5", r.memory[ebp + 0] == 5.0)


def test_ir_mod():
    """MOD: 取模"""
    r, _ = run_ir("ALLOC 2\nMOV $0 7\nMOD $0 3")
    ebp = r.memory[-3]
    check("MOD $0 3 → 1 (7%3)", r.memory[ebp + 0] == 1)

    r, _ = run_ir("ALLOC 2\nMOV $0 10\nMOV $1 4\nMOD $0 $1")
    ebp = r.memory[-3]
    check("MOD $0 $1 → 2 (10%4)", r.memory[ebp + 0] == 2)


def test_ir_and():
    """AND: 位与"""
    r, _ = run_ir("ALLOC 2\nMOV $0 12\nAND $0 10")  # 1100 & 1010 = 1000 = 8
    ebp = r.memory[-3]
    check("AND $0 10 → 8 (12&10)", r.memory[ebp + 0] == 8)


def test_ir_or():
    """OR: 位或"""
    r, _ = run_ir("ALLOC 2\nMOV $0 12\nOR $0 3")  # 1100 | 0011 = 1111 = 15
    ebp = r.memory[-3]
    check("OR $0 3 → 15 (12|3)", r.memory[ebp + 0] == 15)


def test_ir_xor():
    """XOR: 位异或"""
    r, _ = run_ir("ALLOC 2\nMOV $0 15\nXOR $0 9")  # 1111 ^ 1001 = 0110 = 6
    ebp = r.memory[-3]
    check("XOR $0 9 → 6 (15^9)", r.memory[ebp + 0] == 6)


def test_ir_not():
    """NOT: 位取反"""
    r, _ = run_ir("ALLOC 2\nMOV $0 0\nNOT $0 0")  # ~0 = -1
    ebp = r.memory[-3]
    check("NOT $0 0 → -1 (~0)", r.memory[ebp + 0] == -1)

    r, _ = run_ir("ALLOC 2\nMOV $0 0\nNOT $0 5")  # ~5 = -6
    ebp = r.memory[-3]
    check("NOT $0 5 → -6 (~5)", r.memory[ebp + 0] == -6)


def test_ir_lea():
    """LEA: 取地址"""
    r, _ = run_ir("ALLOC 5\nLEA $0 $3")
    ebp = r.memory[-3]
    # LEA $0 $3 → memory[$0位置] = $3的地址值(即ebp+3)
    check("LEA $0 $3", r.memory[ebp + 0] == ebp + 3)


def test_ir_sea():
    """SEA: 间接存储 (store via address)"""
    r, _ = run_ir("ALLOC 5\nMOV $0 3\nSEA $0 99")
    # SEA $0 99 → memory[memory[ebp+0]] = 99 → memory[3] = 99
    check("SEA $0 99 → memory[3]=99", r.memory[3] == 99)


def test_ir_push_pop():
    """PUSH/POP: 栈操作"""
    r, _ = run_ir("ALLOC 10\nMOV $0 42\nMOV $1 7\nPUSH $1\nPUSH $0\nPOP $2\nPOP $3")
    ebp = r.memory[-3]
    check("PUSH/POP: LIFO 栈", r.memory[ebp + 2] == 42 and r.memory[ebp + 3] == 7)
    check("PUSH/POP: ESP 恢复", reg(r, "ESP") == 11)  # ALLOC 10 → ESP=11, push+2 pop-2


def test_ir_greater():
    """GREATER: 大于比较"""
    # GREATER 比较后 EFG = not(op1 > op2)
    r, _ = run_ir("ALLOC 2\nMOV $0 5\nMOV $1 3\nGREATER $0 $1")
    check("GREATER 5>3 → EFG=False(条件成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 3\nMOV $1 5\nGREATER $0 $1")
    check("GREATER 3>5 → EFG=True(条件不成立)", reg(r, "EFG") == True)


def test_ir_less():
    """LESS: 小于比较"""
    r, _ = run_ir("ALLOC 2\nMOV $0 3\nMOV $1 5\nLESS $0 $1")
    check("LESS 3<5 → EFG=False(条件成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 5\nMOV $1 3\nLESS $0 $1")
    check("LESS 5<3 → EFG=True(条件不成立)", reg(r, "EFG") == True)


def test_ir_equal():
    """EQUAL: 相等比较"""
    r, _ = run_ir("ALLOC 2\nMOV $0 7\nEQUAL $0 7")
    check("EQUAL 7==7 → EFG=False(条件成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 7\nEQUAL $0 8")
    check("EQUAL 7==8 → EFG=True(条件不成立)", reg(r, "EFG") == True)


def test_ir_le():
    """LE: 小于等于"""
    r, _ = run_ir("ALLOC 2\nMOV $0 5\nLE $0 5")
    check("LE 5<=5 → EFG=False(成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 3\nLE $0 5")
    check("LE 3<=5 → EFG=False(成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 7\nLE $0 5")
    check("LE 7<=5 → EFG=True(不成立)", reg(r, "EFG") == True)


def test_ir_ge():
    """GE: 大于等于"""
    r, _ = run_ir("ALLOC 2\nMOV $0 5\nGE $0 5")
    check("GE 5>=5 → EFG=False(成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 7\nGE $0 5")
    check("GE 7>=5 → EFG=False(成立)", reg(r, "EFG") == False)

    r, _ = run_ir("ALLOC 2\nMOV $0 3\nGE $0 5")
    check("GE 3>=5 → EFG=True(不成立)", reg(r, "EFG") == True)


def test_ir_rf():
    """RF: 翻转 EFG"""
    r, _ = run_ir("ALLOC 2\nMOV $0 5\nEQUAL $0 5\nRF")
    # EQUAL 5==5 → EFG=False, RF → EFG=True
    check("RF 翻转 EFG", reg(r, "EFG") == True)


def test_ir_jmp():
    """JMP: 无条件跳转"""
    # JMP 2 → 跳过下一条指令
    r, _ = run_ir("ALLOC 2\nMOV $0 1\nJMP 2\nMOV $0 99\nNOP")
    ebp = r.memory[-3]
    check("JMP 跳过 → $0=1(不是99)", r.memory[ebp + 0] == 1)


def test_ir_jpif():
    """JPIF: 条件为真时跳转"""
    # EFG=True 时跳转
    r, _ = run_ir("ALLOC 2\nMOV $0 1\nEQUAL $0 99\nJPIF 2\nMOV $0 55\nNOP")
    ebp = r.memory[-3]
    # EQUAL 1==99 → EFG=True(不等) → JPIF跳转 → $0保持1
    check("JPIF(EFG=True) 跳转", r.memory[ebp + 0] == 1)

    # EFG=False 时不跳转
    r, _ = run_ir("ALLOC 2\nMOV $0 1\nEQUAL $0 1\nJPIF 2\nMOV $0 55\nNOP")
    ebp = r.memory[-3]
    check("JPIF(EFG=False) 不跳转", r.memory[ebp + 0] == 55)


def test_ir_jpnif():
    """JPNIF: 条件为假时跳转"""
    # EFG=False 时跳转
    r, _ = run_ir("ALLOC 2\nMOV $0 1\nEQUAL $0 1\nJPNIF 2\nMOV $0 55\nNOP")
    ebp = r.memory[-3]
    check("JPNIF(EFG=False) 跳转", r.memory[ebp + 0] == 1)


def test_ir_out():
    """OUT: 输出字符"""
    r, out = run_ir("ALLOC 2\nMOV $0 65\nOUT $0", capture_stdout=True)
    # 65 = 'A'
    check("OUT 65 → 'A'", 'A' in out)

    r, out = run_ir("OUT 66", capture_stdout=True)
    check("OUT 66 → 'B'", 'B' in out)


def test_ir_nop():
    """NOP: 空操作"""
    r, _ = run_ir("ALLOC 2\nMOV $0 42\nNOP\nNOP\nNOP")
    ebp = r.memory[-3]
    check("NOP 不影响状态", r.memory[ebp + 0] == 42)


def test_ir_negative_jmp():
    """JMP 负偏移: 实现循环"""
    # 简单循环: $0从0加到3
    ir = """
    ALLOC 2
    MOV $0 0
    ADD $0 1
    LESS $0 3
    JPIF -2
    """
    # LESS $0 3: 如果 $0<3 → EFG=False, 不跳; 如果 $0>=3 → EFG=True, 跳
    # 等等，JPIF在EFG=True时跳...这里是往回跳，实现循环
    # 修正：LESS $0 3 → EFG = not($0<3). 当$0<3时EFG=False不跳;当$0>=3时EFG=True跳
    # 但JPIF -2表示向前跳2行...这会跳回ADD指令
    # 让我重新设计：用 GREATER 实现 while($0 < 3) 循环
    ir = """
    ALLOC 2
    MOV $0 0
    MOV $1 0
    ADD $0 1
    GREATER $0 3
    JPIF -2
    """
    # GREATER $0 3: EFG = not($0>3). 当$0<=3,EFG=True → JPIF跳回ADD → 继续循环
    # 当$0>3, EFG=False → 不跳 → 结束
    r, _ = run_ir(ir)
    ebp = r.memory[-3]
    check("负偏移JMP循环: $0=4(>3时退出)", r.memory[ebp + 0] == 4)


# ================================================================
#                    PART 2: 编译器翻译模块测试
# ================================================================

def test_compiler_dim():
    """DIM: 变量声明"""
    from src.token_ana import y_token, varea, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))
    area.append_var(y_token(token_type.structure, "double", 1))

    code, area = Compile_tree.Complie("DIM", "$TYPE$$EMPTY$$TOKEN$", ["int", "x"], [], area)
    tk = area.find_token("x")
    check("DIM int x: token注册", tk is not None)
    check("DIM int x: kind=variable", tk.kind == token_type.variable)
    check("DIM int x: type=int", tk.type == "int")
    check("DIM int x: start_pos=int", isinstance(tk.start_pos, int))


def test_compiler_dim_string():
    """DIM 带字符串初值: start_pos 应为 int"""
    from src.token_ana import y_token, varea, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))

    # 先占位
    Compile_tree.Complie("DIM", "$TYPE$$EMPTY$$TOKEN$", ["int", "x"], [], area)

    code, area = Compile_tree.Complie("DIM", "$TYPE$$EMPTY$$TOKEN$=$STRING$", ["int", "s", "AB"], [], area)
    tk = area.find_token("s")
    check("DIM+STRING: token注册", tk is not None)
    check("DIM+STRING: start_pos是int", isinstance(tk.start_pos, int))
    check("DIM+STRING: MOV指令正确", "MOV" in code)


def test_compiler_if_no_else():
    """IF: 纯if语句（无else）不崩溃"""
    from src.token_ana import varea, y_token, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))

    # 模拟 if(cond){body} — codelist只有2个元素
    judge_code = "EQUAL $0 1\n"
    body_code = "MOV $1 42\n"

    try:
        code, area = Compile_tree.Complie("IF", "if($JUDGE$)$AREA$", [], [judge_code, body_code], area)
        check("纯IF(无else)不崩溃", True)
        check("纯IF生成JPIF", "JPIF" in code)
        check("纯IF不含JMP(无else跳转)", "JMP" not in code)
    except IndexError as e:
        check("纯IF(无else)不崩溃", False, f"IndexError: {e}")


def test_compiler_if_else():
    """IF: if-else 仍正确"""
    from src.token_ana import varea, y_token, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))

    judge_code = "EQUAL $0 1\n"
    body_code = "MOV $1 42\n"
    else_code = "MOV $1 99\n"

    code, area = Compile_tree.Complie("IF", "if($JUDGE$)$AREA$else$AREA$", [], [judge_code, body_code, else_code], area)
    check("IF-ELSE含JPIF", "JPIF" in code)
    check("IF-ELSE含JMP", "JMP" in code)


def test_compiler_empty_area():
    """AREA: 空代码块{}生成NOP而非NOPs"""
    from src.token_ana import varea, y_token, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))

    code, area = Compile_tree.Complie("AREA", "$AREA_S$$AREA_E$", [], [], area)
    check("空AREA生成NOP", "NOP" in code)
    check("空AREA不含NOPs", "NOPs" not in code)


def test_compiler_arithmetic():
    """算术节点: ADD/SUB/MUL/DIV/MOD"""
    from src.token_ana import varea, y_token, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))
    t = y_token()
    t.set_as_variable("a", 1, "int", 0, [])
    area.append_var(t, 1)
    t2 = y_token()
    t2.set_as_variable("b", 1, "int", 1, [])
    area.append_var(t2, 1)

    # ADD $OPN$+$OPN$
    code, _ = Compile_tree.Complie("ADD", "$OPN$+$OPN$", ["a", "b"], [], area)
    check("ADD OPN+OPN 含 MOV + ADD", "MOV EAX" in code and "ADD EAX" in code)

    # SUB $OPN$-$OPN$
    code, _ = Compile_tree.Complie("SUB", "$OPN$-$OPN$", ["a", "b"], [], area)
    check("SUB OPN-OPN 含 SUB", "SUB EAX" in code)

    # MUL $OPN$*$OPN$
    code, _ = Compile_tree.Complie("MUL", "$OPN$*$OPN$", ["a", "b"], [], area)
    check("MUL OPN*OPN 含 MUL", "MUL EAX" in code)

    # MOD $OPN$%$OPN$
    code, _ = Compile_tree.Complie("MOD", "$OPN$%$OPN$", ["a", "b"], [], area)
    check("MOD OPN%OPN 含 MOD", "MOD EAX" in code)


def test_compiler_judge():
    """JUDGE: 比较运算符翻译"""
    from src.token_ana import varea, y_token, token_type
    import src.Compile_tree as Compile_tree

    area = varea(None, True, "Main")
    area.append_var(y_token(token_type.structure, "int", 1))
    t = y_token()
    t.set_as_variable("x", 1, "int", 0, [])
    area.append_var(t, 1)

    # <= 优先于 <
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$<=$OPN$", ["x", "5"], [], area)
    check("JUDGE <= → LE指令", "LE" in code)

    # >= 优先于 >
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$>=$OPN$", ["x", "5"], [], area)
    check("JUDGE >= → GE指令", "GE" in code)

    # ==
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$==$OPN$", ["x", "5"], [], area)
    check("JUDGE == → EQUAL指令", "EQUAL" in code)

    # !=
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$!=$OPN$", ["x", "5"], [], area)
    check("JUDGE != → EQUAL+RF", "EQUAL" in code and "RF" in code)

    # <
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$<$OPN$", ["x", "5"], [], area)
    check("JUDGE < → LESS指令", "LESS" in code)

    # >
    code, _ = Compile_tree.Complie("JUDGE", "$OPN$>$OPN$", ["x", "5"], [], area)
    check("JUDGE > → GREATER指令", "GREATER" in code)


def test_token_kind_type():
    """y_token: kind 和 type 字段分离正确"""
    from src.token_ana import y_token, token_type

    t = y_token()
    t.set_as_variable("myvar", 1, "int", 0, [])
    check("variable.kind = token_type.variable", t.kind == token_type.variable)
    check("variable.type = 'int'", t.type == "int")

    t2 = y_token(token_type.structure, "double", 1)
    check("structure.kind = token_type.structure", t2.kind == token_type.structure)

    t3 = y_token()
    t3.set_as_function("int", "myfunc", ["int", "double"])
    check("function.kind = token_type.function", t3.kind == token_type.function)
    check("function.type = 'int'(返回类型)", t3.type == "int")


def test_preprocesser():
    """预处理器: #define, #undefine, #include(错误处理), 注释, 空格"""
    from src.preprocesser import Preprocesser

    p = Preprocesser()

    # #define
    src = "#define X 42\nint a=X;"
    out = p.process(src)
    check("#define 替换", "42" in out)

    # #undefine
    src2 = "#define Y 10\n#undefine Y\nint b=Y;"
    out2 = p.process(src2)
    check("#undefine 取消替换", "Y" in out2 and "10" not in out2.split("Y")[1:][0] if "Y" in out2 else False)

    # #include 不存在的文件不崩溃
    src3 = '#include<__nonexist__.txt>\nint c;'
    try:
        out3 = p.process(src3)
        check("#include 不存在文件不崩溃", True)
    except Exception as e:
        check("#include 不存在文件不崩溃", False, str(e))

    # 注释移除
    src4 = "int a;//this is comment\nint b;"
    out4 = p.process_note(src4)
    check("注释移除 //", "comment" not in out4)


def test_postprocesser():
    """后处理器: 标签替换、JMP偏移"""
    from src.postprocesser import Postprocesser

    p = Postprocesser()

    # 注释移除
    code = "MOV $0 1//comment\nADD $0 2\n"
    out = p.process_note(code)
    check("postprocesser 注释移除", "comment" not in out)

    # ALLOC @label → NOP + JMP @label → 偏移
    code2 = "ALLOC @myfunc\nMOV $0 1\nJMP @myfunc\nNOP\n"
    out2 = p.process(code2)
    check("ALLOC @label → NOP", "NOP" in out2)
    check("JMP @label → 数字偏移", "@myfunc" not in out2)


# ================================================================
#                    PART 3: 端到端集成测试
# ================================================================

def test_e2e_simple_assignment():
    """端到端: 简单赋值与输出"""
    r, out = compile_and_run("int a;a=65;out(a);")
    check("E2E 赋值输出: out(65)='A'", 'A' in out)


def test_e2e_arithmetic():
    """端到端: 四则运算"""
    r, out = compile_and_run("int a;int b;int c;a=7;b=3;c=a+b;c=c+48;out(c);")
    # 7+3=10 → 10+48=58 → chr(58)=':'
    check("E2E 加法: 7+3+48=58→':'", ':' in out)

    r, out = compile_and_run("int a;int b;int c;a=9;b=4;c=a-b;c=c+48;out(c);")
    # 9-4=5 → 53 → '5'
    check("E2E 减法: 9-4+48=53→'5'", '5' in out)

    r, out = compile_and_run("int a;int b;int c;a=3;b=4;c=a*b;c=c+48;out(c);")
    # 3*4=12 → 60 → '<'
    check("E2E 乘法: 3*4+48=60→'<'", '<' in out)


def test_e2e_mod():
    """端到端: 取模运算"""
    r, out = compile_and_run("int a;int b;int c;a=7;b=3;c=a%b;c=c+48;out(c);")
    # 7%3=1 → 49 → '1'
    check("E2E 取模: 7%3+48=49→'1'", '1' in out)


def test_e2e_if():
    """端到端: 纯if语句"""
    r, out = compile_and_run("int a;int b;a=1;b=48;if(a==1){b=65;}out(b);")
    check("E2E 纯if(true): out='A'", 'A' in out)

    r, out = compile_and_run("int a;int b;a=2;b=66;if(a==1){b=65;}out(b);")
    check("E2E 纯if(false): out='B'", 'B' in out)


def test_e2e_if_else():
    """端到端: if-else"""
    r, out = compile_and_run("int a;int b;a=1;if(a==1){b=65;}else{b=66;}out(b);")
    check("E2E if-else(true): out='A'", 'A' in out)

    r, out = compile_and_run("int a;int b;a=2;if(a==1){b=65;}else{b=66;}out(b);")
    check("E2E if-else(false): out='B'", 'B' in out)


def test_e2e_while():
    """端到端: while循环"""
    # 循环加到65输出A
    src = "int a;a=0;while(a<65){a=a+1;}out(a);"
    r, out = compile_and_run(src)
    check("E2E while循环: 0→65 输出'A'", 'A' in out)


def test_e2e_for():
    """端到端: for循环"""
    src = "int a;int b;b=0;for(a=0;a<5;a=a+1){b=b+1;}b=b+48;out(b);"
    # 循环5次 b=5 → 53 → '5'
    r, out = compile_and_run(src)
    check("E2E for循环: 5次→'5'", '5' in out)


def test_e2e_do_while():
    """端到端: do-while循环"""
    src = "int a;a=65;do{out(a);a=a+1;}while(a<68);"
    # 输出 A B C
    r, out = compile_and_run(src)
    check("E2E do-while: 输出含'A'", 'A' in out)
    check("E2E do-while: 输出含'C'", 'C' in out)


def test_e2e_comparison():
    """端到端: 各种比较运算符"""
    # <=
    r, out = compile_and_run("int a;a=65;if(a<=65){out(a);}else{out(66);}")
    check("E2E <=: 65<=65 → 'A'", 'A' in out)

    # >=
    r, out = compile_and_run("int a;a=65;if(a>=65){out(a);}else{out(66);}")
    check("E2E >=: 65>=65 → 'A'", 'A' in out)

    # !=
    r, out = compile_and_run("int a;a=65;if(a!=66){out(a);}else{out(66);}")
    check("E2E !=: 65!=66 → 'A'", 'A' in out)


def test_e2e_nested_if():
    """端到端: 嵌套if"""
    src = "int a;int b;a=1;b=2;if(a==1){if(b==2){out(65);}else{out(66);}}else{out(67);}"
    r, out = compile_and_run(src)
    check("E2E 嵌套if: 输出'A'", 'A' in out)


def test_e2e_bitwise():
    """端到端: 位运算"""
    # 12 & 10 = 8 → 8+48=56 → '8'
    r, out = compile_and_run("int a;int b;int c;a=12;b=10;c=a&b;c=c+48;out(c);")
    check("E2E AND: 12&10=8→'8'", '8' in out)

    # 12 | 3 = 15 → NOT用不了直接out... 15+48=63 → '?'
    r, out = compile_and_run("int a;int b;int c;a=12;b=3;c=a|b;c=c+48;out(c);")
    check("E2E OR: 12|3=15→'?'", '?' in out)


def test_e2e_asm():
    """端到端: 内联汇编 asm()"""
    src = 'int a;a=0;asm("MOV $0 65\\n");out(a);'
    r, out = compile_and_run(src)
    check("E2E asm(): 内联MOV → out='A'", 'A' in out)


# ================================================================
#                          主执行
# ================================================================

def main():
    section("Part 1: IR 指令级测试")
    test_ir_alloc()
    test_ir_mov()
    test_ir_add()
    test_ir_sub()
    test_ir_mul()
    test_ir_div()
    test_ir_mod()
    test_ir_and()
    test_ir_or()
    test_ir_xor()
    test_ir_not()
    test_ir_lea()
    test_ir_sea()
    test_ir_push_pop()
    test_ir_greater()
    test_ir_less()
    test_ir_equal()
    test_ir_le()
    test_ir_ge()
    test_ir_rf()
    test_ir_jmp()
    test_ir_jpif()
    test_ir_jpnif()
    test_ir_out()
    test_ir_nop()
    test_ir_negative_jmp()

    section("Part 2: 编译器翻译模块测试")
    test_compiler_dim()
    test_compiler_dim_string()
    test_compiler_if_no_else()
    test_compiler_if_else()
    test_compiler_empty_area()
    test_compiler_arithmetic()
    test_compiler_judge()
    test_token_kind_type()
    test_preprocesser()
    test_postprocesser()

    section("Part 3: 端到端集成测试")
    test_e2e_simple_assignment()
    test_e2e_arithmetic()
    test_e2e_mod()
    test_e2e_if()
    test_e2e_if_else()
    test_e2e_while()
    test_e2e_for()
    test_e2e_do_while()
    test_e2e_comparison()
    test_e2e_nested_if()
    test_e2e_bitwise()
    test_e2e_asm()

    # 总结
    section("测试结果汇总")
    total = _passed + _failed
    print(f"\n  总计: {total} | 通过: {_passed} ✅ | 失败: {_failed} ❌")
    if _errors:
        print("\n  失败项目:")
        for e in _errors:
            print(f"    {e}")
    print()

    if _failed > 0:
        sys.exit(1)
    else:
        print("  🎉 ALL TESTS PASSED!\n")


if __name__ == "__main__":
    main()
