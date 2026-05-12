"""B: 端到端冒烟测试。"""
import sys, os, io, contextlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def compile_and_run(src_text):
    from preprocesser import Preprocesser
    from postprocesser import Postprocesser
    from Construct_tree import Compiler
    from runner import Runner

    pre = Preprocesser()
    post = Postprocesser()
    compiler = Compiler()
    # 加载文法
    config_path = os.path.join(ROOT, "Config.txt")
    compiler.construct_componets(config_path)

    pre_text = pre.process(src_text)
    state, ir = compiler.Complie_file(pre_text)
    if not state:
        raise RuntimeError("编译失败")
    final_ir = post.process(ir)
    print("=== final IR ===")
    print(final_ir)
    print("=== running ===")
    r = Runner()
    lines = [ln.strip() for ln in final_ir.strip().splitlines() if ln.strip()]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r.RUN(lines)
    return buf.getvalue()


def test_smoke_mod():
    src = open(os.path.join(os.path.dirname(__file__), "smoke_mod.txt"), encoding="utf-8").read()
    out = compile_and_run(src)
    print("=== program stdout ===")
    print(repr(out))
    # 7%3 = 1，out(c) 应输出 chr(1)（不可见），关键在程序是否跑完不报错
    # 用 ord 检查
    assert chr(1) in out, f"期望输出包含 chr(1)，实际 repr：{out!r}"


if __name__ == "__main__":
    test_smoke_mod()
    print("B smoke PASS")
