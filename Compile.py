import re,itertools
from runner import Runner
# 打开文本文件


class token:#token类
    pass

class Compoment:
    Cs={}   #语句类型
    unmatch={}
    def __init__(self, name_,config_,repeat_,no_start):
        self.configs=config_
        self.name=name_
        self.repeat=repeat_
        self.no_start=no_start
    def Complie(self,rule,oplist,codelist,VarPos):
        code=""
        if(self.name=="VAR"): #如果是VARS需要对其做出修正！例如是a 100那就要翻译成a-100直接 #注意到！这里面可能有坑！需要real time计算位置
            #可能会涉及到修改oplist a+i这边是静态 所以计算不出位置 需要写到代码里面去 所以必须设计新的指令系统
            #MOV ECX $1
            #ADD ECX i
            #MOV $(11+$12)携程这种形式吧！
            #其实应该在这里进行修正
            pass
        elif(self.name=="CONST"):
            pass
        elif(self.name=="DIM"):
            code="ALLOC "+str(oplist[0])+"\n"
            pass
        elif(self.name=="OP"):
            for i in codelist: code+=i 
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
                code=codelist[1]
                code+="MOV EBX EAX\n"
                code+=codelist[0]
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
                code=codelist[1]
                code+="MOV EBX EAX\n"
                code+=codelist[0]
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
        elif(self.name=="AND" or self.name=="XOR" or self.name=="OR" or self.name=="MOD"):
            if(bool(re.match("\\$OPN\\$.+\\$OPN\\$", rule))):
                code="MOV EAX "+str(oplist[0])+"\n"
                code+=self.name+" EAX "+str(oplist[1])+"\n"
            elif(bool(re.match("\\$OPN\\$.+\\$OP\\$", rule))):
                code=codelist[0]
                code+=self.name+" EAX "+str(oplist[0])+"\n"
            elif(bool(re.match("\\$OP\\$.+\\$OPN\\$", rule))):
                code=codelist[0]
                code+=self.name+" EAX "+str(oplist[-1])+"\n"
            elif(bool(re.match("\\$OP\\$.+\\$OP\\$", rule))):
                code=codelist[0]
                code+="MOV EBX EAX\n"
                code+=codelist[1]
                code+=self.name+" EAX EBX\n"
            else:
                assert(1==0)

        elif(self.name=="NOT"): #处理单目运算符
            if(rule=="!$OPN$"):
                code="NOT EAX "+str(oplist[0])+"\n"
            elif(rule=="!$OP$"):
                code=codelist[0]
                code+="MOV EBX EAX\n"
                code+="NOT EAX EBX\n"
            else:
                pass
            pass
        elif(self.name=="GETP"):
            pass
        elif(self.name=="SETP"):
            pass
        elif(self.name=="EQUAL"):
            if(rule=="$VAR$=$OPN$;"):
                code="MOV "+str(oplist[0]) +" "+str(oplist[1])+"\n"
            elif(rule=="$VAR$=$OP$;"):   
                code=codelist[0]
                code+= "MOV "+str(oplist[0])  + " EAX\n"
                pass
            pass
        elif(self.name=="SENTENCE"):
            for i in codelist: code+=i 
            pass
        elif(self.name=="JUDGE"):
            if(rule.find("<=")!=-1):
                pass
            elif(rule.find(">=")!=-1):
                pass
            if(rule.find("<")!=-1):
                code="LESS "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find(">")!=-1):
                code="GREATER "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find("==")!=-1):
                code="EQUAL "+oplist[0]+" "+oplist[1]+"\n"
            elif(rule.find("!=")!=-1):
                code="EQUAL "+oplist[0]+" "+oplist[1]+"\n"
                code+="RF\n"
            elif(rule.find("&&")!=-1):
                code=codelist[0]
                code+="JPIF "+str((codelist[1]).count("\n")+1)+"\n"
                code+=codelist[1]
            elif(rule.find("||")!=-1):
                code=codelist[0] #如果不是这样的就跳转到末尾
                code+="JPNIF "+str((codelist[1]).count("\n")+1)+"\n"
                code+=codelist[1]
            else:
                for i in codelist: code+=i 
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
            for i in codelist: code+=i #注意到这里已经完成了赋值 这里面分了三段
            code+="MOV ESP $0:-6\n"
            #code+="MOV $EBP:-3 $EAX\n" EAX不恢复！
            code+="MOV EBX $0:-3\n"
            code+="MOV EFG $0:-2\n"
            code+="MOV ETP $0:-1\n" #不用再跳转了！这里已经写好了参数了！ 注意到这里有一个坑按道理来说必须同时还原,
            code+="MOV EBP $0:-5\n" #使用临时寄存器ETP暂时保存该跳转的结果。
            code+="MOV EIP ETP\n"
            code="JMP "+str(code.count("\n")+1)+"\n"+code
            code="ALLOC @"+oplist[0]+"\n"+code
            VarPos.clear()
            VarPos["SUM"]=0
            #code=codelist[0] #还没处理return问题嘞
            pass
        elif(self.name=="CALL"):#call 然后eax传入参数！
            #oplist[1] 就是标签名 base+最高， 然后把参数都move过去 然后base-最高，就ok了！
            #保存ESP和EBP
            #这里不能这样计算 EAX无用了 因为不会被恢复
            code="MOV EAX ESP\n"
            code+="SUB EAX EBP\n"
            code+="MOV $0:EAX ESP\n"
            code+="MOV $1:EAX EBP\n"
            code+="MOV $2:EAX EAX\n"
            code+="MOV $3:EAX EBX\n"
            code+="MOV $4:EAX EFG\n"
            code+="MOV ETA EAX\n" #保存一下我要压ip的时候用
            
            code+="ADD ESP 6\n"
            code+="MOV ETP ESP\n"
            code+=codelist[0] #压入参数 EAX EBX 可用 EBP ETP 可用否？
            
            code+="MOV EAX EIP\n"
            code+="ADD EAX 4\n"
            code+="MOV $5:ETA EAX\n"#最后才来压入eip! 不行 这里的EAX的值g了
            
            code+="MOV EBP ETP\n" #压完了参数再给ebp复制
            code+="JMP @"+oplist[0]+"\n" #这里需要绝对地址！
            #然后需要执行跳转！
            pass
        elif(self.name=="FUNCNAME"):
            #if(self.name=="FUNC"):
            #这里可以分配标记！ 可以直接进行跳转标记
            #ALLOC world
            pass
        elif(self.name=="PAR"):#这里是形参
            #code="SUB EBP 1\n" #不太需要动EBP
            pass
        elif(self.name=="ARG"): #这里是call的实参  只能使用EAX了 但是我又需要计算op op的值必须要存在eax里面
            #可以使用EAX 但是在算数的时候可能会使用任意参数啊！ 不要把EBX算数寄存器拿来用作控制！
            code="MOV EAX ESP\n"
            code+="SUB EAX EBP\n"
            if(rule=="$OPN$"):
                code+="MOV $0:EAX "+oplist[0]+"\n"
                
            elif(rule=="$OP$"):
                print("NOT_SUPPORT")
                assert(1==0)
                code+="MOV $0:EAX "+oplist[0]+"\n"
            else:
                pass
            code+="ADD ESP 1\n"   
            pass
        elif(self.name=="RETURN"):
            if("$OP$" in rule):
                for i in codelist: code+=i #JMP到最后才行！ 这里怎么写最后啊！
            elif("$OPN$" in rule):
                code="MOV EAX "+oplist[0]+"\n"
            else:
                pass #啥也不返回
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
                    #print(prefix+"(","解析规则 中，规则名称:",rule," 代码:",textc)
                    succ,text,VarPos,oplist,code_list,logs1=self.HandleR(rule,textc,VarPos,prefix+"   ") #这里面没有传入代码 
                    Compoment.unmatch[(textc,self.name,rule)]=(succ,text,VarPos,oplist,code_list,logs1)
                    #所以就算是解析成功也无法返回
                    #print(prefix,"解析规则 状态:",succ,"规则名称:",rule,")")
                if(succ):
                    flag=True
                    repeat=self.repeat
                    r_oplist=oplist
                    #在这里构建code!
                    #print(self.name,rule,oplist,code_list,VarPos)
                    compiled_code=self.Complie(rule,oplist,code_list,VarPos) 
                    r_code+=compiled_code #+" Rule: "+rule
                    this_log="***************Text*************** \n"+textc[:len(textc)-len(text)]+"\n***************Code***************\n"+compiled_code
                    logs=logs1+this_log
                    #print(this_log)
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
                        print("编译错误！,当前编译位置:",textc,"\nlog\n",logs2)
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
                line=line.replace(' ', '')
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


