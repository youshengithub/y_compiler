#IR支持22种指令
#ALLOC
#MOV
#ADD
#SUB
#MUL
#DIV
#AND
#OR
#NOR
#XOR
#MOD
#LEA
#GREATER
#EQUAL
#LESS
#JPIF
#JPNIF
#JMP
#OUT
#RF
#TO  操作数 [%|]$address[:[$|]address] %表示绝对引用  $表示相对与EBP的位置
#NOP
#PUSH
#POP
#IN
import time
import sys
import cProfile

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
# 记录开始时间

class Runner:
    def __init__(self) -> None:
        self.debug_mode = False
        self.breakpoints = set()  # 行号集合
        self.step_mode = False    # 单步执行
        self.perf_counter = {}    # 指令 → 执行次数
        self.total_instructions = 0
        self.max_stack_depth = 0

    def set_debug(self, enabled=True):
        """启用/禁用调试模式"""
        self.debug_mode = enabled

    def add_breakpoint(self, line):
        """添加断点"""
        self.breakpoints.add(line)

    def remove_breakpoint(self, line):
        """删除断点"""
        self.breakpoints.discard(line)

    def get_perf_stats(self):
        """获取性能统计"""
        return {
            "total_instructions": self.total_instructions,
            "instruction_counts": dict(sorted(self.perf_counter.items(), key=lambda x: -x[1])),
            "max_stack_depth": self.max_stack_depth,
        }

    def dump_memory(self, start=0, count=20):
        """打印内存内容"""
        print(f"  Memory[{start}:{start+count}]:")
        for i in range(start, min(start+count, len(self.memory))):
            val = self.memory[i]
            if val != 0:
                print(f"    [{i}] = {int(val)}", end="")
                if 32 <= int(val) <= 126:
                    print(f"  ('{chr(int(val))}')", end="")
                print()

    def dump_registers(self, REGS):
        """打印寄存器"""
        print("  Registers:")
        for name, addr in REGS.items():
            print(f"    {name} = {int(self.memory[addr])}")
    def calc_pos(self,text,REGS): #通过此来计算和数据
        if text.startswith("@"):
            # 间接寻址：通过 this 指针访问结构体成员
            inner = text[1:]
            parts = inner.split(":")
            base = int(parts[0])  # this_pos
            # this_addr = memory[EBP + this_pos]
            this_addr = int(self.memory[int(self.memory[REGS["EBP"]]) + base])
            if len(parts) == 2:
                # @this_pos:offset → memory[this_addr + offset]
                offset = int(parts[1])
                return "pos", this_addr + offset
            elif len(parts) == 3:
                # @this_pos:base_offset:@idx_offset 或 @this_pos:base_offset:$idx_pos
                base_offset = int(parts[1])
                idx_part = parts[2]
                if idx_part.startswith("@"):
                    # idx 也是结构体成员：memory[this_addr + idx_offset]
                    idx_offset = int(idx_part[1:])
                    idx_val = int(self.memory[this_addr + idx_offset])
                elif idx_part.startswith("$"):
                    # idx 是局部变量：memory[EBP + idx_pos]
                    idx_pos = int(idx_part[1:])
                    idx_val = int(self.memory[int(self.memory[REGS["EBP"]]) + idx_pos])
                else:
                    idx_val = int(idx_part)
                return "pos", this_addr + base_offset + idx_val
            else:
                # 单段 @pos（不太可能但防御性处理）
                return "pos", this_addr
        if text.startswith("~"):
            # 参数数组间接寻址：~pos:idx → memory[memory[EBP + pos] + idx]
            inner = text[1:]
            parts = inner.split(":")
            arr_pos = int(parts[0])
            # 基地址 = memory[EBP + arr_pos]（传入的数组绝对地址）
            base_addr = int(self.memory[int(self.memory[REGS["EBP"]]) + arr_pos])
            if len(parts) == 2:
                idx_part = parts[1]
                if idx_part.startswith("$"):
                    # 变量下标：memory[EBP + idx_var_pos]
                    idx_var_pos = int(idx_part[1:])
                    idx_val = int(self.memory[int(self.memory[REGS["EBP"]]) + idx_var_pos])
                else:
                    idx_val = int(idx_part)
                return "pos", base_addr + idx_val
            else:
                return "pos", base_addr
        if("$"  in text):
            ans=0
            texts=text.split(":")
            ans=int(texts[0][1:])
            if(len(texts)==2):
                if(texts[1].startswith("$")):
                    ans+=int(self.memory[int(self.memory[REGS["EBP"]])+int(texts[1][1:])])
                else:
                    ans+=int(texts[1])
            else:
                #只有一段，并且很明显是寄存器的区域,则不需要加ebp,因为这是在对寄存器寻址
                if(ans<0 ): 
                    return "pos",ans
            if("%" in text): #如果标记了是% 那就不需要加入基址
                return "pos",ans
            else:
                 return "pos",ans+self.memory[REGS["EBP"]]
        elif text.startswith("%"):
            # 绝对地址：%n → memory[n]（不加EBP）
            # 支持 %base:idx 格式
            inner = text[1:]
            if ":" in inner:
                parts = inner.split(":")
                ans = int(parts[0])
                if parts[1].startswith("$"):
                    # %base:$var_pos → memory[base + memory[EBP + var_pos]]
                    ans += int(self.memory[int(self.memory[REGS["EBP"]]) + int(parts[1][1:])])
                else:
                    ans += int(parts[1])
                return "pos", ans
            else:
                ans = int(inner)
                return "pos", ans
        else:
            return "real",int(text)
            
    def RUN(self,lines): #注意到操作数可以是real $1 var
        REGS={"EAX":-1, "EBX":-2,"EBP":-3,"ESP":-4,"EIP":-5,"EFG":-6,"ETP":-7}
        self.max_memory=100000
        self.memory=[0 for i in range(self.max_memory+len(REGS))]
        
        keywordss=[]
        for line in lines:
            for k,v in REGS.items():
                if(k in line):
                    line=line.replace(k,"$"+str(v))
            print(line)
            keywordss.append(line.split(" "))
        print("**********execing*********")
        start_time = time.time()
        self.perf_counter = {}
        self.total_instructions = 0
        self.max_stack_depth = 0
        while(True):
            
            ip=self.memory[REGS["EIP"]]
            if(ip>=len(lines)):
                break
            keywords=keywordss[ip]

            # ── 性能计数 ──
            self.total_instructions += 1
            instr_name = keywords[0]
            self.perf_counter[instr_name] = self.perf_counter.get(instr_name, 0) + 1
            # 追踪最大栈深度
            current_esp = int(self.memory[REGS["ESP"]])
            if current_esp > self.max_stack_depth:
                self.max_stack_depth = current_esp

            # ── 调试模式 ──
            if self.debug_mode:
                if int(ip) in self.breakpoints or self.step_mode:
                    print(f"\n  ⏸ Break at line {int(ip)}: {' '.join(keywords)}")
                    self.dump_registers(REGS)
                    while True:
                        cmd = input("  debug> ").strip()
                        if cmd == "" or cmd == "n" or cmd == "next":
                            self.step_mode = True
                            break
                        elif cmd == "c" or cmd == "continue":
                            self.step_mode = False
                            break
                        elif cmd == "r" or cmd == "regs":
                            self.dump_registers(REGS)
                        elif cmd.startswith("m") or cmd.startswith("mem"):
                            parts = cmd.split()
                            start_addr = int(parts[1]) if len(parts) > 1 else 0
                            count = int(parts[2]) if len(parts) > 2 else 20
                            self.dump_memory(start_addr, count)
                        elif cmd == "s" or cmd == "stack":
                            ebp = int(self.memory[REGS["EBP"]])
                            esp = int(self.memory[REGS["ESP"]])
                            print(f"  Stack (EBP={ebp}, ESP={esp}):")
                            self.dump_memory(ebp, esp - ebp + 1)
                        elif cmd == "q" or cmd == "quit":
                            return
                        elif cmd == "p" or cmd == "perf":
                            stats = self.get_perf_stats()
                            print(f"  Instructions executed: {stats['total_instructions']}")
                            print(f"  Max stack depth: {stats['max_stack_depth']}")
                            top5 = list(stats['instruction_counts'].items())[:5]
                            for name, cnt in top5:
                                print(f"    {name}: {cnt}")
                        else:
                            print("  Commands: n(ext), c(ontinue), r(egs), m(em) [addr] [count], s(tack), p(erf), q(uit)")

            if(len(keywords)>=2):flag1,op1=self.calc_pos(keywords[1],REGS)
            if(len(keywords)>=3):flag2,op2=self.calc_pos(keywords[2],REGS)
            if(keywords[0]=="ALLOC"):
                # ALLOC N: 确保栈帧至少到 EBP + N + 1
                target = self.memory[REGS["EBP"]] + op1 + 1
                if(target>=self.max_memory):
                    print("栈溢出！")
                    return 
                else:
                    if target > self.memory[REGS["ESP"]]:
                        self.memory[REGS["ESP"]] = target
            elif(keywords[0]=="MOV"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=self.memory[op2]
                else:
                    self.memory[op1]=op2
                # 如果目标是 EIP，跳过自动 +1（等价于绝对跳转）
                if op1 == REGS["EIP"]:
                    continue
            elif(keywords[0]=="TO"):
                assert(1==0)
                self.memory[REGS[keywords[1]]]=self.memory[REGS[keywords[2]]]
            elif(keywords[0]=="ADD"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]+=self.memory[op2]
                else:
                    self.memory[op1]+=op2
            
            elif(keywords[0]=="SUB"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]-=self.memory[op2]
                else:
                    self.memory[op1]-=op2
            elif(keywords[0]=="MUL"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]*=self.memory[op2]
                else:
                    self.memory[op1]*=op2
            elif(keywords[0]=="DIV"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=int(self.memory[op1])//int(self.memory[op2])
                else:
                    self.memory[op1]=int(self.memory[op1])//int(op2)
            elif(keywords[0]=="AND"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=int(self.memory[op1]) & int(self.memory[op2])
                else:
                    self.memory[op1]=int(self.memory[op1]) & int(op2)
            elif(keywords[0]=="OR"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=int(self.memory[op1]) | int(self.memory[op2])
                else:
                    self.memory[op1]=int(self.memory[op1]) | int(op2)
            elif(keywords[0]=="XOR"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=int(self.memory[op1]) ^ int(self.memory[op2])
                else:
                    self.memory[op1]=int(self.memory[op1]) ^ int(op2)
            elif(keywords[0]=="MOD"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=int(self.memory[op1]) % int(self.memory[op2])
                else:
                    self.memory[op1]=int(self.memory[op1]) % int(op2)
            elif(keywords[0]=="NOT"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]= ~ int(self.memory[op2])
                else:
                    self.memory[op1]= ~ int(op2)
            elif(keywords[0]=="LEA"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    # LEA dst src: 如果 dst 和 src 相同，解引用: dst = memory[memory[src]]
                    # 否则: dst = memory[src] 的位置值（即 src 作为位置赋给 dst）
                    if op1 == op2:
                        self.memory[op1] = self.memory[int(self.memory[op2])]
                    else:
                        self.memory[op1] = self.memory[int(self.memory[op2])]
                else:
                    # flag2 == "real": 直接将数值存入（取地址）
                    self.memory[op1] = op2
                
            elif(keywords[0]=="SEA"):#把M[M[op1]]放入op2
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[self.memory[op1]]= int(self.memory[op2])
                else:
                    self.memory[self.memory[op1]]= int(op2)
            elif(keywords[0]=="PUSH"):
                # 正确语义：把值写入 memory[ESP]，再 ESP+=1
                sp=self.memory[REGS["ESP"]]
                if(flag1=="pos"):
                    self.memory[sp]=int(self.memory[op1])
                else:
                    self.memory[sp]=int(op1)
                self.memory[REGS["ESP"]]=sp+1
            elif(keywords[0]=="POP"):
                # 正确语义：ESP-=1，目的地 = memory[ESP]
                assert(flag1=="pos")
                sp=self.memory[REGS["ESP"]]-1
                self.memory[REGS["ESP"]]=sp
                self.memory[op1]=self.memory[sp]
            elif(keywords[0]=="GREATER"):
                if(flag1=="pos"):
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= self.memory[op1]>self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= self.memory[op1]>op2
                else:
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= op1>self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= op1>op2
                self.memory[REGS["EFG"]]= not self.memory[REGS["EFG"]]
            elif(keywords[0]=="EQUAL"):
                if(flag1=="pos"):
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= self.memory[op1]==self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= self.memory[op1]==op2
                else:
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= op1==self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= op1==op2
                self.memory[REGS["EFG"]]= not self.memory[REGS["EFG"]]
            elif(keywords[0]=="LESS"):
                if(flag1=="pos"):
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= self.memory[op1]<self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= self.memory[op1]<op2
                else:
                    if(flag2=="pos"):
                        self.memory[REGS["EFG"]]= op1<self.memory[op2]
                    else:
                        self.memory[REGS["EFG"]]= op1<op2
                self.memory[REGS["EFG"]]= not self.memory[REGS["EFG"]]
            elif(keywords[0]=="LE"):
                if(flag1=="pos"):
                    a=self.memory[op1]
                else:
                    a=op1
                if(flag2=="pos"):
                    b=self.memory[op2]
                else:
                    b=op2
                self.memory[REGS["EFG"]]= not (a<=b)
            elif(keywords[0]=="GE"):
                if(flag1=="pos"):
                    a=self.memory[op1]
                else:
                    a=op1
                if(flag2=="pos"):
                    b=self.memory[op2]
                else:
                    b=op2
                self.memory[REGS["EFG"]]= not (a>=b)
            elif(keywords[0]=="RF"):
                self.memory[REGS["EFG"]]= not self.memory[REGS["EFG"]]
            elif(keywords[0]=="JPIF"):
                if(self.memory[REGS["EFG"]]==True):
                    if(flag1=="real"):
                        self.memory[REGS["EIP"]]+=op1
                    else:    
                        self.memory[REGS["EIP"]]+=self.memory[op1]
                    continue
            elif(keywords[0]=="JPNIF"):
                if(self.memory[REGS["EFG"]]==False):
                    if(flag1=="real"):
                        self.memory[REGS["EIP"]]+=op1
                    else:
                        self.memory[REGS["EIP"]]+=self.memory[op1]
                    continue    
            elif(keywords[0]=="JMP"):
                if(flag1=="real"):
                    self.memory[REGS["EIP"]]+=op1
                else:
                    self.memory[REGS["EIP"]]+=self.memory[op1]
                continue
            elif(keywords[0]=="OUT"):
                if(flag1=="pos"):
                    print(chr(int(self.memory[op1])),end="",flush=True)
                else:
                    print(chr(int(op1)),end="",flush=True)
            elif(keywords[0]=="OUTNUM"):
                if(flag1=="pos"):
                    print(int(self.memory[op1]),end="",flush=True)
                else:
                    print(int(op1),end="",flush=True)
            elif(keywords[0]=="IN"):
                char = _getch()
                assert(flag1=="pos")
                if(flag1=="pos"):
                    self.memory[op1]=ord(char)

            self.memory[REGS["EIP"]]+=1
        end_time = time.time()
        # 计算执行时间
        elapsed_time = end_time - start_time
        print(f"\n虚拟机执行时间: {elapsed_time} 秒")
    def Run_from_code(self,lines):
        print("********SYSTEM RUNNING********")
        self.RUN(lines)
    def Run_from_file(self,file_path):
        lines=[]
        with open(file_path, 'r') as file: #构造词类
            # 逐行读取文本内容 并执行
            for line in file:
                lines.append(line.strip())
        self.RUN(lines)
if __name__ == "__main__":
    a=Runner()
    a.Run_from_file("IR.txt")
