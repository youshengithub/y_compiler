"""C1 – 纯 if（无 else）不应崩溃，且逻辑正确"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Construct_tree import Compiler, Compoment
from runner import Runner
from postprocesser import Postprocesser
import io, contextlib

def run_code(source):
    Compoment.Cs = {}
    Compoment.unmatch = {}
    c = Compiler()
    c.construct_componets("Config.txt")
    state, code = c.Complie_file(source)
    assert state, "编译失败"
    p = Postprocesser()
    code = p.process(code)
    r = Runner()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r.Run_from_code(code.strip().split("\n"))
    return buf.getvalue()

# 测试1：纯 if，条件为真 -> 应执行 body
src1 = "int a;int b;a=1;b=0;if(a==1){b=65;}out(b);"
out1 = run_code(src1)
# b 应该被赋值为 65 -> chr(65) = 'A'
assert 'A' in out1, f"C1-1 FAIL: expected 'A' in output, got {repr(out1)}"

# 测试2：纯 if，条件为假 -> 不执行 body
src2 = "int a;int b;a=2;b=66;if(a==1){b=65;}out(b);"
out2 = run_code(src2)
# b 应该保持 66 -> chr(66) = 'B'
assert 'B' in out2, f"C1-2 FAIL: expected 'B' in output, got {repr(out2)}"

# 测试3：if-else 仍然正常
src3 = "int a;int b;a=1;if(a==1){b=65;}else{b=66;}out(b);"
out3 = run_code(src3)
assert 'A' in out3, f"C1-3 FAIL: expected 'A' in output, got {repr(out3)}"

print("C1 PASS")
