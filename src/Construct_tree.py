import re,itertools
from src.runner import Runner
from src.token_ana import *
from src.postprocesser import Postprocesser
from src.preprocesser import Preprocesser
import src.Compile_tree as Compile_tree
class Compoment:
    Cs={}   #语句类型
    unmatch={}
    deepest_fail_pos = 0    # 全局最远失败位置（用于错误报告）
    deepest_fail_rule = ""  # 最远失败时的规则
    deepest_fail_name = ""  # 最远失败时的非终结符
    original_text = ""      # 原始完整输入（用于计算偏移量）

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
                        if match_text in ["struct","class","void","in","asm","if","do","while","for","out","outnum","else","elseif","elif","func","return","struct","int","double","continue","break","switch","case","default"] :
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
                        if match_text in ["struct","class","void","in","asm","if","do","while","for","out","outnum","else","elseif","elif","func","return","struct","continue","break","switch","case","default"] :
                            return False,text_c,oplist,codelist
                        oplist.append(match_text) #直接把token放进去
                else:
                    # 记录最远失败位置
                    consumed = len(Compoment.original_text) - len(text)
                    if consumed > Compoment.deepest_fail_pos:
                        Compoment.deepest_fail_pos = consumed
                        Compoment.deepest_fail_rule = rule
                        Compoment.deepest_fail_name = self.name
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
                    # 记录最远失败位置
                    consumed = len(Compoment.original_text) - len(text)
                    if consumed > Compoment.deepest_fail_pos:
                        Compoment.deepest_fail_pos = consumed
                        Compoment.deepest_fail_rule = rule
                        Compoment.deepest_fail_name = self.name
                    return False,text_c,oplist,codelist
            else: #这里用来消除关键字
                    dollar_index = rule.find('$')
                    keyword=rule[:dollar_index] if dollar_index != -1 else rule
                    if(text.startswith(keyword)):
                        text=text[len(keyword):]  
                        rule=rule[len(keyword):]  
                    else:
                        # 记录最远失败位置
                        consumed = len(Compoment.original_text) - len(text)
                        if consumed > Compoment.deepest_fail_pos:
                            Compoment.deepest_fail_pos = consumed
                            Compoment.deepest_fail_rule = rule
                            Compoment.deepest_fail_name = self.name
                        return False,text_c,oplist,codelist
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
                # 使用 hash(text) 作为缓存键，节省内存（text可能很长）
                key=(hash(text),self.name,rule)
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
                    # 使用 ASTNode dataclass 替代原始 tuple
                    compiled_code=[ASTNode(
                        name=self.name,
                        rule=rule,
                        oplist=oplist,
                        children=code_list,
                        source=textc[0:len(textc)-len(text)]
                    )]
                    r_code+=compiled_code
                    break
        return flag,text,r_code,r_oplist
class Compiler:
    def __init__(self) -> None:
        pass
    def ana2(self,text,codes=[]):
        """
        顶层解析循环：逐句匹配并累积语法树节点。
        （已简化：去除了退化的状态列表模式，改为直接循环）
        """
        # 记录原始文本用于错误报告
        Compoment.original_text = text
        Compoment.deepest_fail_pos = 0
        Compoment.deepest_fail_rule = ""
        Compoment.deepest_fail_name = ""

        original_len = len(text)
        ans_code = list(codes)

        while text != "":
            progress = 100 - 100 * len(text) / original_len
            print(f"解析进度:{progress:.2f}%")

            matched = False
            for name, sentence in Compoment.Cs.items():
                if sentence.no_start:
                    continue
                succ, textc, code, r_oplist = sentence.Rrcognize(text)
                if succ:
                    text = textc
                    ans_code += code
                    matched = True
                    break

            if not matched:
                # 增强错误报告：显示最远匹配位置
                fail_pos = Compoment.deepest_fail_pos
                context_start = max(0, fail_pos - 20)
                context_end = min(len(Compoment.original_text), fail_pos + 30)
                context = Compoment.original_text[context_start:context_end]
                pointer_offset = fail_pos - context_start

                print(f"\n{'='*60}")
                print(f"编译错误!")
                print(f"  位置: 字符 {fail_pos}/{original_len}")
                print(f"  上下文: ...{context}...")
                print(f"           {' '*pointer_offset}^ 此处失败")
                print(f"  最后尝试的非终结符: {Compoment.deepest_fail_name}")
                print(f"  最后尝试的规则: {Compoment.deepest_fail_rule}")
                print(f"  当前待解析: {text[:50]}{'...' if len(text)>50 else ''}")
                print(f"{'='*60}\n")
                return False, ans_code

        return True, ans_code

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
                # 格式: NAME:configs:attribute
                # 用rsplit从右侧分割，确保configs中可以包含冒号
                parts = line.rsplit(":", 1)  # 从右分割一次，得到 [name:configs, attribute]
                attribute = parts[1] if len(parts) > 1 else ""
                name_configs = parts[0]
                # 再分割第一个冒号得到 name 和 configs
                nc_parts = name_configs.split(":", 1)
                name = nc_parts[0]
                configs_str = nc_parts[1] if len(nc_parts) > 1 else ""
                configs=configs_str.split("#")
                if(configs[-1]==""):
                    configs=configs[0:-1]
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
        if(isinstance(node, (tuple, ASTNode))):
            name=node[0]
            rule=node[1]
            oplist=node[2]
            code_list=node[3]
            source_text=node[4]
            print(prefix+self.cut_str(name)+"-->"+self.cut_str(rule)+"-->"+self.cut_str(str(oplist))+"-->"+self.cut_str(source_text))
            # 在处理形参声明的子节点前设置标志
            if name in ("PAR", "tPAR"):
                Compile_tree._in_param_declaration = True
            if(code_list!=[]):
                for i in code_list:
                    t_code=""
                    for j in i:
                        b_code=self.show_and_compile(j,"",prefix+" ")
                        t_code+=b_code
                    codelists.append(t_code)  # 保留空代码占位符，保持与子树的位置对应
                code_list=codelists
            if name in ("PAR", "tPAR"):
                Compile_tree._in_param_declaration = False
            b_code=""
            b_code,self.area_tree=Compile_tree.Complie(name,rule,oplist,code_list,self.area_tree)
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
