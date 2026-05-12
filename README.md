# y_compiler

基于 Python 的类 C/C++ 语法编译器，支持编译到自定义 IR 并在虚拟机上运行。

## 项目结构

```
y_compiler/
├── main.py                 # 顶层入口：编译并运行源代码
├── src/                    # 核心源码
│   ├── __init__.py
│   ├── Config.txt          # 语法配置文件（BNF 规则）
│   ├── token_ana.py        # 词法分析 + 符号表（y_token / varea）
│   ├── Construct_tree.py   # 语法分析（递归下降解析器）
│   ├── Compile_tree.py     # 语义分析 + 代码生成（IR 翻译）
│   ├── preprocesser.py     # 预处理器（#include / #define / #undefine / 注释 / 空格）
│   ├── postprocesser.py    # 后处理器（标签替换、JMP 偏移计算）
│   ├── runner.py           # Python 虚拟机（IR 解释器）
│   └── Cyvm.cpp            # C++ 虚拟机实现（高性能版）
├── tests/                  # 测试集
│   ├── __init__.py
│   ├── harness.py          # 测试工具函数
│   └── test_all.py         # 综合测试（IR指令 + 编译器 + 端到端）
├── examples/               # 示例代码
│   └── code.txt            # 示例程序（含素数计算器）
├── lib/                    # 标准库
│   └── lib.txt             # 内置函数（max/min/print_int）
├── docs/                   # 文档
│   ├── BUGS.md             # 已知 bug 排查报告
│   └── FIXES.md            # 修复总览 + 详细变更清单
└── README.md
```

## 快速开始

### 编译运行示例代码

```bash
python main.py                          # 默认运行 examples/code.txt
python main.py examples/code.txt        # 指定源文件
```

### 运行测试

```bash
python tests/test_all.py
```

## 编译器架构

```
源代码 (.txt)
    │
    ▼
┌─────────────┐
│ Preprocesser │  #include / #define / 注释去除 / 空格处理
└─────┬───────┘
      │
      ▼
┌─────────────────┐
│ Construct_tree   │  递归下降解析，生成语法树
│ (语法分析)       │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Compile_tree     │  遍历语法树，生成 IR 指令
│ (代码生成)       │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Postprocesser    │  标签替换、偏移计算
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Runner / Cyvm    │  虚拟机执行 IR
└─────────────────┘
```

## 支持的 IR 指令集（25条）

| 指令 | 语法 | 说明 |
|------|------|------|
| ALLOC | `ALLOC n` | 分配 n 个内存单元 |
| MOV | `MOV dst src` | 数据传送 |
| ADD | `ADD dst src` | 加法 dst += src |
| SUB | `SUB dst src` | 减法 dst -= src |
| MUL | `MUL dst src` | 乘法 dst *= src |
| DIV | `DIV dst src` | 除法 dst /= src |
| MOD | `MOD dst src` | 取模 dst %= src |
| AND | `AND dst src` | 位与 |
| OR | `OR dst src` | 位或 |
| XOR | `XOR dst src` | 位异或 |
| NOT | `NOT dst src` | 位取反 dst = ~src |
| LEA | `LEA dst src` | 取地址 dst = addr(src) |
| SEA | `SEA dst src` | 间接存储 mem[mem[dst]] = src |
| PUSH | `PUSH src` | 压栈 |
| POP | `POP dst` | 出栈 |
| GREATER | `GREATER a b` | a > b 比较 |
| LESS | `LESS a b` | a < b 比较 |
| EQUAL | `EQUAL a b` | a == b 比较 |
| LE | `LE a b` | a <= b 比较 |
| GE | `GE a b` | a >= b 比较 |
| RF | `RF` | 翻转 EFG 标志 |
| JMP | `JMP offset` | 无条件跳转 |
| JPIF | `JPIF offset` | EFG=True 时跳转 |
| JPNIF | `JPNIF offset` | EFG=False 时跳转 |
| OUT | `OUT src` | 输出字符 |
| IN | `IN dst` | 读取输入字符 |
| NOP | `NOP` | 空操作 |

## 支持的语法特性

- 变量声明：`int a;` / `double b[10];`
- 赋值：`a = expr;`
- 算术：`+ - * / %`
- 位运算：`& | ^ !`
- 比较：`== != < > <= >=`
- 逻辑：`&& ||`
- 控制流：`if/else`, `while`, `do-while`, `for`
- 函数：定义、调用、返回值
- 结构体：`struct/class`
- 数组：多维数组访问
- 指针：`&`(取址) / `*`(解引用)
- 预处理：`#include`, `#define`, `#undefine`
- 内联汇编：`asm("IR指令");`
- 字符串字面量初始化

## 测试覆盖

运行 `python tests/test_all.py` 可执行以下三个级别的测试：

1. **IR 指令级测试** (26项)：直接验证虚拟机每条指令的正确性
2. **编译器模块测试** (10项)：验证翻译模块各节点的代码生成
3. **端到端集成测试** (12项)：源码→编译→运行→验证输出

## 开发历史

- 2026-05-12: 修复13项核心bug + 新增 LE/GE 指令 + 完善测试集
- 2026-05-12: 修复翻译模块 IF/DIM/AREA 3项bug
- 2026-05-12: 项目重构，规范化目录结构
