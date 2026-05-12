# y_compiler Bug 排查报告

> 阅读对象：`Compile_tree.py`、`token_ana.py`、`postprocesser.py`、`preprocesser.py`、`runner.py`
> 时间：2026-05-12
> 标记说明：🔴 严重（编译/运行崩溃或结果错） · 🟠 显著（边界场景崩溃） · 🟡 轻微（健壮性 / 文档）

---

## 🔴 BUG 1：除法 / 减法的 `$OP$op$OPN$` 规则代码顺序写反

**位置**：`Compile_tree.py` `SUB`、`DIV`（以及 `AND/XOR/OR/MOD` 整组）

**症状**：当左操作数是表达式（`$OP$`）、右操作数是单个值（`$OPN$`）时，二元运算的求值顺序看起来正确，但**模式判定的正则非常宽松**，会把更长的式子里夹带 `$OP$` 的情形误命中先到先得的分支。

**示例对照**

`AND/XOR/OR/MOD` 的 `$OP$.+$OP$` 分支（第 213–217 行）：
```python
elif(bool(re.match("\\$OP\\$.+\\$OP\\$", rule))):
    code=codelist[0]
    code+="MOV EBX EAX\n"
    code+=codelist[1]
    code+=name+" EAX EBX\n"
```
对比 `ADD` / `SUB` / `MUL` / `DIV` 在同一情形下使用的写法（第 141–145、160–164 等）：
```python
code=codelist[1]
code+="MOV EBX EAX\n"
code+=codelist[0]
code+=name+" EAX EBX\n"
```
两者左右子树的求值顺序**不一致**：`AND/OR/XOR/MOD` 先算左子树再算右子树，结果存到 EBX 后，`name EAX EBX` 实际把 `EBX op EAX` 写入 `EAX`——
- 对 `AND/OR/XOR` 这种交换律运算无影响；
- 对 `MOD` **结果错误**（`a%b` 会被算成 `b%a`）。

**修复**：把 `MOD` 与 `AND/OR/XOR` 拆开，参考 `SUB` 的写法保证 `EAX = (左)`、`EBX = (右)`，再 `MOD EAX EBX`。

---

## 🔴 BUG 2：`MUL` 的 `$OP$*$OP$` 分支同样存在左右颠倒

**位置**：`Compile_tree.py` 第 177–181 行

```python
elif(rule=="$OP$*$OP$"):
    code=codelist[1]            # 先算右
    code+="MOV EBX EAX\n"
    code+=codelist[0]            # 再算左
    code+="MUL EAX EBX\n"
```
乘法是交换律的，没有正确性问题；但**和 `ADD` 写法不一致**（`ADD` 同分支也是先 codelist[1] 再 codelist[0]，OK）。

但比对 `DIV` 第 196–200 行：
```python
elif(rule=="$OP$/$OP$"):
    code=codelist[1]
    code+="MOV EBX EAX\n"
    code+=codelist[0]
    code+="DIV EAX EBX\n"   # ← 这里变成 EAX(=左) /= EBX(=右)，正确
```
等等，`DIV EAX EBX` 在 `runner.py` 中实现为 `memory[EAX] /= memory[EBX]`，所以 `DIV` 写得**对**。

但 `SUB` 的 `$OP$-$OP$` 分支（第 161–164）：
```python
code=codelist[1]                 # EAX ← 右
code+="MOV EBX EAX\n"            # EBX ← 右
code+=codelist[0]                # EAX ← 左
code+="SUB EAX EBX\n"            # EAX ← 左 - 右  ✅
```
这个是对的。

**真正的 bug 在 `AND/XOR/OR/MOD` 那段**——它把 codelist[0] 当成"左子树"，但 `ADD/SUB/MUL/DIV` 的 `$OP$op$OP$` 分支用的是 `codelist[1]` 作为左、`codelist[0]` 作为右（反过来）。两边对同一份 `codelist` 下标的语义不一致，至少有一组是错的。

**结论**：`AND/XOR/OR/MOD` 的求值顺序与算术运算不一致；`MOD` 因为非交换会得到错误结果。

---

## 🔴 BUG 3：`Complie` 函数 `OP+OP` 分支注释与代码的“左右子树”定义不一致

