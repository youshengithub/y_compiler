# y_compiler Bug 修复报告

> 配套文件：`BUGS.md`（原始排查报告）、`tests/`（回归测试集）
> 时间：2026-05-12
> 测试结果：A1–A9 全部 PASS，B 端到端冒烟 PASS（共 9 项）

---

## 一、修复总览

| #   | 编号       | 严重 | 一句话结论                                                          | 修复落点                                              | 验证测试                       |
| --- | ---------- | ---- | ------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------ |
| 1   | BUG 6      | 🔴   | runner 的 PUSH/POP 把 ESP 寄存器自身当栈顶                          | `runner.py` PUSH/POP 重写                             | `test_a1_push_pop.py`          |
| 2   | BUG 4      | 🟡   | （误报）`!=` 实际语义正确，`EQUAL` 末尾的 `not` + `RF` 抵消后结果对 | 仅写白盒/端到端测试确认；不改代码                     | `test_a2_neq_eq.py`            |
| 3   | BUG 5      | 🔴   | `<=` / `>=` 被吞掉                                                  | 新增 `LE/GE` 指令；`Compile_tree.JUDGE` 优先匹配两字符 | `test_a3_le_ge.py`             |
| 4   | BUG 1/2/3  | 🔴   | `MOD` 左右颠倒（与 ADD/SUB/MUL/DIV 实际正确不同）                   | `Compile_tree.MOD` 拆出独立分支，参考 SUB 写法        | `test_a4_mod.py`               |
| 5   | BUG 12     | 🔴   | `set_as_variable` 把 `type` 写两次，覆盖 `token_type.variable`      | `token_ana.py` 拆 `kind` / `type` 两字段              | `test_a5_token_kind.py`        |
| 6   | BUG 7      | 🟠   | `JMP @label` 偏移 baseline 行为                                     | 维持现状 + 写文档注明 baseline；本轮不改               | `test_a6_jmp_offset.py`        |
| 7/8 | BUG 8/9    | 🟠   | `#undefine` 切片错误 / `process_include` 异常分支变量未定义         | `preprocesser.py` 切片改 `len("#undefine ")`；异常分支 `continue` | `test_a7_a8_preprocesser.py`   |
| 9   | BUG 11     | 🟠   | 维度边界判断 `>` 应为 `>=`，下标用错 `i` 应为 `index`               | `Compile_tree.py` VAR 段两处                         | `test_a9_dim_bound.py`         |
| 10  | （新增）   | 🔴   | DIM 分支 rule 字符串拼写错误，导致变量始终未注册                    | `Compile_tree.py` DIM 段改为 `$TYPE$$EMPTY$$TOKEN$`   | B 阶段端到端冒烟              |
| 11  | （新增）   | 🔴   | 多处 IR 直接写变量名，runner 不识别                                 | 新增 `_addr()` 把变量名翻译为 `$start_pos`            | B 阶段端到端冒烟              |
| 12  | （新增）   | 🟠   | VAR 节点对简单标量也输出地址计算 code，污染父节点 codelist 索引     | VAR 段简单标量提前 `return`                          | B 阶段端到端冒烟              |
| 13  | BUG 13/14  | 🟡   | 文档注解，错误信息中 `find_type` 引用顺序                          | 部分通过测试覆盖到（A5/A9）                          | —                              |

---

## 二、详细变更清单

### 1. `runner.py`

- **PUSH 重写**：`memory[ESP] ← value` → 正确写入栈顶 `memory[memory[ESP]] = value; memory[ESP] += 1`
- **POP 重写**：先 `memory[ESP] -= 1`，再 `memory[op1] = memory[memory[ESP]]`
- **新增指令** `LE` / `GE`：
  - `LE op1 op2` → `EFG = not (op1 <= op2)`
  - `GE op1 op2` → `EFG = not (op1 >= op2)`
  - 极性与 `LESS/GREATER/EQUAL` 一致：EFG=True 表示"条件不成立"，配合编译器 `JPIF` 跳过 then 分支。

### 2. `Cyvm.cpp`

