import re,itertools
from runner import Runner
# 打开文本文件




class Compoment:
    Cs={}   #语句类型
    unmatch={}
    def __init__(self, name_,config_,repeat_,no_start):
        self.configs=config_
        self.name=name_
        self.repeat=repeat_
        self.no_start=no_start
    def Complie(self,rule,oplist,codelist,VarPos):
        #print(codelist,oplist)
        code=""
        if(self.name=="VAR"): #如果是VARS需要对其做出修正！例如是a 100那就要翻译成a-100直接 #注意到！这里面可能有坑！需要real time计算位置
            #可能会涉及到修改oplist a+i这边是静态 所以计算不出位置 需要写到代码里面去 所以必须设计新的指令系统
            #MOV ECX $1
            #ADD ECX i
            #MOV $(11+$12)携程这种形式吧！
            pass
        elif(self.name=="CONST"):
            pass
        elif(self.name=="DIM"):
            code="ALLOC "+str(oplist[0])+"\n"
            pass
        elif(self.name=="OP"):
            code=codelist[0]
            pass
        elif(self.name=="ADD"):
            if(rule=="$OPN$+$OPN$"):
                code="MOV EAX "+str(oplist[0])+"\n"
                code+="ADD EAX "+str(oplist[1])+"\n"
            elif(rule=="$OPN$+$OP$"):
                code=codelist[0]
                code+="ADD EAX "+str(oplist[0])+"\n"
            elif(rule=="$OP$+$OPN$"):
                code=codelist[0]
                code+="ADD EAX "+str(oplist[-1])+"\n"
            elif(rule=="$OP$+$OP$"):
                code=codelist[0]
                code+="MOV EBX EAX\n"
                code+=codelist[1]
                code+="ADD EAX EBX\n"
            else:
                assert(1==0)
        elif(self.name=="SUB"):
            if(rule=="$OPN$-$OPN$"):
                code="MOV EAX "+str(oplist[0])+"\n"
                code+="SUB EAX "+str(oplist[1])+"\n"
            elif(rule=="$OPN$-$OP$"):
                code=codelist[0]
                code+="MOV EBX "+str(oplist[0])+"\n"
                code+="SUB EBX EAX\n"
                code+="MOV EAX EBX\n"
            elif(rule=="$OP$-$OPN$"):
                code=codelist[0]
                code+="SUB EAX "+str(oplist[-1])+"\n"
            elif(rule=="$OP$-$OP$"):
                code=codelist[1]
                code+="MOV EBX EAX\n"
                code+=codelist[0]
                code+="SUB EAX EBX\n"
            else:
                assert(1==0)
        elif(self.name=="MUL"): #注意到可能会被修正成代码！ op可能会被修正成位置
            if(rule=="$OPN$*$OPN$"):
                code="MOV EAX "+str(oplist[0])+"\n"
                code+="MUL EAX "+str(oplist[1])+"\n"
            elif(rule=="$OPN$*$OP$"):
                code=codelist[0]
                code+="MUL EAX "+str(oplist[0])+"\n"
            elif(rule=="$OP$*$OPN$"):
                code=codelist[0]
                code+="MUL EAX "+str(oplist[-1])+"\n"
            elif(rule=="$OP$*$OP$"):
                code=codelist[0]
                code+="MOV EBX EAX\n"
                code+=codelist[1]
                code+="MUL EAX EBX\n"
            else:
                assert(1==0)
        elif(self.name=="DIV"):
            if(rule=="$OPN$/$OPN$"):
                code="MOV EAX "+str(oplist[0])+"\n"
                code+="DIV EAX "+str(oplist[1])+"\n"
            elif(rule=="$OPN$/$OP$"):
                code=codelist[0]
                code+="MOV EBX "+str(oplist[0])+"\n"
                code+="DIV EBX EAX\n"
                code+="MOV EAX EBX\n"
            elif(rule=="$OP$/$OPN$"):
                code=codelist[0]
                code+="DIV EAX "+str(oplist[-1])+"\n"
            elif(rule=="$OP$/$OP$"):
                code=codelist[1]
                code+="MOV EBX EAX\n"
                code+=codelist[0]
                code+="DIV EAX EBX\n"
            else:
                assert(1==0)
        elif(self.name=="EQUAL"):
            if(rule=="$VAR$=$OPN$;"):
                code="MOV "+str(oplist[0]) +" "+str(oplist[1])+"\n"
            elif(rule=="$VAR$=$OP$;"):   
                code=codelist[0]
                code+= "MOV "+str(oplist[0])  + " EAX\n"
                pass
            pass
        elif(self.name=="SENTENCE"):
            if(len(codelist)!=0):code=codelist[0]
            pass
        elif(self.name=="JUDGE"):
            if(rule.find("<")!=-1):
                code="LESS "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find(">")!=-1):
                code="GREATER "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find("==")!=-1):
                code="EQUAL "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find("!=")!=-1):
                code="EQUAL "+oplist[0]+" "+oplist[1]+"\n"
                code+="RF\n"
            pass
        elif(self.name=="LOGIC"):
            if(rule.find("&&")!=-1):
                code=codelist[0]
                code+="JPIF "+str((codelist[1]).count("\n")+1)+"\n"
                code+=codelist[1]
            elif(rule.find("||")!=-1):

                code=codelist[0] #如果不是这样的就跳转到末尾
                code+="JPNIF "+str((codelist[1]).count("\n")+1)+"\n"
                code+=codelist[1]
                pass
            else:
                if(len(codelist)!=0):code=codelist[0]
        elif(self.name=="IF"):
            code=codelist[0]
            code+="JPIF "+str((codelist[1]).count("\n")+2)+"\n"
            code+=codelist[1]
            code+="JMP "+str((codelist[2]).count("\n")+1)+"\n"
            code+=codelist[2]
            pass
        elif(self.name=="DO"):
            code=codelist[0]+codelist[1]
            code+="RF\n"
            code+="JPIF -"+str((codelist[0]+codelist[1]).count("\n")+1)+"\n"
            
            pass
        elif(self.name=="WHILE"):
            code=codelist[0]
            code+="JPIF "+str(codelist[1].count("\n")+2)+"\n"
            code+=codelist[1]
            code+="JMP -"+str((codelist[0]+codelist[1]).count("\n")+1)+"\n"
            pass
        elif(self.name=="FOR"):
            code=codelist[0]+codelist[1]
            code+="JPIF "+str((codelist[3]+codelist[2]).count("\n")+2)+"\n"
            code+=codelist[3]+codelist[2]
            code+="JMP -"+str((codelist[1]+codelist[3]+codelist[2]).count("\n")+1)+"\n"
            
            pass
        elif(self.name=="PRINT"):
            code="OUT "+str(oplist[0])+"\n"
            pass
        elif(self.name=="FUNC"):#在定义的时候，不要执行语句
            for i in codelist: code+=i
            code+="JMP EBP\n"
            code="JMP "+str(code.count("\n")+1)+"\n"+code
            #code=codelist[0] #还没处理return问题嘞
            pass
        elif(self.name=="CALL"):#call 然后eax传入参数！
            #oplist[1] 就是标签名 base+最高， 然后把参数都move过去 然后base-最高，就ok了！
            code="NOP\n"
            pass
        elif(self.name=="FUNCNAME"):
            pass
        elif(self.name=="PAR"):
            
            pass
        elif(self.name=="RETURN"):
            code=codelist[0] 
            pass
        return code
    def handelP(self,rule,text,VarPos,prefix): #按道理这个也应该返回一个oplist
        #print("HandleP: Rule:",rule," Text: ",text)
        next_index = rule[1:].find('$')
        if(next_index==-1): return False
        name=rule[1:next_index+1]
        return Compoment.Cs[name].Rrcognize(text,VarPos,rule,prefix)
    def HandleR(self,rule,text,VarPos,prefix): #匹配失败返回原样
        text_c=text
        oplist=[]#这里返回解析的每一个op!
        codelist=[]
        #print("HandleR: Rule:",rule," Text: ",text)
        r_logs=""
        while(rule!=""):
            # if(rule==";" ): #注意到这是特殊规则
            #     rule=rule[1:]
            #     if(text.startswith(";")):
            #         text=text[1:]
            #     continue
            if(text.startswith("1") and rule=="$OPN$"):
                    debug=1
            if(rule[0]=="@"):
                next_index = rule[1:].find('@')
                if(next_index==-1): 
                    return False,text_c,VarPos,oplist,codelist,r_logs
                pattern=rule[1:next_index+1] 
                match = re.search(pattern, text)
                if match!=None :
                    #print("变量解析成功:",text,pattern)
                    text=text[match.regs[0][1]:]  
                    rule=rule[2+len(pattern):]  
                    
                    if(self.name=="VAR"): #需要进行判断是什么词性
                        num_groups = len(match.groups())
                        var_length="1"
                        var_name=match.group(1)
                        if(match.group(2)!=None):
                            var_length=match.group(2)[1:-1] #这里是字符串
                        if(var_name not in VarPos): 
                            VarPos[var_name]=VarPos["SUM"]
                            VarPos["SUM"]+=int(var_length)#这里必须成果！
                        first="$"+str(VarPos[var_name])+":"
                        
                        if(var_length.isdigit()==True):
                            if(match.group(2)==None):
                                second="0" #a=1 就是a[0]=1
                            else:
                                second=var_length
                        else:
                            second="$"+str(VarPos[var_length])
                        oplist.append(first+second) # #MOV $1:$2 or $1:2实际位置就是 携程这种形式吧！
                    elif(self.name=="CONST"):
                        oplist.append(match.group(0))
                    elif(self.name=="FUNCNAME"): #需要有一个table 
                        oplist.append(match.group(0))
                else:
                    
                    return False,text_c,VarPos,oplist,codelist,r_logs
                
            elif(rule.startswith("$")):

                succ,text,code,VarPos,r_oplist,logs=self.handelP(rule,text,VarPos,prefix+"  ") #消除掉rule部分 并且这里的code 没有用上！
                if(succ==True):
                    r_logs+=logs
                    dollar_index = rule[1:].find('$')
                    rule=rule[2+dollar_index:] 
                    oplist+=r_oplist
                    if(code!=""):
                        codelist+=[code]
                    continue
                else:
                    return False,text_c,VarPos,oplist,codelist,r_logs
            else:
                    dollar_index = rule.find('$')
                    keyword=rule[:dollar_index] if dollar_index != -1 else rule
                    if(text.startswith(keyword)):
                        text=text[len(keyword):]  
                        rule=rule[len(keyword):]  
                    else:
                        return False,text_c,VarPos,oplist,codelist,r_logs
        return True,text,VarPos,oplist,codelist,r_logs
            #匹配到Rule结束位置
    
    def Rrcognize(self,text,VarPos,toprule="",prefix=""):
        #如果是repeat的话 还需要重复！
        #print("Rrcognize: name: ",self.name, "Text: ",text)
        if(self.name=="EQUAL"):
            debug=1
        flag=False
        code=""
        repeat=True
        r_oplist=[]
        r_code=""
        logs=""
        if(text.startswith("a=1+(23)") and self.name=="VAR"):
            debug=1
        while(repeat): #规则必须也是寻找最有可能的匹配
            repeat=False
            for rule in self.configs:#通过语句构建,这个选择一种规则！
                textc=text
                if((text,self.name,rule) in Compoment.unmatch ): #使用缓存，避免重复解析
                    if(Compoment.unmatch[(text,self.name,rule)]=="PROCESSING"):
                        #陷入重入
                        succ=False
                    else:
                        succ,text,VarPos,oplist,code_list,logs1=Compoment.unmatch[(text,self.name,rule)]
                else:
                    Compoment.unmatch[(textc,self.name,rule)]="PROCESSING"
                    print(prefix+"(","解析规则 中，规则名称:",rule," 代码:",textc)
                    succ,text,VarPos,oplist,code_list,logs1=self.HandleR(rule,textc,VarPos,prefix+"   ") #这里面没有传入代码 
                    Compoment.unmatch[(textc,self.name,rule)]=(succ,text,VarPos,oplist,code_list,logs1)
                    #所以就算是解析成功也无法返回
                    print(prefix,"解析规则 状态:",succ,"规则名称:",rule,")")
                if(succ):
                    flag=True
                    repeat=self.repeat
                    r_oplist=oplist
                    #在这里构建code!
                    #print(self.name,rule,oplist,code_list,VarPos)
                    compiled_code=self.Complie(rule,oplist,code_list,VarPos) 
                    r_code+=compiled_code
                    logs=logs1+"\n"+" Grammer: "+self.name+" Rule: "+rule+ " Text: "+textc[:len(textc)-len(text)]+" codes:"+compiled_code
                    break   #这里仿佛也不应该call;最好是用 

        return flag,text,r_code,VarPos,r_oplist,logs
    

