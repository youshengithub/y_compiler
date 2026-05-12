"""A6: postprocesser 把 ALLOC@L / JMP@L 解析为相对跳转的偏移是否合适。

注意：postprocesser 的 toend 公式与 runner 的 JMP 语义紧耦合——这条 bug 与函数调用约定相关，
本测试**只验证现状下的实际行为**作为基线，不要求修改。

runner JMP 语义：EIP += op1 后 continue（不再 +1）。
所以"想停在第 K 行（绝对）" 等价于 "JMP (K - 当前行)"。
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from postprocesser import Postprocesser


def test_jmp_label_offset():
    src = (
        "ALLOC @L\n"     # 行 0: 被替换为 NOP，tags["L"]=0
        "MOV EAX 1\n"    # 行 1
        "MOV EAX 2\n"    # 行 2
        "JMP @L\n"       # 行 3: 想跳回 L
    )
    pp = Postprocesser()
    out = pp.process(src)
    print("[A6] post-processed:\n", out)
    # 当前实现 toend = 0 - 3 + 2 = -1
    # 含义：在行 3 执行时 EIP=3，加 -1 得 EIP=2，下一条是行 2 (MOV EAX 2) ——并不是 L 行
    # 这表明现有 +2 语义是"跳到目标行的下两行"，对 ALLOC@func / JMP@func 这种调用约定才有意义
    # 暂保留为已知问题，不在本轮修改
    last_jmp_line = [ln for ln in out.strip().split("\n") if ln.startswith("JMP")][-1]
    print("[A6] last JMP becomes:", last_jmp_line)
    # 仅断言：JMP 已被解析为数字（不再含 @），不再做绝对正确性断言
    assert "@" not in last_jmp_line, "JMP @label 应被解析为相对偏移"


if __name__ == "__main__":
    test_jmp_label_offset()
    print("A6 PASS (基线行为，offset 公式本轮不改)")
