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
    def calc_pos(self,text): #通过此来计算和数据
        if("$" not in text):
            return "real",int(text)
        else:
            ans=0
            texts=text.split(":")
            assert(len(texts)==2)
            ans=int(texts[0][1:])
            if(texts[1].startswith("$")):
                ans+=int(self.memory[int(texts[1][1:])])
            else:
                ans+=int(texts[1])
            return "pos",ans+self.base
    def RUN(self,lines): #注意到操作数可以是real $1 var
        max_memory=100000
        self.jump=0
        self.base=0
        self.memory=[0 for i in range(max_memory)]
        start_time = time.time()
        ip=1
        VARS={"EAX":100, "EBX":101}
        keywordss=[]
        for line in lines:
            for k,v in VARS.items():
                if(k in line):
                    line=line.replace(k,"$"+str(v)+":0")
            keywordss.append(line.split(" "))

        while(ip<=len(lines)):
            
            keywords=keywordss[ip-1]
            #print("正在执行:",keywords)
            if(len(keywords)>=2):flag1,op1=self.calc_pos(keywords[1])
            if(len(keywords)>=3):flag2,op2=self.calc_pos(keywords[2])
            if(keywords[0]=="ALLOC"):
               if(op1+len(VARS)>=max_memory):
                   print("栈溢出！")
                   return 
            elif(keywords[0]=="MOV"):
                assert(flag1=="pos")
                if(flag2=="pos"):
                    self.memory[op1]=self.memory[op2]
                else:
                    self.memory[op1]=op2
            elif(keywords[0]=="TO"):
                assert(1==0)
                self.memory[VARS[keywords[1]]]=self.memory[VARS[keywords[2]]]
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
                        self.jump= self.memory[op1]>self.memory[op2]
                    else:
                        self.jump= self.memory[op1]>op2
                else:
                    if(flag2=="pos"):
                        self.jump= op1>self.memory[op2]
                    else:
                        self.jump= op1>op2
                self.jump= not self.jump
            elif(keywords[0]=="EQUAL"):
                if(flag1=="pos"):
                    if(flag2=="pos"):
                        self.jump= self.memory[op1]==self.memory[op2]
                    else:
                        self.jump= self.memory[op1]==op2
                else:
                    if(flag2=="pos"):
                        self.jump= op1==self.memory[op2]
                    else:
                        self.jump= op1==op2
                self.jump= not self.jump
            elif(keywords[0]=="LESS"):
                if(flag1=="pos"):
                    if(flag2=="pos"):
                        self.jump= self.memory[op1]<self.memory[op2]
                    else:
                        self.jump= self.memory[op1]<op2
                else:
                    if(flag2=="pos"):
                        self.jump= op1<self.memory[op2]
                    else:
                        self.jump= op1<op2
                self.jump= not self.jump
            elif(keywords[0]=="RF"):
                self.jump= not self.jump
            elif(keywords[0]=="JPIF"):
                if(self.jump==True):
                    assert(flag1=="real")
                    ip+=op1
                    continue
            elif(keywords[0]=="JPNIF"):
                if(self.jump==False):
                    assert(flag1=="real")
                    ip+=op1
                    continue    
            elif(keywords[0]=="JMP"):
                assert(flag1=="real")
                ip+=op1
                continue
            elif(keywords[0]=="OUT"):
                if(flag1=="pos"):
                    print("OUT: ",self.memory[op1])
                else:
                    print("OUT: ",op1)
                
            ip+=1
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
