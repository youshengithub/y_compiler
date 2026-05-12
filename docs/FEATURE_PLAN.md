# Y Compiler 功能规划文档

> 版本: v2.0  
> 日期: 2026-05-12  
> 状态: 规划中

---

## 一、当前已支持功能清单

### 1.1 数据类型与变量
| 功能 | 状态 | 说明 |
|------|------|------|
| `int` 类型 | ✅ 已支持 | 整数类型声明与运算 |
| `double` 类型 | ⚠️ 部分 | 声明可以，但虚拟机内部全部用 `int()` 转换，无浮点运算支持 |
| `void` 类型 | ✅ 已支持 | 用于函数返回类型 |
| 标量变量 | ✅ 已支持 | `int a;` |
| 一维/多维数组 | ✅ 已支持 | `int a[10];`、`int a[3][3];`，固定常量下标访问正常 |
| 字符串初始化 | ✅ 已支持 | `int s[10]="Hello";`，逐字符存入内存 |

### 1.2 运算符
| 功能 | 状态 | 说明 |
|------|------|------|
| 算术 `+ - * / %` | ✅ 已支持 | 含优先级分层 (FACTOR > UNARY > OP) |
| 位运算 `& \| ^ !` | ✅ 已支持 | AND / OR / XOR / NOT |
| 比较 `== != < > <= >=` | ✅ 已支持 | |
| 逻辑 `&& \|\|` | ✅ 已支持 | 短路求值 |
| 取地址 `&` | ✅ 已支持 | LEA 指令 |
| 解引用 `*` | ✅ 已支持 | PUSH/POP + SEA 指令 |

### 1.3 控制流
| 功能 | 状态 | 说明 |
|------|------|------|
| `if / else` | ✅ 已支持 | 包含纯 if（已修复 Bug-14）|
| `while` | ✅ 已支持 | |
| `do-while` | ✅ 已支持 | |
| `for` | ✅ 已支持 | |
| 嵌套控制流 | ✅ 已支持 | if 嵌套、循环嵌套均正常 |

### 1.4 函数
| 功能 | 状态 | 说明 |
|------|------|------|
| 函数定义 | ⚠️ 部分 | 语法正确，栈帧创建/销毁有基本框架 |
| 函数调用 | ❌ 不可用 | ARG/tARG 参数传递未实现，实参无法正确压栈 |
| return 语句 | ⚠️ 部分 | 语法正确，`JMP END` 机制已有，但返回值无法被调用方获取 |
| 递归调用 | ❌ 不可用 | 栈帧保存/恢复使用固定偏移，递归会覆盖 |

### 1.5 结构体/类
| 功能 | 状态 | 说明 |
|------|------|------|
| struct/class 声明 | ⚠️ 部分 | 可解析语法，成员变量注册到符号表 |
| 成员变量访问 `a.b` | ⚠️ 部分 | VAR 节点有地址计算逻辑，但未经充分测试 |
| 成员函数(方法) | ❌ 不可用 | 无 this 指针，无方法调用机制 |
| 构造函数 | ❌ 不可用 | |
| 实例化 | ❌ 不可用 | DIM 不支持自定义类型声明 |

### 1.6 其他
| 功能 | 状态 | 说明 |
|------|------|------|
| `out()` 输出 | ✅ 已支持 | 单字符输出 (按 ASCII 码) |
| `in()` 输入 | ✅ 已支持 | 单字符读取 |
| `asm()` 内联汇编 | ✅ 已支持 | 直接注入 IR 代码 |
| `#define` 宏定义 | ✅ 已支持 | 简单文本替换 |
| `#include` 文件包含 | ✅ 已支持 | |
| `//` 注释 | ✅ 已支持 | 预处理器删除 |

---

## 二、待实现功能详细规划

### ═══════════════════════════════════════
### P0 优先级：核心功能（必须先做，后续功能依赖它们）
### ═══════════════════════════════════════

---

### 【F-01】函数参数传递 ⭐⭐⭐⭐⭐

