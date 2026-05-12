"""共用工具：把项目根目录加入 sys.path，并提供静默版 Runner。"""
import os
import sys
import io
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 确保 src 也在 path 中（兼容旧式导入）
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def run_ir(ir_text, capture_stdout=False):
    """跑一段 IR 文本（多行字符串），返回 Runner 实例（含 .memory 和 REGS）。"""
    from src.runner import Runner
    r = Runner()
    lines = [ln.strip() for ln in ir_text.strip().splitlines() if ln.strip()]
    if capture_stdout:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r.RUN(lines)
        return r, buf.getvalue()
    else:
        r.RUN(lines)
        return r, ""


REG_SLOTS = {"EAX": -1, "EBX": -2, "EBP": -3, "ESP": -4, "EIP": -5, "EFG": -6, "ETP": -7}


def reg(runner, name):
    """读寄存器槽对应的内存值。"""
    idx = REG_SLOTS[name]
    return runner.memory[idx]


def compile_and_run(source_code, capture_stdout=True):
    """编译源代码并运行，返回 (runner, stdout_text)。"""
    from src.Construct_tree import Compiler, Compoment
    from src.postprocesser import Postprocesser
    from src.preprocesser import Preprocesser

    Compoment.Cs = {}
    Compoment.unmatch = {}
    compiler = Compiler()
    config_path = os.path.join(ROOT, "src", "Config.txt")
    compiler.construct_componets(config_path)

    preprocesser = Preprocesser()
    preprocessed = preprocesser.process(source_code)

    state, code = compiler.Complie_file(preprocessed)
    assert state, "编译失败"

    postprocesser = Postprocesser()
    code = postprocesser.process(code)

    from src.runner import Runner
    r = Runner()
    lines = [ln for ln in code.strip().split("\n") if ln.strip()]

    if capture_stdout:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r.RUN(lines)
        return r, buf.getvalue()
    else:
        r.RUN(lines)
        return r, ""