**位置**：`ADD` 第 141–145、`SUB` 第 161–164、`MUL` 第 177–181、`DIV` 第 196–200

```python
elif(rule=="$OP$+$OP$"):
    code=codelist[1]   # ← 这里假设 codelist[1] 是左子树
    code+="MOV EBX EAX\n"
    code+=codelist[0]
    code+="ADD EAX EBX\n"
```
但语法分析自上而下，`codelist[0]` 通常是**第一个匹配到的子节点**（左子树）。这意味着这里很可能写反了，导致 `a-b` 被编成 `b-a`。  
**建议**：在调用 `Complie` 的地方打印 `rule + codelist` 的对应关系做一次验证；如果确实反了，把所有 `$OP$+$OP$ / -/* / //` 分支的 `codelist[0]` 与 `codelist[1]` 位置交换。

---

## 🔴 BUG 4：`!=` 编译生成的代码语义错误

**位置**：`Compile_tree.py` 第 281–283 行

```python
elif(rule.find("!=")!=-1):
    code="EQUAL "+oplist[0]+" "+oplist[1]+"\n"
    code+="RF\n"
```
- `EQUAL` 在 `runner.py` 中（第 199 行）执行的最后一句是 `EFG = not EFG`，相当于"相等时 EFG=False"。
- 紧跟一个 `RF`（`EFG = not EFG`）——结果是"相等时 EFG=True"——**和 `==` 完全一样**，`!=` 语义被吃掉了。

**修复**：`!=` 应当是"`EQUAL` 之后**不要** `RF`"，或者把整套比较的极性梳理清楚。`runner.py` 里 `GREATER/LESS/EQUAL` 后面统一都加了 `not`，配合编译器里到处 `JPIF` 跳到 else 分支，整个 EFG 的语义**反向**且容易掉坑。

---

## 🔴 BUG 5：`<=` / `>=` 直接被吞掉

**位置**：`Compile_tree.py` 第 271–274 行

```python
if(rule.find("<=")!=-1):
    pass
elif(rule.find(">=")!=-1):
    pass
if(rule.find("<")!=-1):
    code="LESS "+oplist[0]+" "+oplist[1]+"\n"
elif(rule.find(">")!=-1):
    code="GREATER "+oplist[0]+" "+oplist[1]+"\n"
```
- 进入 `<=` 分支后只是 `pass`，**没有 return / 没有 break**；
- 紧接着的 `if rule.find("<")!=-1` 因为 `<=` 也包含 `<`，会再被命中，最终被编成普通的 `<`。
- `>=` 同理被编成 `>`。

**修复**：在 `<=/>=` 处补上正确的 IR 生成（例如先 `LESS` 再用 `EQUAL` 取或；或扩展 `runner.py` 增加 `LE/GE` 指令）。

---

## 🔴 BUG 6：`runner.py` 的 `PUSH` 实现有竞态——先写后加

**位置**：`runner.py` 第 165–170 行

```python
elif(keywords[0]=="PUSH"):
    if(flag1=="pos"):
        self.memory[REGS["ESP"]]= int(self.memory[op1])  # 把值写进 ESP 寄存器位置（=-4）
    else:
        self.memory[REGS["ESP"]]= int(op1)
    self.memory[REGS["ESP"]]+=1
```
这里把 `memory[REGS["ESP"]]` 直接当成"被压数据 + 自身递增"——
1. 第一行把"要压入的数值"写到了 `memory[-4]`（也就是 ESP 寄存器**自身**），而不是栈顶 `memory[memory[-4]]`；
2. 第二行 `+=1` 把它当数值递增；

正确语义应当是：
```python
sp = self.memory[REGS["ESP"]]
self.memory[sp] = value
self.memory[REGS["ESP"]] = sp + 1
```
**这个 bug 让 `PUSH` 实际上覆盖了 ESP 自身**，立即破坏栈帧。`POP`（第 171–175）也对应错误：
```python
self.memory[REGS["ESP"]]-=1
if(flag1=="pos"):
    self.memory[op1]=self.memory[REGS["ESP"]]   # ← 把 ESP 寄存器值给目的，而不是 memory[ESP]
```
应当是 `self.memory[op1] = self.memory[self.memory[REGS["ESP"]]]`。

