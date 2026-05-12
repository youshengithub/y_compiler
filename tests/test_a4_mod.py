"""A4: MOD $OP$%$OP$ 的左右子树次序。a%b 应等于 a - (a/b)*b。

我们用最小代码模拟编译器送进 Complie 的 codelist，并用 runner 跑出来比较。
"""
from harness import run_ir, reg
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from Compile_tree import Complie
from token_ana import varea


def _emit_mod_op_op(left_val, right_val):
    """模拟左、右子树都是 $OP$（求值结果都在 EAX）。
    我们用 codelist 提供的"子树代码"分别把 left_val、right_val 写进 EAX。"""
    area = varea(None, True, "Main")
    code_left = f"MOV EAX {left_val}\n"
    code_right = f"MOV EAX {right_val}\n"
    code, _ = Complie("AND" if False else "MOD",  # name 必须是 MOD 走到那段
                      "$OP$%$OP$",
                      [],
                      [code_left, code_right],
                      area)
    return code


def test_mod_op_op():
    code = _emit_mod_op_op(7, 3)
    print("[A4] generated IR:\n", code)
    # 加一个写到 mem[5] 的 epilogue，便于断言
    full = "MOV EBP 0\nMOV ESP 100\n" + code + "MOV $5 EAX\n"
    r, _ = run_ir(full)
    print("[A4] mem[5] =", r.memory[5])
    assert r.memory[5] == 7 % 3, f"7 % 3 应=1，实际 {r.memory[5]}"


def test_mod_more():
    # 再来 10 % 4 = 2
    full = "MOV EBP 0\nMOV ESP 100\n" + _emit_mod_op_op(10, 4) + "MOV $5 EAX\n"
    r, _ = run_ir(full)
    assert r.memory[5] == 10 % 4, f"10 % 4 应=2，实际 {r.memory[5]}"
    # 25 % 7 = 4
    full = "MOV EBP 0\nMOV ESP 100\n" + _emit_mod_op_op(25, 7) + "MOV $5 EAX\n"
    r, _ = run_ir(full)
    assert r.memory[5] == 25 % 7, f"25 % 7 应=4，实际 {r.memory[5]}"


if __name__ == "__main__":
    test_mod_op_op()
    test_mod_more()
    print("A4 PASS")