**现状**：  
ARG 节点只处理了 `rule=="$OPN$"` 和 `rule=="$OP$"`（且 OP 直接 assert 报错），但实际上 ARG 会匹配到 `$tARG$` 规则，而 tARG 的编译分支只有 `for i in codelist: code+=i`，没有做实参的实际压栈。

**目标**：  
```c
int add(int a, int b) {
    return a + b;
}
int r;
r = add(30, 35);     // 常量参数
r = add(r, r+1);     // 表达式参数
out(r);
```

**需要修改的文件和内容**：

1. **`Compile_tree.py` — tARG 分支**
   - tARG 负责递归拆分参数列表（`$OP$,$tARG$` / `$OPN$,$tARG$` / `$OP$` / `$OPN$`）
   - 每个参数需要：计算值 → 存入 `memory[ESP+offset]` → ESP++
   - 对于 `$OPN$` 类型的简单参数：直接 `MOV $0:EAX oplist[0]` + `ADD ESP 1`
   - 对于 `$OP$` 类型的表达式参数：先执行 codelist 代码（结果在 EAX）→ `MOV $0:offset EAX` + `ADD ESP 1`

2. **`Compile_tree.py` — ARG 分支**
   - ARG 匹配到 `$tARG$` 时，直接使用 tARG 生成的代码
   - 删除现有的 ARG 分支中对 `$OPN$` / `$OP$` 的处理（因为实际不会匹配到）

3. **`Config.txt` — 可选调整**
   - 确认 ARG/tARG 规则正确

**测试验证**：
```c
// 测试1：常量参数
int add(int a, int b) { return a + b; }
out(add(30, 35));  // 期望输出: A (65)

// 测试2：变量参数
int x; int y;
x = 30; y = 35;
out(add(x, y));    // 期望输出: A

// 测试3：多参数
int sum3(int a, int b, int c) { return a + b + c; }
out(sum3(20, 20, 25));  // 期望输出: A
```

---

### 【F-02】函数返回值传递 ⭐⭐⭐⭐⭐

**现状**：  
`return expr` 会把结果放入 EAX 并 `JMP END`。FUNC 的尾声代码会恢复所有寄存器（包括 EAX），导致调用方拿到的 EAX 是调用前的旧值。

**目标**：  
```c
int double_it(int x) {
    return x * 2;
}
int r;
r = double_it(33);
out(r);  // 期望输出: B (66)
```

**需要修改的文件和内容**：

1. **`Compile_tree.py` — FUNC 尾声**
   - 在恢复寄存器时，**不恢复 EAX**（EAX 作为返回值通道）
   - 或者：在恢复 EAX 之前，先把返回值暂存到约定位置（如栈帧固定偏移），恢复后再取回
   - 推荐方案：return 把值放入 EAX → FUNC 尾声恢复 EBP/ESP/EBX/EFG/EIP，**跳过 EAX 的恢复**

2. **`Compile_tree.py` — CALL 之后**
   - 调用方在 JMP 返回后，EAX 即为返回值
   - `EQUAL` 的 `$VAR$=$OP$` 分支已经用 `MOV oplist[0] EAX`，如果 OP 是 CALL 则正确

**测试验证**：
```c
int get65() { return 65; }
int r;
r = get65();
out(r);  // 期望输出: A
```

---

### 【F-03】局部变量带初始化值 ⭐⭐⭐⭐

**现状**：  
`int a = 5;` 不支持（只支持 `int a;` 然后 `a = 5;`，或 `int s[10]="Hello";` 字符串初始化）。

**目标**：  
```c
int a = 65;
out(a);  // 期望输出: A

int b = 3 + 4;
// 暂不要求表达式初始化，先支持常量初始化
```

**需要修改的文件和内容**：

