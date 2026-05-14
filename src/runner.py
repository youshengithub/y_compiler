#IR支持扩展指令集
#ALLOC MOV ADD SUB MUL DIV AND OR NOR XOR MOD LEA
#GREATER EQUAL LESS JPIF JPNIF JMP OUT RF TO NOP
#PUSH POP IN SEA OUTNUM
# --- 新增指令 ---
#SHL SHR (位移)
#FMOV FADD FSUB FMUL FDIV (浮点运算)
#MALLOC FREE (堆内存)
#PRINTF (格式化输出)
#HALT (停机)
import time
import sys

# 跨平台 getch 实现
try:
    import msvcrt
    def _getch():
        return msvcrt.getch()
except ImportError:
    import tty, termios
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode('utf-8')

class HeapManager:
    """简单的堆内存管理器 — 使用首次适配算法"""
    def __init__(self, memory, heap_start, heap_size):
        self.memory = memory
        self.heap_start = heap_start
        self.heap_size = heap_size
        # 空闲块列表：[(start, size), ...]
        self.free_list = [(heap_start, heap_size)]
        self.alloc_map = {}  # addr → size

    def malloc(self, size):
        """分配 size 个内存单元，返回起始地址；失败返回 0"""
        for i, (start, block_size) in enumerate(self.free_list):
            if block_size >= size:
                # 找到足够大的块
                self.alloc_map[start] = size
                if block_size == size:
                    self.free_list.pop(i)
                else:
                    self.free_list[i] = (start + size, block_size - size)
                return start
        return 0  # 分配失败

    def free(self, addr):
        """释放之前分配的内存"""
        if addr not in self.alloc_map:
            return  # 无效 free
        size = self.alloc_map.pop(addr)
        # 插入到空闲列表并合并相邻块
        self.free_list.append((addr, size))
        self.free_list.sort()
        # 合并相邻空闲块
        merged = []
        for start, sz in self.free_list:
            if merged and merged[-1][0] + merged[-1][1] == start:
                merged[-1] = (merged[-1][0], merged[-1][1] + sz)
            else:
                merged.append((start, sz))
        self.free_list = merged


