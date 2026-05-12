#!/usr/bin/env python3
"""y_compiler 主入口 —— 编译并运行源代码"""
import os
import sys

# 确保项目根目录在 sys.path 中
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.Construct_tree import Compiler, Compoment
from src.runner import Runner
from src.postprocesser import Postprocesser
from src.preprocesser import Preprocesser


def main():
    source_file = sys.argv[1] if len(sys.argv) > 1 else "examples/code.txt"
    config_file = os.path.join(ROOT, "src", "Config.txt")

    if not os.path.exists(source_file):
        print(f"错误：源文件不存在: {source_file}")
        sys.exit(1)

    # 初始化编译器各组件
    Compoment.Cs = {}
    Compoment.unmatch = {}
    compiler = Compiler()
    runner = Runner()
    postprocesser = Postprocesser()
    preprocesser = Preprocesser()

    # 加载语法配置
    compiler.construct_componets(config_file)

    # 读取源代码
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 预处理
    preprocessed = preprocesser.process(content)

    # 编译
    state, code = compiler.Complie_file(preprocessed)
    if not state:
        print("编译失败！")
        sys.exit(1)

    # 后处理
    code = postprocesser.process(code)

    # 保存 IR
    ir_path = os.path.join(ROOT, "output", "IR.txt")
    os.makedirs(os.path.dirname(ir_path), exist_ok=True)
    with open(ir_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"[INFO] IR 已保存至 {ir_path}")

    # 运行
    lines = [ln for ln in code.strip().split("\n") if ln.strip()]
    runner.Run_from_code(lines)


if __name__ == "__main__":
    main()