1. **`Config.txt`**  
   - DIM 规则新增：`$TYPE$$EMPTY$$TOKEN$=$CONST$` 或 `$TYPE$$EMPTY$$TOKEN$=$OPN$`
   - 当前 DIM 是：`$TYPE$$EMPTY$$TOKEN$=$STRING$` 和 `$TYPE$$EMPTY$$TOKEN$`
   - 新增规则处理数值初值：`$TYPE$$EMPTY$$TOKEN$=$OPN$`

2. **`Compile_tree.py` — DIM 分支**
   - 新增 `rule=="$TYPE$$EMPTY$$TOKEN$=$OPN$"` 的处理
   - 生成 `ALLOC size` + `MOV $start_pos value`
   - 后续可扩展为支持表达式初始化（`$TYPE$$EMPTY$$TOKEN$=$OP$`）

**测试验证**：
```c
int a = 65;
out(a);         // A
int b = 60;
int c = a + b;  // 这个需要 $OP$ 初始化支持
```

---

### 【F-04】数组变量下标访问 ⭐⭐⭐⭐

**现状**：  
VAR 节点可以为 `s[i]` 生成地址计算代码（结果在 EAX），但 PRINT/JUDGE/EQUAL 等节点用 `_addr(oplist[0])` 处理 `s[i]`，`_addr()` 不支持数组表达式。

**目标**：  
```c
int s[5];
int i;
s[0] = 65; s[1] = 66; s[2] = 67;
i = 0;
while(i < 3) {
    out(s[i]);    // 变量下标访问
    i = i + 1;
}
// 期望输出: ABC
```

**需要修改的文件和内容**：

1. **方案 A（推荐）：增强 `_addr()` 函数**
   - 当 `_addr()` 检测到 `op` 包含 `[` 或 `.` 时，不返回简单地址
   - 而是返回一段**前置代码** + **结果操作数**（如 `("MOV EAX...\n", "EAX")`）
   - 调用方（PRINT/JUDGE/EQUAL/算术）需要先插入前置代码，再使用结果操作数

2. **方案 B：统一走 codelist**
   - 所有涉及变量的 oplist 在编译时先检查是否为数组/结构体访问
   - 如果是，自动在前面插入 VAR 的地址计算代码

3. **影响范围**：
   - `_addr()` 函数签名和返回值改变
   - PRINT / JUDGE / EQUAL / ADD / SUB / MUL / DIV / MOD / AND / OR / XOR 所有用到 `_addr()` 的分支都要适配

**测试验证**：
```c
int a[3];
a[0]=65; a[1]=66; a[2]=67;
int i;
for(i=0; i<3; i=i+1) { out(a[i]); }
// 期望输出: ABC
```

---

### ═══════════════════════════════════════
### P1 优先级：重要功能（显著提升语言实用性）
### ═══════════════════════════════════════

---

### 【F-05】break / continue 语句 ⭐⭐⭐⭐

**现状**：  
Config.txt 中 `continue` 已列为关键词，但无语法规则、无翻译逻辑。

**目标**：  
```c
int i;
int sum;
sum = 0;
for(i = 0; i < 10; i = i + 1) {
    if(i == 5) { break; }
    sum = sum + 1;
}
// sum == 5

for(i = 0; i < 10; i = i + 1) {
    if(i % 2 == 0) { continue; }
    sum = sum + 1;
}
// sum 只累加奇数
```

**需要修改的文件和内容**：

1. **`Config.txt`**
   - SENTENCE 规则新增：`$BREAK$;` 和 `$CONTINUE$;`
   - 新增规则：`BREAK: break : NO_START`
   - 新增规则：`CONTINUE: continue : NO_START`

2. **`Compile_tree.py`**
   - 编译 BREAK 时生成 `JMP BREAK_END`（占位符）
   - 编译 CONTINUE 时生成 `JMP CONTINUE_POS`（占位符）
   - 在 WHILE / FOR / DO 的编译代码中，回填 BREAK_END 和 CONTINUE_POS
   - 需要一个**循环上下文栈**来追踪当前循环的跳转目标

3. **`Compile_tree.py` — 新增循环上下文管理**
   ```python
   loop_stack = []  # 每个元素 = {"break_label": str, "continue_label": str}
   ```