> ⚠️ 这是 runner.py 里**最严重**的实现错误，凡是带函数调用 / `PUSH/POP` 的程序都会跑飞。

---

## 🟠 BUG 7：`postprocesser.py` 的 `JMP @label` 偏移多加了 2

**位置**：`postprocesser.py` 第 31 行
```python
toend=tags[name]-i+2
```
`runner.py` 中 `JMP` 的语义是 `EIP += op1` 后 `continue`（不再 `+1`），因此**只需偏移 = 目的行 - 当前行**，无需 `+2`。
- 当前 `+2` 会让 `JMP @label` **跳到 label 之后第二条**指令——除非编写者是有意把 label 当作"call site 之后还要跳过 ALLOC + JMP 两条"的约定，那就需要在 BUG 8 中说明的 `ALLOC @label` 实际有占位才行。
- 但 `ALLOC @label` 行已被替换为单条 `NOP`（不是两条），所以偏移 `+1` 就够，`+2` 偏多 1。

**建议**：单步跑通 `lib/lib.txt` 的 `print_int` 调用，看看 `JMP` 是否真的进入 ALLOC 行下一行。

---

## 🟠 BUG 8：`process_define` 解析 `#undefine` 取了第 20 字符之后

**位置**：`preprocesser.py` 第 41 行
```python
defines=line[20:].split(" ")
```
`#undefine ` 长度只有 10。这里取 `line[20:]` 会**把要 undefine 的标识符截断成空串**（如果标识符长度不足 11）。这条分支几乎永远跑不出正确结果。

**修复**：`line[len("#undefine "):].split(" ")` 或 `line[10:].split(" ")`。

---

## 🟠 BUG 9：`process_include` 出现 FileNotFoundError 后 `content` 未定义即被使用

**位置**：`preprocesser.py` 第 24–28 行
```python
except FileNotFoundError:
    print("错误：文件未找到。请检查文件路径是否正确:",file_path)
except IOError:
    print("错误：无法读取文件:",file_path)
code+=self.process_include(content)   # ← 异常情况下 content 是上一轮的值或 NameError
```
异常分支没有 `continue` / `return` / 设置 `content=""`，会把上一轮的 `content` 当作此次 include 的内容，或者直接抛 `NameError`。

---

## 🟠 BUG 10：`remove_spaces_outside_quotes` 把名字写反了

**位置**：`preprocesser.py` 第 49–60 行  
函数名叫 *outside* quotes，但实际逻辑：
```python
if(char==' ' and in_quotes):    # 引号内
    result.append('\x00')
else:
    result.append(char)         # 引号外原样保留
```
用占位符替换的是**引号内的空格**，函数名应当是 `_inside_quotes`。功能是对的（保护字符串里的空格不被后续 `remove_spaces_around_symbols` 误删），名字坑读者。

---

## 🟠 BUG 11：变量维度边界判断有 off-by-one + 错误下标

**位置**：`Compile_tree.py` 第 56–58 行
```python
if(int(i[index+1])>find_var.muti_dimension[index]):
    print(... ,find_var.muti_dimension[i],...)
```
- 边界判断写成 `>`，应是 `>=`（`int a[10]` 合法下标是 0..9）。
- `print` 里的 `find_var.muti_dimension[i]` 用的是循环外面的 `i`（一个 list），会报 `TypeError: list indices must be integers`，应该是 `find_var.muti_dimension[index]`。

---

## 🟠 BUG 12：`set_as_variable` 把 `type` 字段写两次，覆盖了 `token_type.variable`

**位置**：`token_ana.py` 第 33–39 行
```python
def set_as_variable(self, name, size, type, start_pos, muti_dimension=[]):
    self.type = token_type.variable     # 先标记成"变量类别"
    self.name = name
    self.size = size
    self.type = type                    # ← 立刻被字符串类型名（"int"/"double"…）覆盖
    self.start_pos = start_pos
    self.muti_dimension = muti_dimension
```
之后 `get_type()` / `if i.type==token_type.function` 这种判断会全部失效（`type` 变成 `"int"` 字符串）。