- `opcode` 枚举与 `op_map` 增加 `LE` / `GE`
- `case LE:` / `case GE:` 实现与 Python runner 一致
- ⚠️ **本轮未重新编译 `Cyvm.exe`**，已在归档文档中列入"待执行"。

### 3. `Compile_tree.py`

#### 3.1 新增辅助 `_addr(area_tree, op)`（文件首部）

```python
def _addr(area_tree, op):
    """把 oplist 字符串元素翻译为 runner 能识别的操作数。
    数字、寄存器名、已带 $/%/@ 的串原样返回；裸标识符若能在符号表里查到变量，
    则用 $start_pos 表示绝对地址。"""
```

被以下分支使用：`EQUAL` / `PRINT` / `ADD` / `SUB` / `MUL` / `DIV` /
`AND` / `OR` / `XOR` / `MOD` / `NOT` / `JUDGE`。

> 没替换的位置：`GETP` / `SETP` / `ARG` / `RETURN` 等暂未被冒烟用例覆盖；后续如需扩展，按相同模式注入即可。

#### 3.2 DIM 分支 rule 字符串修正

```diff
- if(rule=="$TYPE$->$TOKEN$"):           # 永远不会命中 → 变量从未注册
+ if(rule=="$TYPE$$EMPTY$$TOKEN$"):
- elif(rule=="$TYPE$->$TOKEN$=$STRING$"):
+ elif(rule=="$TYPE$$EMPTY$$TOKEN$=$STRING$"):
```

#### 3.3 VAR 节点：简单标量直接返回空 code

```diff
  if(name=="VAR"):
      if not oplist[0] in [...REGS...]:
+         if "[" not in oplist[0] and "." not in oplist[0]:
+             return code, area_tree    # 标量交给 _addr 处理
          var = y_token.trans_var(oplist[0])
          ...
```

否则父节点（如 `EQUAL $VAR$=$OP$`）的 codelist 会被多塞一段地址计算 code，
导致 `codelist[0]` 不再是右侧 OP 的代码、左右值张冠李戴。

#### 3.4 MOD 独立分支（保证 `EAX = 左, EBX = 右`）

```python
elif(name=="MOD"):
    if(re.match(r"\$OPN\$.+\$OPN\$", rule)):
        code  = "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
        code += "MOD EAX " + _addr(area_tree, oplist[1]) + "\n"
    elif(re.match(r"\$OPN\$.+\$OP\$", rule)):
        code  = codelist[0]
        code += "MOV EBX EAX\n"
        code += "MOV EAX " + _addr(area_tree, oplist[0]) + "\n"
        code += "MOD EAX EBX\n"
    elif(re.match(r"\$OP\$.+\$OPN\$", rule)):
        code  = codelist[0]
        code += "MOD EAX " + _addr(area_tree, oplist[-1]) + "\n"
    elif(re.match(r"\$OP\$.+\$OP\$", rule)):
        code  = codelist[1]              # 右
        code += "MOV EBX EAX\n"
        code += codelist[0]              # 左
        code += "MOD EAX EBX\n"
```

#### 3.5 JUDGE 段：先两字符再单字符

```python
if rule.find("<=") != -1: code = "LE ..."
elif rule.find(">=") != -1: code = "GE ..."
elif rule.find("==") != -1: ...
elif rule.find("!=") != -1: code = "EQUAL ...\nRF\n"   # 误报，保留
elif rule.find("<") != -1: ...
elif rule.find(">") != -1: ...
```

#### 3.6 维度判断

```diff
- if int(i[index+1]) > find_var.muti_dimension[index]:
+ if int(i[index+1]) >= find_var.muti_dimension[index]:
-     print(... find_var.muti_dimension[i] ...)
+     print(... find_var.muti_dimension[index] ...)
```

#### 3.7 STRUCTURE / 一系列 `i.type == token_type.X` 判断

随 `token_ana.y_token` 拆字段（见 4.x），统一改为 `i.kind == token_type.X`。

### 4. `token_ana.py`

