"""共用工具：把项目根目录加入 sys.path，并提供静默版 Runner。"""
import os
import sys
import io
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def run_ir(ir_text, capture_stdout=False):
    """跑一段 IR 文本（多行字符串），返回 Runner 实例（含 .memory 和 REGS）。"""
    # 延迟 import，避免在加 sys.path 之前
    from runner import Runner  # noqa
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
    """读寄存器槽对应的内存值（memory 末尾几个槽位放寄存器）。"""
    # runner.memory 长度 = max_memory + len(REGS)；REGS 槽位是从尾部往前数
    idx = REG_SLOTS[name]  # 形如 -1, -2, ...
    return runner.memory[idx]
