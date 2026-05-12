"""C2 – DIM 带字符串初值时 start_pos 类型应为 int"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from token_ana import y_token, varea, token_type
import Compile_tree

# 模拟一个简单的 area_tree
area = varea(None, True, "Main")
area.append_var(y_token(token_type.structure, "int", 1))

# 先分配一个变量占位
Compile_tree.Complie("DIM", "$TYPE$$EMPTY$$TOKEN$", ["int", "x"], [], area)

# 现在测试带字符串初值的 DIM
code, area = Compile_tree.Complie("DIM", "$TYPE$$EMPTY$$TOKEN$=$STRING$", ["int", "s", "AB"], [], area)

# 找到 s 的 token
tk = area.find_token("s")
assert tk is not None, "C2 FAIL: token 's' not found"
assert isinstance(tk.start_pos, int), f"C2 FAIL: start_pos should be int, got {type(tk.start_pos).__name__} = {repr(tk.start_pos)}"

print(f"[C2] start_pos = {tk.start_pos} (type={type(tk.start_pos).__name__})")
print("C2 PASS")