```diff
- def __init__(self, type=token_type.variable, ...):
-     self.type = type
+ def __init__(self, kind=token_type.variable, type="", ...):
+     self.kind = kind     # variable / function / structure
+     self.type = type     # 值类型字符串："int" / "double" / 用户结构体名

  def set_as_variable(self, name, size, type, start_pos, muti_dimension=[]):
-     self.type = token_type.variable
+     self.kind = token_type.variable
      self.name = name
      self.size = size
      self.type = type
      self.start_pos = start_pos
      self.muti_dimension = muti_dimension
```

`set_as_function` / `set_as_structure` 同样写 `self.kind = token_type.X`，不再覆盖 `self.type`。

### 5. `preprocesser.py`

```diff
- defines = line[20:].split(" ")
+ defines = line[len("#undefine "):].split(" ")

  except FileNotFoundError:
      print("错误：文件未找到 ...", file_path)
+     continue
  except IOError:
      print("错误：无法读取文件 ...", file_path)
+     continue
```

### 6. `Construct_tree.py`

```diff
- # b_code, self.area_tree = Compile_tree.Complie(name, rule, oplist, code_list, self.area_tree)
+ b_code, self.area_tree = Compile_tree.Complie(name, rule, oplist, code_list, self.area_tree)
```

> 取消注释，让 `show_and_compile` 真正驱动 `Compile_tree.Complie`。

---

## 三、测试集

| 测试文件                             | 覆盖范围                                              |
| ------------------------------------ | ----------------------------------------------------- |
| `tests/harness.py`                   | sys.path 注入 + `run_ir()` 工具 + `REG_SLOTS` 映射    |
| `tests/test_a1_push_pop.py`          | runner PUSH/POP 栈语义                                |
| `tests/test_a2_neq_eq.py`            | `!=` / `==` 在 IF 端到端的语义（确认正确）            |
| `tests/test_a3_le_ge.py`             | `<= / >=` 编译生成 `LE/GE` IR、跳转语义               |
| `tests/test_a4_mod.py`               | `c = a % b` 与表达式 mod 的 IR / 运行结果             |
| `tests/test_a5_token_kind.py`        | y_token `kind` 与 `type` 字段独立                     |
| `tests/test_a6_jmp_offset.py`        | postprocesser JMP 偏移 baseline                       |
| `tests/test_a7_a8_preprocesser.py`   | `#undefine` 切片 + `#include` 异常 fallback           |
| `tests/test_a9_dim_bound.py`         | 数组下标越界判断（`>=` + 下标 `index` 修正）          |
| `tests/test_b_smoke.py` (+ `smoke_mod.txt`) | DIM/EQUAL/MOD/PRINT 端到端冒烟                  |

运行：

```bash
cd y_compiler
for t in tests/test_*.py; do python "$t"; done
```

全部输出尾部应为 `<NAME> PASS`。

---

## 四、本轮**未**修复但已记录的项

1. **BUG 7（JMP 偏移 +2）**：与 postprocesser 的 `ALLOC @label → NOP` 替换数量、runner JMP 语义存在 off-by-one 隐患。`test_a6_jmp_offset.py` 仅记录 baseline，未来若引入函数调用回归，需要专门跑 `lib/lib.txt` 的 `print_int` 单步验证。
2. **Cyvm.cpp 编译**：源代码已加 `LE/GE`，但未重新编译 `Cyvm.exe`。
3. **`GETP` / `SETP` / `ARG` / `RETURN` / `CALL`** 等仍然直接写 `str(oplist[i])`：
   当前冒烟未覆盖；后续如要支持函数调用，应统一接入 `_addr()`。
4. **`postprocesser.process_note` 破坏字符串中 `//`**（BUG 15）：影响极小，未改。
5. **`area_tree.find_token / find_area` 名为 BFS 实为 DFS**（BUG 16）：仅文档级问题。

---

## 五、下一步建议

- 用 `lib/lib.txt` 的 `print_int` 做一次端到端：能跑通即说明 PUSH/POP + JMP 偏移在函数调用语境下也对齐。
- 把 `_addr()` 推广到 `GETP / SETP / ARG / RETURN`，并补一个"指针 + 形参"用例的端到端测试。
- 重新编译 `Cyvm.exe` 后，写一个对比测试：同一份 IR 跑 Python runner 与 Cyvm.exe，比较输出与寄存器终态。
