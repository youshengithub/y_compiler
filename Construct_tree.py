import re,itertools
from runner import Runner
from token_ana import *
from postprocesser import Postprocesser
from preprocesser import Preprocesser
import Compile_tree
class Compoment:
    Cs={}   #语句类型
    unmatch={}
    def __init__(self, name_,config_,repeat_,no_start,is_keywords):
        self.configs=config_
        self.name=name_
        self.repeat=repeat_
        self.no_start=no_start
        self.is_keywords=is_keywords
    def HandleR(self,rule,text): 
        text_c=text
        oplist=[]
        codelist=[]
        while(rule!=""):
            if(rule[0]=="@"): #这里很麻烦的啦！ 
                next_index = rule[1:].find('@')
                if(next_index==-1): 
                    return False,text_c,oplist,codelist
                pattern=rule[1:next_index+1] 
                match = re.search(pattern, text)
                if match!=None :
                    match_text=text[:match.regs[0][1]] #仿佛这是最简单的办法
                    text=text[match.regs[0][1]:]  
                    rule=rule[2+len(pattern):]  
                    if(self.name=="VAR"): #需要进行判断是什么词性
                        if match_text in ["struct","class","void","in","asm","if","do","while","for","out","else","func","return","struct","int","double","continue"] :
                            return False,text_c,oplist,codelist
                        oplist.append(match_text)
                    elif(self.name=="CONST" ):
                        oplist.append(match.group(0))
                    elif(self.name=="STRING"): #需要有一个table 
                        oplist.append(match.group(0)[1:-1])
                    elif(self.name=="REGS"):
                        oplist.append(match.group(0)) #直接把名称放进去
                    elif(self.name=="TYPE"):
                        oplist.append(match.group(0)) #直接把类型放进去
                    elif(self.name=="TOKEN"):
                        if match_text in ["struct","class","void","in","asm","if","do","while","for","out","else","func","return","struct","continue"] :
                            return False,text_c,oplist,codelist
                        oplist.append(match_text) #直接把token放进去
                else:
                    #if(text_c!=text): print("正则表达式无法识别---",rule,"-->\n",text)
                    return False,text_c,oplist,codelist
            elif(rule.startswith("$")):
                next_index = rule[1:].find('$')
                if(next_index==-1): return False
                name=rule[1:next_index+1]
                succ,text,code,r_oplist=Compoment.Cs[name].Rrcognize(text) #消除掉rule部分 并且这里的code 没有用上！
                if(succ==True):
                    dollar_index = rule[1:].find('$')
                    rule=rule[2+dollar_index:] 
                    oplist+=r_oplist
                    if(code!=""):
                        codelist+=[code]
                    continue
                else:
                    #if(text_c!=text):     print("$$识别错误---",rule,"-->\n",text,"\n")
                    return False,text_c,oplist,codelist
            else: #这里用来消除关键字
                    dollar_index = rule.find('$')
                    keyword=rule[:dollar_index] if dollar_index != -1 else rule
                    if(text.startswith(keyword)):
                        text=text[len(keyword):]  
                        rule=rule[len(keyword):]  
                    else:
                        #if(text_c!=text): print("有多余关键字未识别---",rule,"-->\n",text)
                        return False,text_c,oplist,codelist
        #print("识别成功:",self.name,"->",text_c,"--->",c_rule)
        return True,text,oplist,codelist
    def Rrcognize(self,text):
        flag=False
        repeat=True
        r_oplist=[]
        r_code=[]
        while(repeat): #规则必须也是寻找最有可能的匹配
            repeat=False
            for rule in self.configs:#通过语句构建,这个选择一种规则！
                textc=text
                key=(hash(text),self.name,rule) #使用hash节约内存
                if(key in Compoment.unmatch ): #使用缓存，避免重复解析
                    if(Compoment.unmatch[key]=="PROCESSING"): #陷入重入
                        succ=False
                    else:
                        succ,text,oplist,code_list=Compoment.unmatch[key]
                else:
                    Compoment.unmatch[key]="PROCESSING"
                    succ,text,oplist,code_list=self.HandleR(rule,textc) #这里面没有传入代码 
                    Compoment.unmatch[key]=(succ,text,oplist,code_list,)
                if(succ): 
                    flag=True
                    repeat=self.repeat
                    r_oplist=oplist
                    compiled_code=[(self.name,rule,oplist,code_list,textc[0:len(textc)-len(text)] )]
                    r_code+=compiled_code #+" Rule: "+rule
                    break   #这里仿佛也不应该call;最好是用 
        return flag,text,r_code,r_oplist