**测试验证**：
```c
int i; int r;
r = 0;
for(i=0; i<10; i=i+1) {
    if(i==3) { break; }
    r = r + 1;
}
r = r + 48;
out(r);  // 期望输出: 3
```

---

### 【F-06】全局变量 ⭐⭐⭐⭐

**现状**：  
所有变量都在当前作用域的顶级域中分配，函数内外无法共享变量。

**目标**：  
```c
int global_val;
global_val = 65;

void print_global() {
    out(global_val);
}

print_global();  // 期望输出: A
```

**需要修改的文件和内容**：

1. **`Compile_tree.py` / `Construct_tree.py`**
   - 编译器启动时创建的 Main area_tree 作为全局作用域
   - 函数内 `find_token()` 沿父链向上查找时，最终能查到全局域的变量
   - 全局变量使用**绝对地址**（`%start_pos`）而非相对地址（`$start_pos`）

2. **`runner.py`**
   - `calc_pos` 已支持 `%` 前缀表示绝对引用
   - 确认全局变量地址计算正确

3. **`_addr()` 函数**
   - 判断变量是否在全局域中定义
   - 如果是，使用 `%start_pos` 而非 `$start_pos`

**测试验证**：
```c
int g;
g = 65;
void show() { out(g); }
show();  // 期望输出: A
```

---

### 【F-07】复合赋值运算符 ⭐⭐⭐

**现状**：  
不支持 `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`。

**目标**：  
```c
int a;
a = 60;
a += 5;     // a == 65
out(a);     // 期望输出: A
```

**需要修改的文件和内容**：

1. **`Config.txt`**
   - EQUAL 规则扩展，新增：
     ```
     EQUAL: $VAR$+=$<OP|OPN>$ # $VAR$-=$<OP|OPN>$ # $VAR$*=$<OP|OPN>$ # ...
     ```

2. **`Compile_tree.py` — EQUAL 分支**
   - 检测 rule 中是否包含 `+=` / `-=` 等
   - 翻译为：读取左值 → 执行运算 → 写回
   - 例如 `a += 5` → `MOV EAX $addr_a` → `ADD EAX 5` → `MOV $addr_a EAX`

**测试验证**：
```c
int a; a = 60;
a += 5;   out(a);  // A (65)
a -= 1;   out(a);  // @ (64)
```

---

### 【F-08】自增/自减运算符 ⭐⭐⭐

**现状**：  
不支持 `i++`, `i--`, `++i`, `--i`。

**目标**：  
```c
int i;
i = 64;
i++;
out(i);    // 期望输出: A (65)
```

**需要修改的文件和内容**：

1. **`Config.txt`**
   - 方案一（作为语句）：SENTENCE 新增 `$VAR$++;` / `$VAR$--;`
   - 方案二（作为表达式）：UNARY 新增 `$VAR$++` / `++$VAR$`
   - 建议先做方案一（语句级），更简单

2. **`Compile_tree.py`**
   - `i++` → `ADD $addr_i 1`
   - `i--` → `SUB $addr_i 1`

**测试验证**：
```c
int i; i = 64;
i++;
out(i);  // A (65)
i--;
out(i);  // @ (64)
```

---

### 【F-09】递归调用 ⭐⭐⭐

**现状**：  
CALL 的栈帧保存使用相对于当前 ESP 的固定偏移（$0:EAX, $1:EAX...），第二次调用会覆盖第一次的保存区。

**目标**：  
```c
int factorial(int n) {
    if(n <= 1) { return 1; }
    return n * factorial(n - 1);
}
// factorial(5) == 120
```

**需要修改的文件和内容**：

1. **`Compile_tree.py` — CALL 分支**
   - 每次调用前，ESP 向上移动足够空间保存旧帧
   - 保存区域 = [旧ESP, 旧EBP, 旧EAX, 旧EBX, 旧EFG, 旧EIP]
   - 参数紧接在保存区域之后
   - 被调函数执行时 EBP 指向自己的栈帧起始
   - 返回时从固定偏移恢复

