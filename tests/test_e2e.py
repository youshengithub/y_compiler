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
    # — 算法测试 —
    ("t71_while_sum.y",         "55",   False),
    ("t72_dowhile_count.y",     "1",    False),
    ("t73_nested_for.y",        "9",    False),
    ("t74_func_fib_iter.y",     "55",   False),
    ("t75_gcd.y",               "12",   False),
    ("t76_power.y",             "256",  False),
    ("t77_abs_val.y",           "42",   False),
    ("t78_array_reverse.y",     "CBA",  False),
    ("t79_bubble_sort.y",       "123",  False),
    ("t80_max_min.y",           "9",    False),
    # — 新增功能：switch/case、成员函数、继承 —
    ("t81_switch_case.y",       "B",    False),
    ("t82_switch_default.y",    "D",    False),
    ("t83_method.y",            "B",    False),
    ("t84_method_return.y",     "A",    False),
    ("t85_constructor.y",       "AB",   False),
    ("t86_inheritance.y",       "4",    False),
    ("t88_strlen.y",            "5",    False),
    ("t89_switch_no_default.y", "A",    False),
    ("t90_method_multi.y",      "D",    False),
    ("t91_multi_instance.y",    "AB",   False),
    ("t92_switch_fallthrough.y","AC",   False),
    ("t93_method_modify.y",     "A",    False),
    ("t94_nested_struct_access.y","A",  False),
    ("t95_struct_access.y",     "AB",   False),
    ("t96_linked_list.y",       "3",    False),
    ("t97_method_chain.y",      "C",    False),
    ("t98_switch_assign.y",     "B",    False),
    ("t99_method_loop.y",       "5",    False),
    ("t100_stack.y",            "CBA",  False),
    # — 综合测试：方法进阶 + switch进阶 —
    ("t101_method_if.y",        "Y",    False),
    ("t102_multi_instance_method.y","BD",False),
    ("t103_queue.y",            "AB",   False),
    ("t104_switch_func.y",      "C",    False),
    ("t105_state_machine.y",    "A",    False),
    # — 新增功能：else if / JUDGE表达式 / 逻辑运算 / 嵌套函数 / 数组表达式下标 / 表达式初始化 —
    ("t106_else_if.y",          "B",    False),
    ("t107_judge_expr.y",       "5",    False),
    ("t108_logic_and.y",        "A",    False),
    ("t109_logic_or.y",         "A",    False),
    ("t110_logic_not.y",        "A",    False),
    ("t111_nested_call.y",      "A",    False),
    ("t112_arr_expr_idx.y",     "CE",   False),
    ("t113_dim_expr_init.y",    "A",    False),
    ("t114_complex_judge.y",    "2",    False),
    ("t115_fib_nested_call.y",  "3",    False),

    # ---- 数组作为函数参数 ----
    ("t116_arr_param_read.y",   "D",    False),  # 数组参数读取
    ("t117_arr_param_write.y",  "B",    False),  # 数组参数写入
    ("t118_arr_param_pass.y",   "A",    False),  # 数组参数再传递
    ("t119_arr_param_sort.y",   "1",    False),  # 数组参数排序
    ("t120_global_arr_param.y", "C",    False),  # 全局数组参数

    # ---- 预处理器增强: 宏/条件编译/标准库 ----
    ("t121_func_macro.y",       "A",    False),  # 函数式宏
    ("t122_ifdef.y",            "AB",   False),  # #ifdef / #ifndef
    ("t123_undef.y",            "AB",   False),  # #undef
    ("t124_include_stdio.y",    "65",   False),  # stdio.y print_int
    ("t125_include_math.y",     "A",    False),  # math.y abs
    ("t126_max_min.y",          "AB",   False),  # math.y max/min
    ("t127_gcd_lib.y",          "4",    False),  # math.y gcd
    ("t128_include_stdlib.y",   "F",    False),  # stdlib.y 全包含
    ("t129_multiline_macro.y",  "Hi",   False),  # 多行宏
    ("t130_ifdef_else.y",       "A",    False),  # #ifdef #else
    ("t131_include_guard.y",    "A",    False),  # include 防重复
    ("t132_pow.y",              "@",    False),  # pow_int
    ("t133_isqrt.y",            "7",    False),  # isqrt
    # — 新功能测试 —
    ("t134_char_literal.y",     "A",    False),  # 字符字面量
    ("t135_char_literal_calc.y","C",    False),  # 字符字面量计算
    ("t136_enum_basic.y",       "B",    False),  # enum 枚举
    ("t137_enum_value.y",       "A",    False),  # enum 指定值
    ("t138_typedef.y",          "A",    False),  # typedef
    ("t139_const.y",            "A",    False),  # const
    ("t140_ternary.y",          ":",    False),  # 三元运算符 true (10+48=58=':')
    ("t141_ternary_false.y",    "8",    False),  # 三元运算符 false (8+48=56='8')
    ("t142_for_dim.y",          ":",    False),  # for中DIM (10+48=58=':')
    ("t143_chain_sub.y",        "5",    False),  # 连续减法 (5+48=53='5')
    ("t144_chain_sub_var.y",    "<",    False),  # 变量连续减法 (12+48=60='<')
    ("t145_const_fold.y",       "7",    False),  # 常量折叠 (7+48=55='7')
    ("t146_perf_counter.y",     ":",    False),  # 性能计数 (10+48=58=':')

    # ---- 严重差距补齐 ----
    ("t147_float_basic.y",      "5:",   False),  # 浮点基础
    ("t148_pointer_basic.y",    "42",   False),  # 指针读取
    ("t149_pointer_write.y",    "99",   False),  # 指针写入
    ("t150_malloc_basic.y",     "A",    False),  # 堆内存分配
    ("t151_array_init.y",       "ABC",  False),  # 数组字面量初始化
    ("t152_shift.y",            "8,4",  False),  # 位移运算
    ("t153_sizeof.y",           "1",    False),  # sizeof
    ("t154_null.y",             "0",    False),  # NULL 指针
    ("t155_forward_decl.y",     "7",    False),  # 函数调用
    ("t156_pointer_arith.y",    "H",    False),  # 指针+数组
    ("t157_shift_assign.y",     "16,4", False),  # 位移复合赋值
    ("t158_float_calc.y",       "3",    False),  # 整数除法
    ("t159_malloc_array.y",     "ABCDE",False),  # 堆数组分配
    ("t160_ptr_swap.y",         "20,10",False),  # 指针交换变量
    ("t161_array_init_sum.y",   "15",   False),  # 数组初始化求和
    ("t162_shift_ops.y",        "240",  False),  # 位移运算
    ("t163_struct_ptr.y",       "53",   False),  # 结构体访问
    ("t164_ptr_chain.y",        "100",  False),  # 指针链
    ("t165_malloc_free.y",      "AB",   False),  # 堆分配+释放
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
    Compoment.Cs = {}
    Compoment.unmatch = {}
    _silence()
    compiler.construct_componets(os.path.join(ROOT, "src", "Config.txt"))
    _restore()

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    preprocesser = Preprocesser()
    preprocesser.set_lib_dirs([os.path.join(ROOT, "lib")])
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
