#!/usr/bin/env python3
"""
=== 端到端 .y 源代码测试 ===

运行方式：
  cd y_compiler
  python tests/test_e2e.py
"""
import os
import sys
import io
import traceback
import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.Construct_tree import Compiler, Compoment
from src.postprocesser import Postprocesser
from src.preprocesser import Preprocesser
from src.runner import Runner

TIMEOUT_SEC = 5  # 每个测试最多5秒

TEST_CASES = [
    ("t01_assign_out.y",    "A",    False),
    ("t02_add.y",           "A",    False),
    ("t03_sub.y",           "A",    False),
    ("t04_mul.y",           "B",    False),
    ("t05_div.y",           "A",    False),
    ("t06_mod.y",           "1",    False),
    ("t07_and.y",           "8",    False),
    ("t08_or.y",            "A",    False),
    ("t09_xor.y",           "A",    False),
    ("t10_if_else_true.y",  "Y",    False),
    ("t11_if_else_false.y", "N",    False),
    ("t12_if_no_else.y",    "A",    False),
    ("t13_while.y",         "A",    False),
    ("t14_for.y",           "5",    False),
    ("t15_do_while.y",      "ABC",  False),
    ("t16_cmp_ops.y",       "YYY",  False),
    ("t17_nested_if.y",     "A",    False),
    ("t18_compound.y",      "Z",    False),
    ("t19_string.y",        "A",    False),
    ("t20_asm.y",           "A",    False),
    ("t21_func.y",          "A",    False),
    ("t22_define.y",        "A",    False),
    ("t23_nested_loop.y",   "9",    False),
    ("t24_multi_out.y",     "OK",   False),
    ("t25_sum.y",           "6",    False),
    ("t26_precedence_mul_add.y", "7", False),
    ("t27_precedence_mul_sub.y", "4", False),
    ("t28_precedence_paren.y",   "9", False),
    ("t29_precedence_div_add.y", "4", False),
    ("t30_precedence_mixed.y",   "8", False),
    ("t31_func_return.y",       "A",    False),
    ("t32_dim_init.y",          "A",    False),
    ("t33_dim_expr_init.y",     "A",    False),
    ("t34_compound_add.y",      "A",    False),
    ("t35_compound_sub.y",      "A",    False),
    ("t36_compound_mul.y",      "A",    False),
    ("t37_incr.y",              "A",    False),
    ("t38_decr.y",              "A",    False),
    ("t39_break.y",             "3",    False),
    ("t40_continue.y",          "2",    False),
    ("t41_outnum.y",            "65",   False),
    ("t42_multiline_comment.y", "A",    False),
    ("t43_struct.y",            "AB",   False),
    ("t44_while_break.y",       "1",    False),
    ("t45_func_multi_args.y",   "A",    False),
    ("t46_out_expr.y",          "A",    False),
    ("t47_for_incr.y",          ":",    False),
    ("t48_outnum_expr.y",       "100",  False),
    ("t49_compound_div_mod.y",  "6",    False),
    # — 新增功能测试 —
    ("t50_array_index.y",       "ABC",  False),
    ("t51_negative.y",          "A",    False),
    ("t52_void_call.y",         "A",    False),
    ("t53_global_var.y",        "A",    False),
    ("t54_recursive.y",         "0",    False),
    ("t55_switch.y",            "B",    False),
    ("t56_method.y",            "A",    False),
    ("t57_array_param.y",       "B",    False),
    ("t58_switch_case.y",       "C",    False),
    ("t59_fib.y",               "3",    False),
    ("t60_global_counter.y",    "3",    False),
    ("t61_array_sum.y",         "6",    False),
    ("t62_nested_func.y",       "A",    False),
    ("t63_expr_arg.y",          "A",    False),
    ("t64_multi_return.y",      "B",    False),
    ("t65_struct_calc.y",       "A",    False),
    ("t66_method_call.y",       "B",    False),
    ("t67_array_func.y",        "B",    False),
    ("t68_nested_struct.y",     "A",    False),
    ("t69_func_call_in_expr.y", "A",    False),
    ("t70_mutual_recursion.y",  "C",    False),
]