2. **`Compile_tree.py` — FUNC 尾声**
   - 使用 EBP 的相对偏移恢复寄存器（而非固定 $0:-6 等硬编码）

**依赖**：F-01、F-02 必须先完成

**测试验证**：
```c
int fact(int n) {
    if(n <= 1) { return 1; }
    return n * fact(n - 1);
}
int r;
r = fact(5);  // 120
// 输出 120 需要数字→字符串转换，可先用 asm 验证
```

---

### ═══════════════════════════════════════
### P2 优先级：类功能（面向对象支持）
### ═══════════════════════════════════════

---

### 【F-10】类实例化 — 自定义类型声明变量 ⭐⭐⭐⭐

**现状**：  
`struct Point { int x; int y; };` 可以定义结构体并注册到符号表，但 `Point p;` 无法声明实例变量（DIM 的 TYPE 只认 int/double/void）。

**目标**：  
```c
struct Point {
    int x;
    int y;
};

Point p;
p.x = 65;
out(p.x);  // 期望输出: A
```

**需要修改的文件和内容**：

1. **`Config.txt` — TYPE 规则扩展**
   - 当前：`TYPE: @^double@ # @^int@ # @^void@ # $TOKEN$`
   - TOKEN 分支理论上能匹配自定义类型名，但需确认 DIM 中 TYPE 匹配到自定义名后能正确查找结构体

2. **`Compile_tree.py` — DIM 分支**
   - 当 `type` 不是内置类型（int/double/void）时：
     - 在符号表中查找同名结构体：`area_tree.find_token(type)`
     - 获取结构体大小（`find_type.size`）
     - 为实例分配内存：`ALLOC struct_size`
     - 记录实例变量的 type 为结构体名，后续 `.` 访问时通过 type 找到结构体定义

3. **`Compile_tree.py` — VAR 的 `.` 访问**
   - 当前已有多段 `.` 访问逻辑
   - 确认：`p.x` 中 `p` 的 type 为 `"Point"`，通过 `find_token("Point")` 找到结构体
   - 然后在结构体的 `vars` 中找 `x`，获取其偏移

**测试验证**：
```c
struct Point { int x; int y; };
Point p;
p.x = 65;
p.y = 66;
out(p.x);  // A
out(p.y);  // B
```

---

### 【F-11】成员函数（方法）⭐⭐⭐⭐

**现状**：  
结构体内可以定义函数（语法上 STRUCTURE 的 AREA 内允许 FUNC），但：
- 方法体内无法隐式访问成员变量（无 this 指针）
- 外部无法通过 `obj.method()` 调用

**目标**：  
```c
struct Counter {
    int value;
    
    void inc() {
        value = value + 1;
    }
    
    int get() {
        return value;
    }
};

Counter c;
c.value = 0;
c.inc();
c.inc();
c.inc();
out(c.get());  // 期望输出: C (67 = 65+2... 不对，这里 3+48=51='3')
```

**需要修改的文件和内容**：

1. **`Config.txt`**
   - CALL 规则已有 `$TOKEN$.$CALL$`，理论上 `c.inc()` 能匹配
   - 需确认 CALL 的 oplist 中能获取到对象名和方法名

2. **`Compile_tree.py` — CALL 分支**
   - 检测 `$TOKEN$.$CALL$` 规则时：
     - `oplist[0]` 为方法名（最内层）
     - 前面的 TOKEN 为对象名
   - 调用方法时，隐式将**对象基地址**作为第一个参数压栈
   - 方法体内，通过该基地址 + 成员偏移来访问成员变量

3. **`Compile_tree.py` — 方法体内变量解析**
   - 方法编译时，`area_tree` 需要同时能访问：
     - 方法自身的局部变量
     - 所属结构体的成员变量（通过 this 基地址偏移）
   - 方案：在方法的 area_tree 中注入一个特殊的 `this` 变量
   - 成员访问翻译为：`MOV EAX $this_addr` → `ADD EAX member_offset` → 通过 EAX 间接访问