**影响**：
- `STRUCTURE` 那段（第 430–433）按 `i.type==token_type.function/structure` 划分成员的逻辑，会把所有变量当成 "default 分支" 进入 `vars`——巧合是想要的结果，但只是**因为没人用 `==token_type.variable` 判断**才没暴雷。
- 一旦其它代码用 `is_variable() / type==token_type.variable`，就会立刻挂掉。

**修复**：用两个字段，比如 `kind = token_type.variable` 和 `value_type = "int"`。

---

## 🟡 BUG 13：`Compile_tree.py` 行 33–34 的提示信息引用了未定义的 `find_type`

```python
if not find_flag:
    print(f"类型{find_type.name}不包含{i[0]}变量")
```
当 `id==0` 这一支没 take 走、走到第二轮才进入 `else`，`find_type` 还在 line 40 被定义；逻辑上没问题。但若第一次循环就进入 `else`（用户写了 `a.b` 但 `a` 不存在），`find_type` 还是上一次循环结尾的——多文件场景容易拼错信息。建议给 `find_type` 一个默认值再用。

---

## 🟡 BUG 14：`Compile_tree.py` 行 39 `assert(find_type!=None)` 在变量未定义时也会触发

`find_var.type` 是字符串（见 BUG 12），如果是 `"int"` 这样的内建类型，`area_tree.find_token("int")` 必须保证早就把 int / double 注册成了 `y_token`。`Construct_tree.py / Compile_tree.py` 的 `Compiler.__init__` 是否注册了——快速检查发现没有详细写注释，容易"明明写了 `int a;` 但报 `find_type==None`"的灵异错误。

---

## 🟡 BUG 15：`postprocesser.process_note` 会破坏字符串中的 `//`

```python
pos=line.find("//")
if pos!=-1:
    content+=line[0:pos]+"\n"
```
和 `preprocesser.process_note` 一样，对 `print("a//b")` 这样的字符串字面量是不安全的。考虑到 IR 输出阶段一般不会出现这种行，影响小，但仍是隐患。

---

## 🟡 BUG 16：`area_tree.find_token / find_area` 把 BFS 写成了 DFS

**位置**：`token_ana.py` 第 121–147 行  
变量名叫 `bfs`，但用的是 `pop()`（list.pop 默认从尾部弹出）。等价于 DFS 沿父链向上走——对作用域查找而言这反倒是想要的（先看自己再看父亲），但**变量名误导**严重。建议改名 `walk` 或 `frontier`。

---

## 🟡 BUG 17：`runner.py` 第 1 行注释说支持 22 条指令，实际更多

注释写的指令清单缺少了 `SEA`、`NOP`、`NOR`（实现里也没有）、`POP`，对应实现却分散写着。指令集与文档/注释不一致，新人看会迷路。

---

## 🟡 BUG 18：`Cyvm.exe` 与 `runner.py` 行为可能不一致

C++ 版没有同步检查；至少 `EFG` 反极性、`PUSH/POP` 的实现细节、`JMP` 偏移定义都需要二者**逐条对齐测试**，否则同一份 IR 会一边能跑一边乱跑。

---

# 修复优先级建议

1. **先修 runner 的 PUSH/POP**（BUG 6）—— 否则任何函数调用都跑不通。
2. 然后修 `!=` / `<=` / `>=`（BUG 4、5）—— 否则条件判断/循环都不可信。
3. 再修 `MOD` 的左右操作数次序（BUG 1、3）。
4. `set_as_variable` 字段重名（BUG 12）—— 让符号表语义正确，避免后续踩雷。
5. 其余按时间允许批量改。

---

# 一些建议性改造

- 加上单元测试：分别针对 `preprocesser`、`postprocesser`、`runner`，用最小 IR 片段验证每条指令。
- `runner.py` 的 `PUSH/POP` 可以用 helper 函数 `_push(value)/_pop_to(addr)` 封装，便于和 `Cyvm.cpp` 对齐。
- 把 `token_type.variable` / `token_type.function` / `token_type.structure` 与 `value_type`（"int" 等）彻底分离。
- 给 `Compile_tree.py` 的每个 `assert(1==0)` 替换为带 message 的 `raise SyntaxError(...)`，错误定位会快很多。
