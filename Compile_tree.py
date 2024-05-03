import re
from token_ana import *
def Complie(name,rule,oplist,codelist,area_tree):
    code=""
    if(name=="VAR"): 
        if not oplist[0] in ["EAX","EBX","ESP","EBP","EIP","EFG","ETP"]:
            var=y_token.trans_var(oplist[0])
            base=0
            #ESP的位置用于存储temp变量 #找到变量所在的域 查看起始位置
            code+="MOV EBX 0\n"
            for id,i in enumerate(var):
                if(id==0):
                    find_var=area_tree.find_token(i[0]) #看一看是啥子类型
                else:#好像就是find_var不一样
                    find_flag=False
                    for var in find_type.vars:
                        if(var.name==i[0]):
                            find_var=var
                            find_flag=True
                            break
                    if not find_flag:
                        print(f"类型{find_type.name}不包含{i[0]}变量")
                        assert(1==0)
                
                if(find_var==None):
                    print("变量未定义",oplist[0],"--->",i[0])
                    assert(1==0)
                
                find_type=area_tree.find_token(find_var.type)
                assert(find_type!=None)
                if(len(i[1:])!=len(find_var.muti_dimension)):
                    print("维度不匹配 ",oplist[0],"--->",i[0]," 变量原始维度:",len(find_var.muti_dimension),"变量引用维度:",len(i)-1)
                    assert(1==0)
                base=find_var.start_pos
                if(base!=0): code+="ADD EBX "+str(base)+"\n"#加上基地址
                accumulate_demension=[]
                current=1
                for demension in reversed(find_var.muti_dimension):
                    accumulate_demension.append(current)
                    current*=demension
                accumulate_demension=[i*find_type.size for  i  in reversed(accumulate_demension)] #对齐进行修正 计算正确的大小
                for index in range(len(find_var.muti_dimension)) :
                    #需要判断是j是数字还是变量
                    if(i[index+1].isdigit()):
                        if(int(i[index+1])>find_var.muti_dimension[index]): #算了 不想去判断:
                            print("维度超过限制 ",oplist[0],"--->",i[0],"的第",index,"维,变量原始维度:",find_var.muti_dimension[i],"变量引用维度:",int(i[index+1]))
                            assert(1==0)
                        code+="MOV EAX "+i[index+1]+"\n"
                    else:
                        find_var=area_tree.find_token(i[index+1]) 
                        if(find_var==None):
                            print("变量未定义",oplist[0],"--->",i[index+1])
                            assert(1==0)
                        elif(find_var.type!="int"):
                            print("下标只能为int",oplist[0],"--->",i[index+1])
                            assert(1==0)
                        code+="MOV EAX $"+str(find_var.start_pos)+"\n"
                    code+="MUL EAX "+str(accumulate_demension[index])+"\n"
                    code+="ADD EBX EAX\n"
                        #寻找到变量位置                 
                #最后 EAX就是变量的位置！ EBX为左值 EAX为右值
            oplist.clear()
            oplist.append("EBX")  
    elif(name=="OPN"):
        if(rule=="$CONST$"):
            pass
        elif(rule=="$VAR$"):
            pass
        elif(rule=="($OPN$)"):
            pass
        pass    
    elif(name=="TOKEN"):#不需要对其进行修正 
        pass
    elif(name=="CONST"):
        pass
    elif(name=="AREA"):
        for i in codelist:code+=i
        if(rule=="$AREA_S$$AREA_E$"): code+="NOPs\n"
    elif(name=="REGS"):
        pass
    elif(name=="DIM"): #这里要产生巨变！
        type=oplist[0]
        #解析一下a[10][10]这种类型的
        var=y_token.trans_token(oplist[1])
        num=1
        for i in var[1:]: num*=int(i)
        find_type=area_tree.find_token(type)
        # find_var=area_tree.find_token(var[0])
        # if(find_var!=None):
        #     print("重定义符号",var[0])
        #     assert(1==0)
        if(find_type==None):
            print("编译出错,类型未定义")
            assert("1==0")
        if(rule=="$TYPE$->$TOKEN$"): #进行解析
            start_pos=area_tree.clac_current_pos()
            t=y_token()
            t.set_as_variable(var[0],find_type.size*num,type,start_pos,[int(i) for i in var[1:]])
            area_tree.append_var(t,t.size) #只有变量才会分配区域大小
            code="ALLOC "+str(t.size)+"//"+type+"\n" #
        elif(rule=="$TYPE$->$TOKEN$=$STRING$"):
            assert(type=="int" or type=="double")
            string=oplist[2]
            length=num
            if(length<len(string)):
                length=len(string)
            code="ALLOC "+str(length)+"//"+type+"\n"  
            base=str(area_tree.clac_current_pos()) 
            t=y_token()
            t.set_as_variable(var[0],find_type.size*num,type,base,[int(i) for i in var[1:]])
            area_tree.append_var(t)
            for i in range(len(string)):
                code+="MOV "+base+":"+str(i)+" "+str(ord(string[i]))+ "\n"
            code+="MOV "+base+":"+str(len(string))+ " 0\n"
        else:
            print(oplist)
    elif(name=="OP"):
        for i in codelist: code+=i 
        pass
    elif(name=="ADD"):
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
    elif(name=="SUB"):
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
    elif(name=="MUL"): #注意到可能会被修正成代码！ op可能会被修正成位置
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
    elif(name=="DIV"):
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
    elif(name=="AND" or name=="XOR" or name=="OR" or name=="MOD"):
        if(bool(re.match("\\$OPN\\$.+\\$OPN\\$", rule))):
            code="MOV EAX "+str(oplist[0])+"\n"
            code+=name+" EAX "+str(oplist[1])+"\n"
        elif(bool(re.match("\\$OPN\\$.+\\$OP\\$", rule))):
            code=codelist[0]
            code+=name+" EAX "+str(oplist[0])+"\n"
        elif(bool(re.match("\\$OP\\$.+\\$OPN\\$", rule))):
            code=codelist[0]
            code+=name+" EAX "+str(oplist[-1])+"\n"
        elif(bool(re.match("\\$OP\\$.+\\$OP\\$", rule))):
            code=codelist[0]
            code+="MOV EBX EAX\n"
            code+=codelist[1]
            code+=name+" EAX EBX\n"
        else:
            assert(1==0)

    elif(name=="NOT"): #处理单目运算符
        if(rule=="!$OPN$"):
            code="NOT EAX "+str(oplist[0])+"\n"
        elif(rule=="!$OP$"):
            code=codelist[0]
            code+="MOV EBX EAX\n"
            code+="NOT EAX EBX\n"
        else:
            pass
        pass
    elif(name=="GETP"):
        code+="LEA EAX "+str(oplist[0])+"\n"
        pass
    elif(name=="SETP"):
        if(rule=="*$OPN$"): #在此处对oplist进行修正！ or 插入指令  #总是会把计算压入stack
            code+="PUSH "+str(oplist[0])+"\n"
            #oplist=[]
            #code="SEA  EAX" +str(oplist[0])+"\n"
            pass
        elif(rule=="*$OP$"):#eax是需要修正的结果 不支持 EBX也可能被人用掉了！ 我需要一个不会被人用掉的寄存器或者位置！
            for i in codelist: code+=i #PUSH EBX POP
            code+="PUSH EAX\n"
            pass
        else:
            pass
        pass
    elif(name=="EQUAL"):
        #可能会有code针对左边的地方进行计算！
        if(rule=="$VAR$=$OPN$"):
            code="MOV "+str(oplist[0]) +" "+str(oplist[1])+"\n"
        elif(rule=="$VAR$=$OP$"):   
            code=codelist[0]
            code+= "MOV "+str(oplist[0])  + " EAX\n"
        elif(rule=="$SETP$=$OPN$"):  #这里可能会有点问题 
            for i in codelist: code+=i 
            code+="POP EBX\n"
            code+="SEA EBX "+str(oplist[-1])+"\n" #这里的oplist不一定多少个数据
            pass
        elif(rule=="$SETP$=$OP$"):
            for i in codelist: code+=i 
            code+="POP EBX\n"
            code+="SEA EBX EAX\n"
            pass
        else:
            pass
        pass
    elif(name=="SENTENCE"):
        for i in codelist: code+=i 
        pass
    elif(name=="JUDGE"):
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
    elif(name=="IF"):
        code=codelist[0]
        code+="JPIF "+str((codelist[1]).count("\n")+2)+"\n"
        code+=codelist[1]
        code+="JMP "+str((codelist[2]).count("\n")+1)+"\n"
        code+=codelist[2]
        pass
    elif(name=="DO"):
        code=codelist[0]+codelist[1]
        code+="RF\n"
        code+="JPIF -"+str((codelist[0]+codelist[1]).count("\n")+1)+"\n"
        pass
    elif(name=="WHILE"):
        code=codelist[0]
        code+="JPIF "+str(codelist[1].count("\n")+2)+"\n"
        code+=codelist[1]
        code+="JMP -"+str((codelist[0]+codelist[1]).count("\n")+1)+"\n"
        pass
    elif(name=="FOR"):
        #需要看一看有没有3
        code=codelist[0]+codelist[1]
        code+="JPIF "+str((codelist[3]+codelist[2]).count("\n")+2)+"\n"
        code+=codelist[3]+codelist[2]
        code+="JMP -"+str((codelist[1]+codelist[3]+codelist[2]).count("\n")+1)+"\n"
        
        pass
    elif(name=="PRINT"):
        code="OUT "+str(oplist[0])+"\n"
        pass
    elif(name=="IN"):
        code="IN EAX\n"
    elif(name=="FUNCNAME"): #funcname/structure_name
        sub_area=area_tree.new_area(True,oplist[0])
        area_tree=sub_area#创建顶级域 在AREA的时候恢复顶级域
        pass#在这里就要创建新的顶级域了
    elif(name=="FUNC"):#在定义的时候，不要执行语句
        for i in codelist: code+=i #注意到这里已经完成了赋值 这里面分了三段
        revise_code=code.split("\n")[:-1]
        code=""
        for i in range(len(revise_code)):
            toend=len(revise_code)-i
            revise_code[i]=revise_code[i].replace("END",str(toend))
            code=code+revise_code[i]+"\n"
        #需要把code里面的END全部替换掉！
        code+="MOV ESP $0:-6\n"
        code+="MOV EBX $0:-3\n"
        code+="MOV EFG $0:-2\n"
        code+="MOV ETP $0:-1\n" #不用再跳转了！这里已经写好了参数了！ 注意到这里有一个坑按道理来说必须同时还原,
        code+="MOV EBP $0:-5\n" #使用临时寄存器ETP暂时保存该跳转的结果。
        code+="MOV EIP ETP\n"
        code="JMP "+str(code.count("\n")+1)+"\n"+code
        code="ALLOC @"+oplist[1]+"\n"+code
        area_tree=area_tree.father
        #在codelist[0]里面解析double
        t=y_token()
        par=[]
        for i in codelist[0].split("\n"):
            if(i!="" and len(i.split("//"))==2):
                par.append(i.split("//")[1])  
        t.set_as_function(oplist[0],oplist[1],par)
        area_tree.append_var(t)
        #code=codelist[0] #还没处理return问题嘞
        pass
    elif(name=="CALL"):#call 然后eax传入参数！
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
        code+="MOV EBX EAX\n" #保存一下我要压ip的时候用
        
        code+="ADD ESP 6\n"
        code+="MOV ETP ESP\n"
        code+=codelist[0] #压入参数 EAX EBX 可用 EBP ETP 可用否？
        
        code+="MOV EAX EIP\n"
        code+="ADD EAX 4\n"
        code+="MOV $5:EBX EAX\n"#最后才来压入eip! 不行 这里的EAX的值g了
        
        code+="MOV EBP ETP\n" #压完了参数再给ebp复制
        code+="JMP @"+oplist[0]+"\n" #这里需要绝对地址！
        #然后需要执行跳转！
        pass
    # elif(name=="AREA_S"):
    #     sub_area=area_tree.new_area(False,"None")
    #     area_tree=sub_area#创建顶级域 在AREA的时候恢复顶级域        
    #     #在这里分配作用域
    #     pass
    # elif(name=="AREA_E"):
    #     area_tree=area_tree.father
    #     #在这里分配作用域
    #     pass
    elif(name=="tPAR"):#这里是
        for i in codelist: code+=i
        pass
    elif(name=="PAR"):#这里是形参
        #code="SUB EBP 1\n" #不太需要动EBP
        for i in codelist: code+=i
        code+="NOP\n"
        pass
    elif(name=="ARG"): #这里是call的实参  只能使用EAX了 但是我又需要计算op op的值必须要存在eax里面
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
    elif(name=="RETURN"):
        if("$OP$" in rule):
            for i in codelist: code+=i #JMP到最后才行！ 这里怎么写最后啊！
        elif("$OPN$" in rule):
            code="MOV EAX "+oplist[0]+"\n"
        else:
            pass 
        code+="JMP END\n"# 等到func来填充这个就可以了哦
        pass
    elif(name=="TYPE"):
        pass
    elif(name=="STRUCTURE"):
        t=y_token()
        func=[]
        vars=[]
        struture=[]
        for i in area_tree.vars:
            if(i.type==token_type.function): func.append(i)
            elif(i.type==token_type.structure): struture.append(i)
            else: vars.append(i)
        t.set_as_structure(oplist[0],area_tree.clac_current_pos(),func,vars)
        area_tree=area_tree.father
        if(area_tree.find_token(t.name)!=None):
            print(t.name,"结构体已经被定义")
            assert(1==0)
        area_tree.append_var(t)#判断要不要插入这个区域 如果要插入的话 判断是不
        
    elif(name=="ASM"):
        code+=oplist[0].replace("\\n","\n")
        pass
    return code,area_tree