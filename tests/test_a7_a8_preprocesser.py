"""A7+A8: preprocesser 的 #undefine 与 #include 异常分支。"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from preprocesser import Preprocesser


def test_define_undefine():
    pp = Preprocesser()
    src = (
        "#define FOO bar\n"
        "FOO is here\n"
        "#undefine FOO\n"
        "FOO should remain\n"
    )
    out = pp.process_define(src)
    lines = out.strip().split("\n")
    # 第一行 "FOO is here" 应替换 → "bar is here"
    # 第三行（在 #undefine 之后）应保持 "FOO should remain"，不再被替换
    print("[A7] processed:\n", out)
    assert "bar is here" in out, "define 应替换 FOO→bar"
    assert "FOO should remain" in out, "undefine 后 FOO 不应被替换"


def test_include_missing(tmpdir=None):
    pp = Preprocesser()
    src = "#include<__definitely_nonexistent_file_xyz.txt>\nfoo bar\n"
    # 修复后应该不抛 NameError，并把 include 那行替换为空（或保留），后续行正常
    try:
        out = pp.process_include(src)
    except NameError as e:
        raise AssertionError(f"process_include 异常分支不应抛 NameError，实际：{e}")
    print("[A8] processed:\n", repr(out))
    assert "foo bar" in out, "缺失文件后续行应被保留"


if __name__ == "__main__":
    test_define_undefine()
    test_include_missing()
    print("A7+A8 PASS")
