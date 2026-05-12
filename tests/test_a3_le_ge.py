"""A3: <= 和 >= 应当与 < / > 不同。修复后通过 LE / GE 指令实现。"""
from harness import run_ir, reg

# 复用 A2 中的 IF 测试模板：cmp_line 决定 EFG，后接相同 IF 骨架
def _run_with_cmp(cmp_line):
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


def test_le_runner():
    # 修复后 runner 应支持 LE / GE 指令；极性沿用 LESS/GREATER：
    # LESS 末尾有 "EFG = not EFG"，所以 LESS a b → EFG = not (a<b)
    # 推广：LE  a b → EFG = not (a<=b)；EFG=False ⇒ JPIF 不跳 ⇒ 进 then
    # 即 a<=b 进 then(=1)，否则进 else(=2)
    assert _run_with_cmp("LE 2 3") == 1, "2<=3 应进 then"
    assert _run_with_cmp("LE 3 3") == 1, "3<=3 应进 then"
    assert _run_with_cmp("LE 4 3") == 2, "4<=3 应进 else"


def test_ge_runner():
    assert _run_with_cmp("GE 4 3") == 1, "4>=3 应进 then"
    assert _run_with_cmp("GE 3 3") == 1, "3>=3 应进 then"
    assert _run_with_cmp("GE 2 3") == 2, "2>=3 应进 else"


def test_compiler_emit():
    """验证编译器在 <=/>= 规则下生成的是 LE/GE，而不是被降级到 LESS/GREATER。"""
    from Compile_tree import Complie
    from token_ana import varea
    area = varea(None, True, "Main")
    code, _ = Complie("JUDGE", "$OPN$<=$OPN$", ["3", "3"], [], area)
    print("[A3] <= IR:", repr(code.strip()))
    assert "LE 3 3" in code, f"<= 应生成 LE，实际：{code}"

    code, _ = Complie("JUDGE", "$OPN$>=$OPN$", ["3", "3"], [], area)
    print("[A3] >= IR:", repr(code.strip()))
    assert "GE 3 3" in code, f">= 应生成 GE，实际：{code}"


if __name__ == "__main__":
    test_le_runner()
    test_ge_runner()
    test_compiler_emit()
    print("A3 PASS")