_devnull = open(os.devnull, 'w')

def _silence():
    sys.stdout = _devnull

def _restore():
    sys.stdout = sys.__stdout__

def init_compiler():
    Compoment.Cs = {}
    Compoment.unmatch = {}
    compiler = Compiler()
    _silence()
    compiler.construct_componets(os.path.join(ROOT, "src", "Config.txt"))
    _restore()
    return compiler

def compile_and_run(compiler, filepath):
    Compoment.unmatch = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    preprocesser = Preprocesser()
    preprocessed = preprocesser.process(source)

    _silence()
    try:
        state, code = compiler.Complie_file(preprocessed)
    except Exception as e:
        _restore()
        return False, "", f"编译异常: {e}"
    _restore()

    if not state:
        return False, "", "编译失败"

    postprocesser = Postprocesser()
    code = postprocesser.process(code)

    runner = Runner()
    lines = [ln for ln in code.strip().split("\n") if ln.strip()]

    output_buf = io.StringIO()
    sys.stdout = output_buf
    try:
        runner.RUN(lines)
    except Exception as e:
        _restore()
        return False, "", f"运行时错误: {e}"
    _restore()

    raw_output = output_buf.getvalue()
    marker = "**********execing*********\n"
    if marker in raw_output:
        after_marker = raw_output.split(marker, 1)[1]
        time_marker = "\n虚拟机执行时间:"
        if time_marker in after_marker:
            user_output = after_marker.split(time_marker, 1)[0]
        else:
            user_output = after_marker
    else:
        user_output = raw_output

    return True, user_output, ""


def main():
    cases_dir = os.path.join(ROOT, "tests", "cases")
    compiler = init_compiler()
    
    passed = 0
    failed = 0
    skipped = 0
    errors = []

    print("=" * 60)
    print("  端到端 .y 源代码测试")
    print("=" * 60)

    for filename, expected, skip in TEST_CASES:
        filepath = os.path.join(cases_dir, filename)

        if skip:
            skipped += 1
            print(f"  ⏭️  {filename}: SKIP")
            continue
        
        if not os.path.exists(filepath):
            failed += 1
            msg = f"  ❌ {filename}: 文件不存在"
            print(msg)
            errors.append(msg)
            continue

        try:
            def _timeout_handler(signum, frame):
                raise TimeoutError("执行超时")
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(TIMEOUT_SEC)
            success, output, err_msg = compile_and_run(compiler, filepath)
            signal.alarm(0)
        except TimeoutError:
            signal.alarm(0)
            failed += 1
            msg = f"  ❌ {filename}: 执行超时(可能死循环)"
            print(msg)
            errors.append(msg)
            _restore()
            continue
        except Exception as e:
            failed += 1
            msg = f"  ❌ {filename}: 异常 - {e}"
            print(msg)
            errors.append(msg)
            continue

        if not success:
            failed += 1
            msg = f"  ❌ {filename}: {err_msg}"
            print(msg)
            errors.append(msg)
            continue

        if output == expected:
            passed += 1
            print(f"  ✅ {filename}: '{output}' == '{expected}'")
        else:
            failed += 1
            msg = f"  ❌ {filename}: 期望 '{expected}', 实际 '{output}'"
            print(msg)
            errors.append(msg)

    print()
    print("=" * 60)
    total = passed + failed + skipped
    print(f"  总计: {total} | 通过: {passed} ✅ | 失败: {failed} ❌ | 跳过: {skipped} ⏭️")
    
    if errors:
        print()
        print("  失败详情:")
        for e in errors:
            print(f"    {e}")
    
    print()
    if failed == 0:
        print("  🎉 ALL E2E TESTS PASSED!")
    
    _devnull.close()
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
