"""C3 – 空代码块 {} 应生成 NOP 而非 NOPs"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Compile_tree
from token_ana import varea, y_token, token_type

area = varea(None, True, "Main")
area.append_var(y_token(token_type.structure, "int", 1))

code, area = Compile_tree.Complie("AREA", "$AREA_S$$AREA_E$", [], [], area)

assert "NOPs" not in code, f"C3 FAIL: 'NOPs' found in code: {repr(code)}"
assert "NOP" in code, f"C3 FAIL: 'NOP' not found in code: {repr(code)}"

print(f"[C3] empty AREA code: {repr(code)}")
print("C3 PASS")
