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
import time

# 记录开始时间

class Runner:
    def __init__(self) -> None:
        pass
    def RUN(self,lines): #注意到操作数可以是real $1 var
        start_time = time.time()
        current_alloc=0
        ip=1
        VARS={"EAX":100, "EBX":101}
        keywordss=[]
        for line in lines:
            keywordss.append(line.split(" "))
            #在这里可以对其进行预处理 使其都转换成位置 $1的形式
        while(ip<=len(lines)):
            keywords=keywordss[ip-1]
            if(keywords[0]=="ALLOC"):
                if(keywords[1] not in VARS):
                    VARS[keywords[1]]=current_alloc
                    current_alloc+=int(keywords[2]) 
            elif(keywords[0]=="MOV"):
                if(keywords[2] in VARS):
                    self.memory[VARS[keywords[1]]]=self.memory[VARS[keywords[2]]]
                else:
                    self.memory[VARS[keywords[1]]]=int(keywords[2])

            elif(keywords[0]=="TO"):
                self.memory[VARS[keywords[1]]]=self.memory[VARS[keywords[2]]]
            elif(keywords[0]=="ADD"):
                if(keywords[2] not in VARS):
                    self.memory[VARS[keywords[1]]]+=int(keywords[2])
                else:
                    self.memory[VARS[keywords[1]]]+=self.memory[VARS[keywords[2]]]
            elif(keywords[0]=="SUB"):
                if(keywords[2] not in VARS):
                    self.memory[VARS[keywords[1]]]-=int(keywords[2])
                else:
                    self.memory[VARS[keywords[1]]]-=self.memory[VARS[keywords[2]]]
            elif(keywords[0]=="MUL"):
                if(keywords[2] not in VARS):
                    self.memory[VARS[keywords[1]]]*=int(keywords[2])
                else:
                    self.memory[VARS[keywords[1]]]*=self.memory[VARS[keywords[2]]]
            elif(keywords[0]=="DIV"):
                if(keywords[2] not in VARS):
                    self.memory[VARS[keywords[1]]]/=int(keywords[2])
                else:
                    self.memory[VARS[keywords[1]]]/=self.memory[VARS[keywords[2]]]
            elif(keywords[0]=="GREATER"):
                if(self.memory[VARS[keywords[1]]]>int(keywords[2])):
                    self.jump=False
                else:
                    self.jump=True
            elif(keywords[0]=="EQUAL"):
                if(self.memory[VARS[keywords[1]]]==int(keywords[2])):
                    self.jump=False
                else:
                    self.jump=True
            elif(keywords[0]=="LESS"):
                if(self.memory[VARS[keywords[1]]]<int(keywords[2])):
                    self.jump=False
                else:
                    self.jump=True
            elif(keywords[0]=="RF"):
                self.jump= not self.jump
            elif(keywords[0]=="JPIF"):
                if(self.jump==True):
                    ip+=int(keywords[1])
                    continue
            elif(keywords[0]=="JPNIF"):
                if(self.jump==False):
                    ip+=int(keywords[1])
                    continue    
            elif(keywords[0]=="JMP"):
                ip+=int(keywords[1])
                continue
            elif(keywords[0]=="OUT"):
                print("OUT: ",self.memory[VARS[keywords[1]]])
            ip+=1
        end_time = time.time()
        # 计算执行时间
        elapsed_time = end_time - start_time
        print(f"虚拟机执行时间: {elapsed_time} 秒")
    def Run_from_code(self,lines):
        print("********SYSTEM RUNNING********")
        self.jump=0
        self.memory=[0 for i in range(1000)]
        self.RUN(lines)
    def Run_from_file(self,file_path):
        self.jump=0
        self.memory=[0 for i in range(1000)]
        lines=[]
        with open(file_path, 'r') as file: #构造词类
            # 逐行读取文本内容 并执行
            for line in file:
                lines.append(line.strip())
        self.RUN(lines)
if __name__ == "__main__":
    a=Runner()
    a.Run_from_file("IR.txt")
