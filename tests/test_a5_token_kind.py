"""A5: y_token 应当用 kind 表示种类（function/variable/structure），用 type 保存值类型字符串。

修复前 set_as_variable 里 self.type = token_type.variable 立即被 self.type = type（"int"）覆盖。
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from token_ana import y_token, token_type


def test_variable_kind():
    t = y_token()
    t.set_as_variable("a", 4, "int", 0, [])
    assert t.kind == token_type.variable, f"set_as_variable 后 kind 应=variable，实际 {t.kind}"
    assert t.type == "int", f"set_as_variable 后 type 应=int，实际 {t.type}"


def test_function_kind():
    t = y_token()
    t.set_as_function("double", "foo", ["int", "int"])
    assert t.kind == token_type.function
    # 函数的 type 字段不再有意义，但不应是 token_type 枚举混入
    # 主要确认 kind 正确分类


def test_structure_kind():
    t = y_token()
    t.set_as_structure("S", 8, [], [])
    assert t.kind == token_type.structure


def test_compile_tree_classify():
    """Compile_tree.py STRUCTURE 段按 i.kind 分类的逻辑要能区分变量。"""
    from token_ana import varea
    area = varea(None, True, "Main")
    v = y_token(); v.set_as_variable("v", 4, "int", 0, [])
    f = y_token(); f.set_as_function("int", "fn", [])
    s = y_token(); s.set_as_structure("S", 8, [], [])
    area.vars = [v, f, s]
    funcs = [i for i in area.vars if i.kind == token_type.function]
    structs = [i for i in area.vars if i.kind == token_type.structure]
    vars_ = [i for i in area.vars if i.kind == token_type.variable]
    assert len(funcs) == 1 and funcs[0].name == "fn"
    assert len(structs) == 1 and structs[0].name == "S"
    assert len(vars_) == 1 and vars_[0].name == "v"


if __name__ == "__main__":
    test_variable_kind()
    test_function_kind()
    test_structure_kind()
    test_compile_tree_classify()
    print("A5 PASS")