class Compiler:
    #VARPos=环境
    def __init__(self) -> None:
        pass
    def ana2(self,text,codes=[]):
        state=[(text,codes)]
        ans_code=[]
        while len(state)!=0:
            (n_text,n_codes)=state[0]
            print(f"解析进度:{100-100*len(n_text)/len(text):.2f}%")
            state=state[1:]
            ans_code=n_codes
            if(n_text==""): break
            single_succ=""
            for name,sentence in Compoment.Cs.items():
                if(sentence.no_start==True): continue
                succ,textc,code,r_oplist=sentence.Rrcognize(n_text)
                if(succ==True):
                    state.append((textc,n_codes+code))
                    single_succ=name
                    break
            if(single_succ==""):    print("编译发生错误,当前编译位置",n_text if len(n_text)<50 else n_text[:50]+"...")
        return single_succ!="",ans_code
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
                if(line==""):continue
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
                Compoment.Cs[name]=Compoment (name,revised_configs,"REPEAT" in attribute, "NO_START" in attribute,"IS_KEYWORDS" in attribute)  
    def Complie_file(self,text):
        state,codelists=self.ana2(text)
        if(state):
            return state,self.real_compile(codelists)
        else:
            return False,""
    def cut_str(self,i,limits=50):
        if(len(i)<limits): return i
        else: return i[:limits]+"..."
    def show_and_compile(self,node,code,prefix=""):
        codelists=[]
        if(isinstance(node,tuple)):
            name=node[0]
            rule=node[1]
            oplist=node[2]
            code_list=node[3]
            source_text=node[4]
            if(code_list!=[]):
                for i in code_list:
                    t_code=""
                    for j in i:
                        b_code=self.show_and_compile(j,"",prefix+" ")
                        t_code+=b_code
                    if(t_code!=""):
                        codelists.append(t_code)
                code_list=codelists
            b_code,self.area_tree=Compile_tree.Complie(name,rule,oplist,code_list,self.area_tree)
            print(prefix+self.cut_str(name)+"-->"+self.cut_str(rule)+"-->"+self.cut_str(str(oplist))+"-->"+self.cut_str(str(code_list))+"-->"+self.cut_str(source_text)+"-->"+b_code)
            code+=b_code
            return code
        else:   assert(1==0)
    def real_compile(self,c_lists):
        area_tree=varea(None,True,"Main")
        area_tree.append_var(y_token(token_type.structure,"int",1))
        area_tree.append_var(y_token(token_type.structure,"double",1))
        code=""
        self.area_tree=area_tree
        for i in c_lists:
            b_code=self.show_and_compile(i,"")
            code+=b_code
        print(area_tree)
        return code
if __name__=="__main__":
    a=Compiler()
    b=Runner()
    c=Postprocesser()
    d=Preprocesser()
    a.construct_componets("Config.txt")
    with open("code.txt", 'r', encoding='utf-8') as file:
        content = file.read()
    preprocessed_code=d.process(content)
    state,code=a.Complie_file(preprocessed_code)
    if state:print(code)
    # code=c.process(code)
    # with open("IR.txt", 'w', encoding='utf-8') as file:
    #     file.write(code)
    #b.Run_from_code(code.split("\n"))