4. **`_addr()` / `Compile_tree.py`**
   - 方法内访问裸成员名时（如 `value`），需判断是否为所属类的成员
   - 如果是，自动翻译为 `this.value` 的间接访问

**测试验证**：
```c
struct Box {
    int val;
    void set(int v) { val = v; }
    int get_val() { return val; }
};
Box b;
b.set(65);
out(b.get_val());  // A
```

---

### 【F-12】构造函数 ⭐⭐⭐

**现状**：  
完全没有构造函数机制。

**目标**：  
```c
struct Point {
    int x;
    int y;
    
    void init(int ax, int ay) {
        x = ax;
        y = ay;
    }
};

Point p;
p.init(65, 66);
out(p.x);  // A
out(p.y);  // B
```

**需要修改的文件和内容**：

1. **约定构造函数名称**
   - 方案一：使用 `init` 作为构造函数名（Python 风格）
   - 方案二：使用与类同名的函数（C++ 风格）
   - 建议用方案一，实现更简单

2. **自动调用构造函数（可选增强）**
   - 基础版：手动调用 `p.init(...)` — 这只需要 F-11 成员函数即可
   - 增强版：`Point p(65, 66);` 自动调用构造函数
   - 增强版需要修改 Config.txt 的 DIM 规则，支持 `$TYPE$$EMPTY$$TOKEN$($ARG$)`

**依赖**：F-10、F-11 必须先完成

---

### 【F-13】析构函数（可选）⭐⭐

**现状**：  
无析构函数机制，也无动态内存管理（所有内存都是栈上分配）。

**目标**：  
```c
struct Resource {
    int handle;
    void destroy() {
        handle = 0;
        // 释放资源
    }
};
```

**说明**：  
由于当前编译器没有堆内存分配（没有 malloc/free），析构函数的作用有限。建议作为最低优先级，等堆内存支持后再考虑。

---

### 【F-14】运算符重载 ⭐⭐

**现状**：  
Config.txt 中有 `OPERATOR: $TYPE$--$OPS$--$FUNCNAME$($PAR$)$AREA$` 规则，但 Compile_tree 中完全没有处理。

**目标**：  
```c
struct Vec2 {
    int x;
    int y;
};

Vec2 int--+--vec_add(Vec2 a, Vec2 b) {
    Vec2 result;
    result.x = a.x + b.x;
    result.y = a.y + b.y;
    return result;
}
```

**说明**：  
运算符重载是高级特性，依赖 F-10（类实例化）和 F-11（方法），优先级较低。

---

### 【F-15】继承（组合方式）⭐⭐

**现状**：  
无继承机制。

**目标（通过组合模拟继承）**：  
```c
struct Animal {
    int legs;
    void set_legs(int n) { legs = n; }
};

struct Dog {
    Animal base;     // 组合继承
    int has_tail;
    void init() {
        base.set_legs(4);
        has_tail = 1;
    }
};
```

**说明**：  
真正的继承（虚函数表、多态）非常复杂。建议用**组合（composition）** 方式实现继承的效果——在子类中包含父类实例作为成员变量。这只需要 F-10 和 F-11 支持嵌套结构体即可。

---

### ═══════════════════════════════════════
### P3 优先级：语言完善（让编译器更实用）
### ═══════════════════════════════════════

---

### 【F-16】类型检查与类型转换 ⭐⭐⭐

**现状**：  
int 和 double 混用无警告，虚拟机全部用 `int()` 转换。

**目标**：  
- 编译期：检测类型不匹配时发出警告
- 运行时：`double` 变量保持浮点精度
- 支持显式类型转换：`(int)x`、`(double)y`

**需要修改的文件和内容**：

1. **`runner.py`**
   - 区分 int/double 的存储和运算
   - DIV 对 int 做整除，对 double 做浮点除

2. **`Compile_tree.py`**
   - 在运算节点中检查两侧操作数类型
   - 必要时插入类型转换指令

