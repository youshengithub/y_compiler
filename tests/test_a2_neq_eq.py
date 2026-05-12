"""A2: 验证 != 与 == 在 IF 语境下的真实跳转行为是否符合预期。

经过白盒推导：
  EQUAL a b 在 runner 中实际执行 EFG = (a!=b)
  !=  对应  EQUAL a b / RF  → EFG = (a==b)
  ==  对应  EQUAL a b       → EFG = (a!=b)

IF 在 Compile_tree 中是 "JPIF 跳过 then 段"，所以 EFG=True ⇒ 不进 then。
=> ==  : a==b → EFG=False → 进 then  ✅
=> !=  : a==b → EFG=True  → 不进 then ✅

因此 BUG 4 实为误报。本测试仅作为回归保护，证明 != 与 == 的 IR 不会导致 IF 行为错位。
"""
from harness import run_ir, reg


def _run_eq_branch(op, a, b):
    """模拟一个 IF: 若 a OP b 进 then(写 1 到 mem[10]) else 写 2 到 mem[10]。"""
    # JPIF 跳过 then 段（占 1 行 MOV mem[10] 1），然后 JMP 跳过 else 段（占 1 行）
    # then: MOV $5 1   else: MOV $5 2  （用 mem[5]=$0:5= 5+EBP, EBP=0）
    if op == "==":
        cmp_line = f"EQUAL {a} {b}"
    elif op == "!=":
        cmp_line = f"EQUAL {a} {b}\nRF"
    else:
        raise ValueError(op)
    # 计算 JPIF/JMP 偏移：runner 的 JPIF/JMP 语义是 EIP+=op1 后 continue（不再 +1）
    # 行号布局：
    #   [0] MOV EBP 0
    #   [1] MOV ESP 100
    #   [2] EQUAL ...    （+ 可选 RF 占行 [3]）
    #   [N] JPIF X       （N=3 或 4） — 想跳到 [end] 即 EIP=N+3 → X=3
    #   [N+1] MOV $5 1
    #   [N+2] JMP Y      — 想跳过 else（1行）+ JMP 自身后停在 end → Y=2
    #   [N+3] MOV $5 2
    ir = f"""
    MOV EBP 0
    MOV ESP 100
    {cmp_line}
    JPIF 3
    MOV $5 1
    JMP 2
    MOV $5 2
    """
    r, _ = run_ir(ir)
    return r.memory[5]


def test_eq_neq():
    # ==
    assert _run_eq_branch("==", 3, 3) == 1, "3==3 应进 then"
    assert _run_eq_branch("==", 3, 4) == 2, "3==4 应进 else"
    # !=
    assert _run_eq_branch("!=", 3, 3) == 2, "3!=3 应进 else"
    assert _run_eq_branch("!=", 3, 4) == 1, "3!=4 应进 then"


if __name__ == "__main__":
    test_eq_neq()
    print("A2 PASS (BUG 4 撤回 - != 与 == 实际语义正确)")
