#IR支持13种命令
#ALLOC
#MOV
#TO
#ADD
#SUB
#MUL
#DIV
#GREATER
#EQUAL
#LESS
#JPIF
#JMP
#OUT
import time,re

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
                if(ans+self.memory[REGS["EBP"]]>=self.max_memory): #寄存器的地址不能加EBP
                    return "pos",ans
                
                #如果地址里面带有EBP ESP等等 那就不再需要去加基地址EBP
            return "pos",ans+self.memory[REGS["EBP"]]
        elif ("@"  in text):
            return "tag",text[1:]
        else:
            return "real",int(text)
            
    def RUN(self,lines): #注意到操作数可以是real $1 var
        self.max_memory=100000
        self.memory=[0 for i in range(self.max_memory)]
        self.tags={} #这里用来记录程序中分配的tag tag 和jmp tag tag用@来表示 TAG @a JMP @a
        start_time = time.time()
        REGS={"EAX":self.max_memory-1, "EBX":self.max_memory-2,"EBP":self.max_memory-3,"ESP":self.max_memory-4,"EIP":self.max_memory-5,"EFG":self.max_memory-6,"ETP":self.max_memory-7}
        keywordss=[]
        for line in lines:
            for k,v in REGS.items():
                if(k in line):
                    line=line.replace(k,"$"+str(v))
            keywordss.append(line.split(" "))
        while(True):
            
            ip=self.memory[REGS["EIP"]]
            if(ip>=len(lines)):
                break
            keywords=keywordss[ip]
            
            #print("正在执行:",keywords)
            if(len(keywords)>=2):flag1,op1=self.calc_pos(keywords[1],REGS)
            if(len(keywords)>=3):flag2,op2=self.calc_pos(keywords[2],REGS)
            if(keywords[0]=="ALLOC"):
                if(flag1=="tag"):
                    if(op1 in self.tags):
                        print("重定义符号") #接下来的即使jmp
                    else:
                        self.tags[op1]=ip+2
                else:
                    if(op1+len(REGS)>=self.max_memory):
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
                    elif(flag1=="tag"):
                        self.memory[REGS["EIP"]]=self.tags[op1] #这里必须得是绝对地址哦！ 
                    else:    
                        self.memory[REGS["EIP"]]+=self.memory[op1]
                    continue
            elif(keywords[0]=="JPNIF"):
                if(self.memory[REGS["EFG"]]==False):
                    if(flag1=="real"):
                        self.memory[REGS["EIP"]]+=op1
                    elif(flag1=="tag"):
                        self.memory[REGS["EIP"]]=self.tags[op1] #这里必须得是绝对地址哦！ 
                    else:
                        self.memory[REGS["EIP"]]+=self.memory[op1]
                    continue    
            elif(keywords[0]=="JMP"):
                if(flag1=="real"):
                    self.memory[REGS["EIP"]]+=op1
                elif(flag1=="tag"):
                        self.memory[REGS["EIP"]]=self.tags[op1] #这里必须得是绝对地址哦！ 
                else:
                    self.memory[REGS["EIP"]]+=self.memory[op1]
                continue
            elif(keywords[0]=="OUT"):
                if(flag1=="pos"):
                    print("OUT: ",self.memory[op1])
                else:
                    print("OUT: ",op1)
            self.memory[REGS["EIP"]]+=1
        end_time = time.time()
        # 计算执行时间
        elapsed_time = end_time - start_time
        print(f"虚拟机执行时间: {elapsed_time} 秒")
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