---

### 【F-17】switch/case 语句 ⭐⭐

**目标**：  
```c
int x;
x = 2;
switch(x) {
    case 1: out(65); break;
    case 2: out(66); break;
    default: out(67); break;
}
// 期望输出: B
```

**需要修改的文件和内容**：

1. **`Config.txt`**
   - 新增关键词：`switch`, `case`, `default`
   - 新增规则：
     ```
     SWITCH: switch($OPN$){$CASE$} :
     CASE: case$CONST$:$SENTENCE$break;$CASE$ # default:$SENTENCE$break; :NO_START# REPEAT#
     ```

2. **`Compile_tree.py`**
   - SWITCH 翻译为一系列 `EQUAL + JPIF + JMP` 的链式判断

---

### 【F-18】多返回值或 void 函数调用作为语句 ⭐⭐

**现状**：  
`call()` 作为语句时必须有返回值赋值（`r = call()`），不能直接 `call();`。

**目标**：  
```c
void hello() { out(72); out(105); }
hello();  // 直接调用，不需要赋值
```

**需要修改**：
- SENTENCE 中确保 `$CALL$;` 能正确匹配和编译

---

### 【F-19】数组作为函数参数（传指针）⭐⭐⭐

**目标**：  
```c
void fill(int arr[], int n, int val) {
    int i;
    for(i = 0; i < n; i = i + 1) {
        arr[i] = val;
    }
}

int data[5];
fill(data, 5, 65);
out(data[0]);  // A
```

**需要修改**：
- 数组参数传递其基地址（LEA 取地址 → 压栈）
- 被调函数内通过该地址 + 偏移访问数组元素

---

### 【F-20】负数字面量修正 ⭐⭐

**现状**：  
Config.txt 中 `CONST: @^<-|>[0-9]{1,255}@` 的 `<-|>` 展开为 `-` 或空字符串。空字符串的正则 `@^[0-9]{1,255}@` 是正确的，但 `-` 的正则 `@^-[0-9]{1,255}@` 需要确认负号不被 SUB 运算符消费。

**需要修改**：
- 确认负数常量（如 `-5`）在各种上下文中正确解析
- 测试 `int a; a = -5;` 和 `int a; a = 0 - 5;` 的差异

---

### 【F-21】字符串操作库 ⭐⭐

**目标**：  
提供内置函数：`strlen(s)`、`strcpy(dst, src)`、`strcmp(a, b)` 等。

**实现方式**：  
可以用编译器内置函数（hardcoded IR 序列）或用 .y 标准库文件 + `#include` 引入。

---

### 【F-22】多行注释 `/* */` ⭐

**现状**：  
预处理器只处理 `//` 单行注释。

**需要修改**：  
`preprocesser.py` 的 `process_note()` 增加 `/* ... */` 多行注释删除逻辑。

---

### 【F-23】数字输出（OUT 增强）⭐⭐⭐

**现状**：  
`out()` 只能输出 ASCII 字符（`chr(value)`），要输出数字 `65` 需要自己转换。

**目标**：  
```c
int a;
a = 65;
out(a);        // 输出字符 A（现有行为）
outnum(a);     // 输出数字 65（新功能）
outstr(s);     // 输出字符串（新功能）
```

**需要修改**：
1. **`Config.txt`** — 新增 PRINT 规则变体
2. **`Compile_tree.py`** — 新增 `OUTNUM` / `OUTSTR` IR 指令的生成
3. **`runner.py`** — 新增 `OUTNUM` / `OUTSTR` 指令的执行

---

### 【F-24】错误恢复与多错误报告 ⭐

**现状**：  
遇到第一个解析错误就停止，只报告一个错误。

**目标**：  
- 解析器尝试跳过错误行，继续解析后续代码
- 报告所有发现的错误（最多 N 个）

---

## 三、实现顺序建议