class Runner:
    def __init__(self) -> None:
        self.debug_mode = False
        self.breakpoints = set()
        self.step_mode = False
        self.perf_counter = {}
        self.total_instructions = 0
        self.max_stack_depth = 0

    def set_debug(self, enabled=True):
        self.debug_mode = enabled

    def add_breakpoint(self, line):
        self.breakpoints.add(line)

    def remove_breakpoint(self, line):
        self.breakpoints.discard(line)

    def get_perf_stats(self):
        return {
            "total_instructions": self.total_instructions,
            "instruction_counts": dict(sorted(self.perf_counter.items(), key=lambda x: -x[1])),
            "max_stack_depth": self.max_stack_depth,
        }

    def dump_memory(self, start=0, count=20):
        print(f"  Memory[{start}:{start+count}]:")
        for i in range(start, min(start+count, len(self.memory))):
            val = self.memory[i]
            if val != 0:
                print(f"    [{i}] = {val}", end="")
                if isinstance(val, (int, float)) and 32 <= int(val) <= 126:
                    print(f"  (\'{chr(int(val))}\')", end="")
                print()

    def dump_registers(self, REGS):
        print("  Registers:")
        for name, addr in REGS.items():
            print(f"    {name} = {self.memory[addr]}")

    def calc_pos(self, text, REGS):
        if text.startswith("@"):
            inner = text[1:]
            parts = inner.split(":")
            base = int(parts[0])
            this_addr = int(self.memory[int(self.memory[REGS["EBP"]]) + base])
            if len(parts) == 2:
                offset = int(parts[1])
                return "pos", this_addr + offset
            elif len(parts) == 3:
                base_offset = int(parts[1])
                idx_part = parts[2]
                if idx_part.startswith("@"):
                    idx_offset = int(idx_part[1:])
                    idx_val = int(self.memory[this_addr + idx_offset])
                elif idx_part.startswith("$"):
                    idx_pos = int(idx_part[1:])
                    idx_val = int(self.memory[int(self.memory[REGS["EBP"]]) + idx_pos])
                else:
                    idx_val = int(idx_part)
                return "pos", this_addr + base_offset + idx_val
            else:
                return "pos", this_addr
        if text.startswith("~"):
            inner = text[1:]
            parts = inner.split(":")
            arr_pos = int(parts[0])
            base_addr = int(self.memory[int(self.memory[REGS["EBP"]]) + arr_pos])
            if len(parts) == 2:
                idx_part = parts[1]
                if idx_part.startswith("$"):
                    idx_var_pos = int(idx_part[1:])
                    idx_val = int(self.memory[int(self.memory[REGS["EBP"]]) + idx_var_pos])
                else:
                    idx_val = int(idx_part)
                return "pos", base_addr + idx_val
            else:
                return "pos", base_addr
        if "$" in text:
            ans = 0
            texts = text.split(":")
            ans = int(texts[0][1:])
            if len(texts) == 2:
                if texts[1].startswith("$"):
                    ans += int(self.memory[int(self.memory[REGS["EBP"]]) + int(texts[1][1:])])
                else:
                    ans += int(texts[1])
            else:
                if ans < 0:
                    return "pos", ans
            if "%" in text:
                return "pos", ans
            else:
                return "pos", int(ans + self.memory[REGS["EBP"]])
        elif text.startswith("%"):
            inner = text[1:]
            if ":" in inner:
                parts = inner.split(":")
                ans = int(parts[0])
                if parts[1].startswith("$"):
                    ans += int(self.memory[int(self.memory[REGS["EBP"]]) + int(parts[1][1:])])
                else:
                    ans += int(parts[1])
                return "pos", ans
            else:
                ans = int(inner)
                return "pos", ans
        else:
            # 尝试浮点数
            try:
                val = float(text)
                if '.' in text:
                    return "real", val
                else:
                    return "real", int(text)
            except ValueError:
                return "real", int(text)

    def RUN(self, lines):
        REGS = {"EAX": -1, "EBX": -2, "EBP": -3, "ESP": -4, "EIP": -5, "EFG": -6, "ETP": -7}
        self.max_memory = 100000
        HEAP_START = 80000  # 堆起始地址
        HEAP_SIZE = 20000   # 堆大小
        self.memory = [0 for i in range(self.max_memory + len(REGS))]
        self.heap = HeapManager(self.memory, HEAP_START, HEAP_SIZE)

        keywordss = []
        for line in lines:
            for k, v in REGS.items():
                if k in line:
                    line = line.replace(k, "$" + str(v))
            print(line)
            keywordss.append(line.split(" "))
        print("**********execing*********")
        start_time = time.time()
        self.perf_counter = {}
        self.total_instructions = 0
        self.max_stack_depth = 0

        while True:
            ip = self.memory[REGS["EIP"]]
            if ip >= len(lines):
                break
            keywords = keywordss[int(ip)]

            self.total_instructions += 1
            instr_name = keywords[0]
            self.perf_counter[instr_name] = self.perf_counter.get(instr_name, 0) + 1
            current_esp = int(self.memory[REGS["ESP"]])
            if current_esp > self.max_stack_depth:
                self.max_stack_depth = current_esp

            # 调试模式
            if self.debug_mode:
                if int(ip) in self.breakpoints or self.step_mode:
                    print(f"\n  ⏸ Break at line {int(ip)}: {' '.join(keywords)}")
                    self.dump_registers(REGS)
                    while True:
                        cmd = input("  debug> ").strip()
                        if cmd in ("", "n", "next"):
                            self.step_mode = True
                            break
                        elif cmd in ("c", "continue"):
                            self.step_mode = False
                            break
                        elif cmd in ("r", "regs"):
                            self.dump_registers(REGS)
                        elif cmd.startswith("m") or cmd.startswith("mem"):
                            parts = cmd.split()
                            sa = int(parts[1]) if len(parts) > 1 else 0
                            cnt = int(parts[2]) if len(parts) > 2 else 20
                            self.dump_memory(sa, cnt)
                        elif cmd in ("s", "stack"):
                            ebp = int(self.memory[REGS["EBP"]])
                            esp = int(self.memory[REGS["ESP"]])
                            print(f"  Stack (EBP={ebp}, ESP={esp}):")
                            self.dump_memory(ebp, esp - ebp + 1)
                        elif cmd in ("q", "quit"):
                            return
                        elif cmd in ("p", "perf"):
                            stats = self.get_perf_stats()
                            print(f"  Instructions executed: {stats['total_instructions']}")
                            print(f"  Max stack depth: {stats['max_stack_depth']}")
                            top5 = list(stats['instruction_counts'].items())[:5]
                            for name, cnt in top5:
                                print(f"    {name}: {cnt}")
                        else:
                            print("  Commands: n(ext), c(ontinue), r(egs), m(em) [addr] [count], s(tack), p(erf), q(uit)")

            if len(keywords) >= 2: flag1, op1 = self.calc_pos(keywords[1], REGS)
            if len(keywords) >= 3: flag2, op2 = self.calc_pos(keywords[2], REGS)

            if keywords[0] == "ALLOC":
                target = self.memory[REGS["EBP"]] + op1 + 1
                if target >= self.max_memory:
                    print("栈溢出！")
                    return
                else:
                    if target > self.memory[REGS["ESP"]]:
                        self.memory[REGS["ESP"]] = target
            elif keywords[0] == "MOV":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = self.memory[op2]
                else:
                    self.memory[op1] = op2
                if op1 == REGS["EIP"]:
                    continue
            elif keywords[0] == "ADD":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] += self.memory[op2]
                else:
                    self.memory[op1] += op2
            elif keywords[0] == "SUB":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] -= self.memory[op2]
                else:
                    self.memory[op1] -= op2
            elif keywords[0] == "MUL":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] *= self.memory[op2]
                else:
                    self.memory[op1] *= op2
            elif keywords[0] == "DIV":
                assert flag1 == "pos"
                if flag2 == "pos":
                    divisor = self.memory[op2]
                else:
                    divisor = op2
                dividend = self.memory[op1]
                # 如果任一为浮点数，用浮点除法
                if isinstance(dividend, float) or isinstance(divisor, float):
                    self.memory[op1] = float(dividend) / float(divisor) if divisor != 0 else 0
                else:
                    self.memory[op1] = int(dividend) // int(divisor) if divisor != 0 else 0
            elif keywords[0] == "AND":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) & int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) & int(op2)
            elif keywords[0] == "OR":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) | int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) | int(op2)
            elif keywords[0] == "XOR":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) ^ int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) ^ int(op2)
            elif keywords[0] == "MOD":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) % int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) % int(op2)
            elif keywords[0] == "NOT":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = ~int(self.memory[op2])
                else:
                    self.memory[op1] = ~int(op2)
            # ── 位移运算 ──
            elif keywords[0] == "SHL":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) << int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) << int(op2)
            elif keywords[0] == "SHR":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op1]) >> int(self.memory[op2])
                else:
                    self.memory[op1] = int(self.memory[op1]) >> int(op2)
            # ── 浮点运算 ──
            elif keywords[0] == "FMOV":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = float(self.memory[op2])
                else:
                    self.memory[op1] = float(op2)
                if op1 == REGS["EIP"]:
                    continue
            elif keywords[0] == "FADD":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = float(self.memory[op1]) + float(self.memory[op2])
                else:
                    self.memory[op1] = float(self.memory[op1]) + float(op2)
            elif keywords[0] == "FSUB":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = float(self.memory[op1]) - float(self.memory[op2])
                else:
                    self.memory[op1] = float(self.memory[op1]) - float(op2)
            elif keywords[0] == "FMUL":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = float(self.memory[op1]) * float(self.memory[op2])
                else:
                    self.memory[op1] = float(self.memory[op1]) * float(op2)
            elif keywords[0] == "FDIV":
                assert flag1 == "pos"
                if flag2 == "pos":
                    d = float(self.memory[op2])
                else:
                    d = float(op2)
                self.memory[op1] = float(self.memory[op1]) / d if d != 0 else 0.0
            elif keywords[0] == "FTOI":
                # 浮点转整数
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = int(self.memory[op2])
                else:
                    self.memory[op1] = int(op2)
            elif keywords[0] == "ITOF":
                # 整数转浮点
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[op1] = float(self.memory[op2])
                else:
                    self.memory[op1] = float(op2)
            # ── 堆内存 ──
            elif keywords[0] == "MALLOC":
                # MALLOC dst size — 分配 size 个单元，地址存入 dst
                assert flag1 == "pos"
                if flag2 == "pos":
                    size = int(self.memory[op2])
                else:
                    size = int(op2)
                addr = self.heap.malloc(size)
                self.memory[op1] = addr
            elif keywords[0] == "FREE":
                # FREE src — 释放 src 指向的地址
                if flag1 == "pos":
                    addr = int(self.memory[op1])
                else:
                    addr = int(op1)
                self.heap.free(addr)
            # ── 格式化输出 ──
            elif keywords[0] == "PRINTF":
                # PRINTF fmt_addr arg_count
                # 从 fmt_addr 开始读取格式字符串，然后按 arg_count 个参数输出
                if flag1 == "pos":
                    fmt_addr = int(self.memory[op1])
                else:
                    fmt_addr = int(op1)
                if flag2 == "pos":
                    arg_count = int(self.memory[op2])
                else:
                    arg_count = int(op2)
                # 读取格式字符串
                fmt_str = ""
                pos = fmt_addr
                while self.memory[pos] != 0:
                    fmt_str += chr(int(self.memory[pos]))
                    pos += 1
                # 从栈上读取参数（参数按顺序压入 ETP 之后）
                args = []
                etp = int(self.memory[REGS["ETP"]])
                for i in range(arg_count):
                    args.append(self.memory[etp + i])
                # 解析格式字符串并输出
                output = self._format_printf(fmt_str, args)
                print(output, end="", flush=True)
            # ── 停机 ──
            elif keywords[0] == "HALT":
                break
            elif keywords[0] == "LEA":
                assert flag1 == "pos"
                if flag2 == "pos":
                    if op1 == op2:
                        self.memory[op1] = self.memory[int(self.memory[op2])]
                    else:
                        self.memory[op1] = self.memory[int(self.memory[op2])]
                else:
                    self.memory[op1] = op2
            elif keywords[0] == "SEA":
                assert flag1 == "pos"
                if flag2 == "pos":
                    self.memory[int(self.memory[op1])] = self.memory[op2]
                else:
                    self.memory[int(self.memory[op1])] = op2
            elif keywords[0] == "PUSH":
                sp = self.memory[REGS["ESP"]]
                if flag1 == "pos":
                    self.memory[int(sp)] = self.memory[op1]
                else:
                    self.memory[int(sp)] = op1
                self.memory[REGS["ESP"]] = sp + 1
            elif keywords[0] == "POP":
                assert flag1 == "pos"
                sp = self.memory[REGS["ESP"]] - 1
                self.memory[REGS["ESP"]] = sp
                self.memory[op1] = self.memory[int(sp)]
            elif keywords[0] == "GREATER":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a > b)
            elif keywords[0] == "EQUAL":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a == b)
            elif keywords[0] == "LESS":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a < b)
            elif keywords[0] == "LE":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a <= b)
            elif keywords[0] == "GE":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a >= b)
            elif keywords[0] == "NE":
                if flag1 == "pos":
                    a = self.memory[op1]
                else:
                    a = op1
                if flag2 == "pos":
                    b = self.memory[op2]
                else:
                    b = op2
                self.memory[REGS["EFG"]] = not (a != b)
            elif keywords[0] == "RF":
                self.memory[REGS["EFG"]] = not self.memory[REGS["EFG"]]
            elif keywords[0] == "JPIF":
                if self.memory[REGS["EFG"]] == True:
                    if flag1 == "real":
                        self.memory[REGS["EIP"]] += op1
                    else:
                        self.memory[REGS["EIP"]] += self.memory[op1]
                    continue
            elif keywords[0] == "JPNIF":
                if self.memory[REGS["EFG"]] == False:
                    if flag1 == "real":
                        self.memory[REGS["EIP"]] += op1
                    else:
                        self.memory[REGS["EIP"]] += self.memory[op1]
                    continue
            elif keywords[0] == "JMP":
                if flag1 == "real":
                    self.memory[REGS["EIP"]] += op1
                else:
                    self.memory[REGS["EIP"]] += self.memory[op1]
                continue
            elif keywords[0] == "OUT":
                if flag1 == "pos":
                    print(chr(int(self.memory[op1])), end="", flush=True)
                else:
                    print(chr(int(op1)), end="", flush=True)
            elif keywords[0] == "OUTNUM":
                if flag1 == "pos":
                    val = self.memory[op1]
                else:
                    val = op1
                # 浮点数显示为小数，整数显示为整数
                if isinstance(val, float) and val != int(val):
                    print(f"{val:.6g}", end="", flush=True)
                else:
                    print(int(val), end="", flush=True)
            elif keywords[0] == "IN":
                char = _getch()
                assert flag1 == "pos"
                self.memory[op1] = ord(char)
            elif keywords[0] == "NOP":
                pass
            elif keywords[0] == "TO":
                pass

            self.memory[REGS["EIP"]] += 1
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n虚拟机执行时间: {elapsed_time} 秒")

    def _format_printf(self, fmt, args):
        """解析类C格式字符串"""
        result = ""
        arg_idx = 0
        i = 0
        while i < len(fmt):
            if fmt[i] == '%' and i + 1 < len(fmt):
                i += 1
                if fmt[i] == 'd':
                    result += str(int(args[arg_idx])) if arg_idx < len(args) else "?"
                    arg_idx += 1
                elif fmt[i] == 'f':
                    result += f"{float(args[arg_idx]):.6f}" if arg_idx < len(args) else "?"
                    arg_idx += 1
                elif fmt[i] == 'c':
                    result += chr(int(args[arg_idx])) if arg_idx < len(args) else "?"
                    arg_idx += 1
                elif fmt[i] == 's':
                    # 字符串：从地址读到\0
                    if arg_idx < len(args):
                        addr = int(args[arg_idx])
                        s = ""
                        while self.memory[addr] != 0:
                            s += chr(int(self.memory[addr]))
                            addr += 1
                        result += s
                    arg_idx += 1
                elif fmt[i] == '%':
                    result += '%'
                else:
                    result += '%' + fmt[i]
            elif fmt[i] == '\\' and i + 1 < len(fmt):
                i += 1
                if fmt[i] == 'n':
                    result += '\n'
                elif fmt[i] == 't':
                    result += '\t'
                else:
                    result += '\\' + fmt[i]
            else:
                result += fmt[i]
            i += 1
        return result

    def Run_from_code(self, lines):
        print("********SYSTEM RUNNING********")
        self.RUN(lines)

    def Run_from_file(self, file_path):
        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                lines.append(line.strip())
        self.RUN(lines)

if __name__ == "__main__":
    a = Runner()
    a.Run_from_file("IR.txt")