class Compiler:
    #VARPos=环境
    def __init__(self) -> None:
        self.error=False
    def ana(self,text,codes,VarPos={},prefix=""): #这里必须有个递归,可能符合多种情况
        r_logs=""
        if(text==""):
            print("**********IR**********")
            print(codes)
            return True,codes,VarPos,r_logs
        flag=False
        for name,sentence in Compoment.Cs.items():
            if(sentence.no_start==True): continue
            if(text.startswith("c>0;)") and name=="$JUDGE$"):
                 debug=1
            #print(prefix+"[ ","解析语法中 规则名称: ",name," 代码:",text)
            succ,textc,code,VarPos,r_oplist,logs1=sentence.Rrcognize(text,VarPos,"",prefix+"   ")
            #print(prefix,"解析语法结果 状态:",succ,"规则名称: ",name, " Text: ",text[:len(text)-len(textc)],"codes:",code+" ]")
            if(succ==True):
                succ,true_code,VarPos,logs2=self.ana(textc,codes+code,VarPos,"   "+prefix) #代码都是至上往下的
                r_logs=logs2+"\n"+logs1
                if(succ==True):    
                    codes=true_code
                    flag=True
                    break #只能有一种 不能再加了！
                else:
                    if(self.error==False):
                        self.error=True
                        print("编译错误！,当前编译位置:",textc)
                    #return False,codes,VarPos,r_logs #这句话不知道该不该加上去！！！！
        return flag,codes,VarPos,r_logs
    def revise_config(self,original_str):
        pattern = r"<(.*?)>"
        matches = re.findall(pattern, original_str)
        split_parts = [match.split('|') for match in matches]
        combinations = list(itertools.product(*split_parts))
        ans=[]
        for replace_tuple in combinations:
            replaced_str = original_str
            for item in replace_tuple:
                replaced_str = re.sub(r"<.*?>", item, replaced_str, 1)  # 只替换第一个匹配的项
            ans.append(replaced_str)
        return ans
    def construct_componets(self,file_path): #仿佛可以对规则进行修改<$$|;>将进行排列组合
        with open(file_path, 'r') as file: #构造词类
            for line in file:
                temp=line.split(":")
                name=temp[0]
                configs=temp[1].split("#")
                if(configs[-1]==""):
                    configs=configs[0:-1]
                attribute=temp[2]
                revised_configs=[]
                for config in configs:
                    revised_configs+=self.revise_config(config)
                print(name,revised_configs)
                Compoment.Cs[name]=Compoment (name,revised_configs,"REPEAT" in attribute, "NO_START" in attribute)  
    def Complie_file(self,file_path):
        content=""
        with open(file_path, 'r') as file:
            for line in file:
                pos=line.find("//")
                if pos!=-1:
                    content+=line[0:pos]
                else:
                    content+=line
                    
        print("**********CODE**********")

        content_without_newlines = content.replace('\n', '').replace(' ', '').replace('\t', '')
        print(content,content_without_newlines)
        self.error=False
        #做好预处理，先把函数的编译出来，然后在这里进行组装,
        return self.ana(content_without_newlines,"",{"SUM":0})
a=Compiler()
b=Runner()
a.construct_componets("Config.txt")
succ,code,varpos,logs=a.Complie_file("code.txt")
b.Run_from_code(code.split("\n"))


#IR支持16种指令
#ALLOC
#MOV
#ADD
#SUB
#MUL
#DIV
#GREATER
#EQUAL
#LESS
#JPIF
#JPNIF
#JMP
#OUT
#RF
#TO
#NOP