```
阶段 1 — 函数打通（约 3-5 天）
  ├── F-01 函数参数传递          ← 最先做
  ├── F-02 函数返回值传递        ← 紧接着做
  ├── F-03 局部变量带初始化值
  └── F-04 数组变量下标访问

阶段 2 — 控制流增强（约 2-3 天）
  ├── F-05 break / continue
  ├── F-07 复合赋值 += -=
  ├── F-08 自增自减 i++ i--
  └── F-20 负数字面量修正

阶段 3 — 类功能（约 5-7 天）
  ├── F-10 类实例化              ← 先做这个
  ├── F-11 成员函数（方法）      ← 核心难点
  ├── F-12 构造函数
  └── F-15 继承（组合方式）

阶段 4 — 函数高级特性（约 3 天）
  ├── F-06 全局变量
  ├── F-09 递归调用
  └── F-19 数组作为函数参数

阶段 5 — 语言完善（按需）
  ├── F-16 类型检查
  ├── F-17 switch/case
  ├── F-18 void 函数直接调用
  ├── F-22 多行注释
  ├── F-23 数字输出
  └── F-24 错误恢复
```

---

## 四、已修复的 Bug 记录

| Bug ID | 描述 | 修复状态 |
|--------|------|----------|
| Bug-01~13 | fix 分支初始修复（详见 FIXES.md）| ✅ 已修复 |
| Bug-14 | 纯 if 语句 IndexError | ✅ 已修复 |
| Bug-15 | DIM 字符串 start_pos 类型不一致 | ✅ 已修复 |
| Bug-16 | 空代码块 NOPs → NOP | ✅ 已修复 |
| Bug-17 | msvcrt 跨平台兼容 | ✅ 已修复 |
| Bug-18 | DIM 字符串 MOV 缺少 $ 前缀 | ✅ 已修复 |
| Bug-18b | DIM 字符串 append_var 缺少 size | ✅ 已修复 |

---

## 五、虚拟机指令集（当前）

| 指令 | 格式 | 说明 |
|------|------|------|
| ALLOC | `ALLOC n` | 栈顶分配 n 个单元 |
| MOV | `MOV dst src` | 数据传送 |
| ADD | `ADD dst src` | dst += src |
| SUB | `SUB dst src` | dst -= src |
| MUL | `MUL dst src` | dst *= src |
| DIV | `DIV dst src` | dst /= src |
| MOD | `MOD dst src` | dst %= src |
| AND | `AND dst src` | dst &= src |
| OR | `OR dst src` | dst \|= src |
| XOR | `XOR dst src` | dst ^= src |
| NOT | `NOT dst src` | dst = ~src |
| LEA | `LEA dst src` | dst = &src (取地址) |
| SEA | `SEA dst src` | *dst = src (间接写) |
| PUSH | `PUSH src` | memory[ESP] = src; ESP++ |
| POP | `POP dst` | ESP--; dst = memory[ESP] |
| EQUAL | `EQUAL a b` | EFG = !(a == b) |
| LESS | `LESS a b` | EFG = !(a < b) |
| GREATER | `GREATER a b` | EFG = !(a > b) |
| LE | `LE a b` | EFG = !(a <= b) |
| GE | `GE a b` | EFG = !(a >= b) |
| RF | `RF` | EFG = !EFG |
| JPIF | `JPIF offset` | if EFG: EIP += offset |
| JPNIF | `JPNIF offset` | if !EFG: EIP += offset |
| JMP | `JMP offset` | EIP += offset |
| OUT | `OUT src` | print(chr(src)) |
| IN | `IN dst` | dst = ord(getch()) |
| NOP | `NOP` | 空操作 |

**寄存器**：EAX, EBX, ESP, EBP, EIP, EFG, ETP

**操作数格式**：
- `123` — 立即数
- `$n` — 相对地址：memory[EBP + n]
- `$n:m` — 相对地址带偏移：memory[EBP + n + m]
- `$n:$m` — 相对地址带间接偏移：memory[EBP + n + memory[EBP + m]]
- `%n` — 绝对地址：memory[n]（不加 EBP）
