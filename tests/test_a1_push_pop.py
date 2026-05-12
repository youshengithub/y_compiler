"""A1: PUSH/POP 是否正确把值放到 memory[memory[ESP]] 而不是 memory[ESP] 自身。"""
from harness import run_ir, reg


def test_push_pop():
    # 把 EBP 设到 0，ESP 设到 10（栈底）。然后 PUSH 42 / PUSH 7，应当：
    # memory[10] = 42, memory[11] = 7, ESP = 12
    # POP EAX → EAX 槽 = 7，ESP = 11
    # POP EBX → EBX 槽 = 42，ESP = 10
    ir = """
    MOV EBP 0
    MOV ESP 10
    PUSH 42
    PUSH 7
    POP EAX
    POP EBX
    """
    r, _ = run_ir(ir)
    sp = reg(r, "ESP")
    eax = reg(r, "EAX")
    ebx = reg(r, "EBX")
    # 期望：EAX=7（先 POP 出栈顶 7），EBX=42（再 POP 出 42），ESP 回到 10
    print(f"[A1] ESP={sp}, EAX={eax}, EBX={ebx}, mem[10]={r.memory[10]}, mem[11]={r.memory[11]}")
    assert eax == 7, f"POP 顺序 1 应得 7，实际 {eax}"
    assert ebx == 42, f"POP 顺序 2 应得 42，实际 {ebx}"
    assert sp == 10, f"ESP 应回到 10，实际 {sp}"
    assert r.memory[10] == 42 and r.memory[11] == 7, "栈区残留值应为压栈数据"


if __name__ == "__main__":
    test_push_pop()
    print("A1 PASS")
