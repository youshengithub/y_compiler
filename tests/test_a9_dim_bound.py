"""A9: 维度边界判断 + 错误下标。修复点：> → >=，muti_dimension[i] → muti_dimension[index]。"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from token_ana import varea, y_token, token_type
from Compile_tree import Complie


def _setup_area_with_int_array():
    area = varea(None, True, "Main")
    # 注册 int 类型
    int_t = y_token(); int_t.set_as_structure("int", 1, [], [])
    area.append_var(int_t)
    # 声明 int a[10]; （直接构造 y_token 模拟符号表注册）
    a = y_token(); a.set_as_variable("a", 10, "int", 0, [10])
    area.append_var(a, a.size)
    return area


def test_dim_inbound():
    area = _setup_area_with_int_array()
    # a[9] 合法
    code, _ = Complie("VAR", "$VAR$", ["a[9]"], [], area)
    assert code != "" and "a[9]" not in code  # 应当生成寻址 IR


def test_dim_at_limit_should_fail():
    area = _setup_area_with_int_array()
    # a[10] 越界（合法下标 0..9）
    try:
        Complie("VAR", "$VAR$", ["a[10]"], [], area)
    except AssertionError:
        return  # 修复后 >= 判定会触发 assert 报错
    raise AssertionError("a[10] 越界应该报错，但当前没报")


def test_dim_strict_overrun():
    area = _setup_area_with_int_array()
    # a[100] 严重越界，无论 > 还是 >= 都会触发——主要测错误信息里下标 BUG
    try:
        Complie("VAR", "$VAR$", ["a[100]"], [], area)
    except (AssertionError, TypeError) as e:
        # 修复前会触发 TypeError: list indices must be integers
        # 修复后只触发 AssertionError
        assert isinstance(e, AssertionError), f"期望 AssertionError，得到 {type(e).__name__}: {e}"


if __name__ == "__main__":
    test_dim_inbound()
    test_dim_at_limit_should_fail()
    test_dim_strict_overrun()
    print("A9 PASS")
