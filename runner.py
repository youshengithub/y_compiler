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
import time, msvcrt
import cProfile
# 记录开始时间

class Runner:
    def __init__(self) -> None:
        pass
    def calc_pos(self,text,REGS): #通过此来计算和数据
        if("$"  in text):
            ans=0
            texts=text.split(":")
            ans=int(texts[0][1:])
            if(len(texts)==2):
                if(texts[1].startswith("$")):
                    ans+=int(self.memory[int(texts[1][1:])])
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
        while(True):
            
            ip=self.memory[REGS["EIP"]]
            if(ip>=len(lines)):
                break
            keywords=keywordss[ip]
            # for i in keywords:
            #     print(i,end="")
            #     print(" ",end="")
            # print("")
            #print(ip)
            #print("正在执行:",keywords)
            if(len(keywords)>=2):flag1,op1=self.calc_pos(keywords[1],REGS)
            if(len(keywords)>=3):flag2,op2=self.calc_pos(keywords[2],REGS)
            if(keywords[0]=="ALLOC"):
                if(op1>=self.max_memory):
                    print("栈溢出！")
                    return 
                else:
                    self.memory[REGS["ESP"]]=op1+1
            elif(keywords[0]=="MOV"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=self.memory[op2]
                else:
                    self.memory[op1]=op2
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
                    self.memory[op1]/=self.memory[op2]
                else:
                    self.memory[op1]/=op2
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
                assert(flag2=="pos")
                self.memory[op1]=op2
                
            elif(keywords[0]=="SEA"):#把M[M[op1]]放入op2
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[self.memory[op1]]= int(self.memory[op2])
                else:
                    self.memory[self.memory[op1]]= int(op2)
            elif(keywords[0]=="PUSH"):
                if(flag1=="pos"):
                    self.memory[REGS["ESP"]]= int(self.memory[op1])
                else:
                    self.memory[REGS["ESP"]]= int(op1)
                self.memory[REGS["ESP"]]+=1
            elif(keywords[0]=="POP"):
                assert(flag1=="pos")
                self.memory[REGS["ESP"]]-=1
                if(flag1=="pos"):
                    self.memory[op1]=self.memory[REGS["ESP"]]
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
                    pass
                    print(chr(int(self.memory[op1])),end="",flush=True)
                else:
                    pass
                    print(chr(int(op1)),end="",flush=True)
            elif(keywords[0]=="IN"):
                char = msvcrt.getch()
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
