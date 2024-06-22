#此数据结构用于记录各个token的属性
from enum import Enum

token_and_area_id=0
class token_type(Enum):
    function=1
    variable=2
    structure=3
class y_token:
    def __init__(self,type=token_type.function,name="",size=0):
        global token_and_area_id
        token_and_area_id+=1
        self.id=token_and_area_id
        self.type=type
        self.name=name
        self.size=size
        self.functions=[]
        self.vars=[]
        
    def set_as_function(self,return_types,name,paras=[]):
        self.type=token_type.function
        self.paras=paras
        self.name=name
        self.return_types=return_types
    def set_as_variable(self,name,size,type,start_pos,muti_dimension=[]):
        self.type=token_type.variable
        self.name=name
        self.size=size #记住这里是总大小
        self.type=type
        self.start_pos=start_pos
        self.muti_dimension=muti_dimension
    def set_as_structure(self,name,size,functions=[],vars=[]):  
        self.type=token_type.structure
        self.size=size
        self.name=name
        self.functions=functions
        self.vars=vars
    def get_type(self):
        return self.type
    @staticmethod
    def trans_token(token):
        infos=token.split("[")
        ans=[]
        for i in infos:
            ans.append(i.replace(']', ''))
        return ans
    @staticmethod
    def trans_var(var):
        tokens=var.split(".")
        ans=[]
        for i in tokens:
            ans.append(y_token.trans_token(i))
        return ans
    def __str__(self):
        ans=f'ID:{self.id},token名:{self.name},类型:{self.type}'
        if(self.type==token_type.structure):
            ans+=f'拥有函数:{self.functions},拥有变量:{self.vars}'
            pass
        elif(self.type==token_type.variable):
            
            pass
        elif(self.type==token_type.function):
            ans+=f'返回类型:{self.return_types},参数类型:{self.paras}'
        else:
            ans+=f'大小:{self.size},起始位置:{self.start_pos},维度{self.muti_dimension}'
            pass
        return ans
    def __repr__(self):
        return self.__str__()
class varea:#用于实现 函数 变量和 结构体的 作用域 oplist仍然需要用于操作数 每当有一个{}就需要实现一个添加一个新的作用域
    def __init__(self,father,is_top_area=True,name=" ",level=1): 
        global token_and_area_id
        token_and_area_id+=1
        self.id=token_and_area_id#用于标识唯一id
        self.father=father
        self.name=name
        self.is_top_area=is_top_area
        self.current_pos=0
        self.areas=[]
        self.vars=[]
        self.level=level
    def new_area(self,is_top_area,name=""):
        if not hasattr(self,"areas"):
            self.areas=[]
        area=varea(self,is_top_area,name,self.level+1)
        self.areas.append(area)
        return area
    def append_area(self,area):
        self.areas.append(area)
    def add_current_pos(self,size):
        self.current_pos+=size
    def append_var(self,var,size=0): #有的是类型，有的是函数,只有变量才需要size  注意到类型不需要大小！
        self.vars.append(var)
        self.find_top_father().add_current_pos(size) #只在顶级域里面加入size 每一个函数都是一个顶级域,
    def find_top_father(self):
        if(self.is_top_area) :return self
        else: return self.father.find_top_father()
    def clac_current_pos(self):
        return self.find_top_father().current_pos
    def __str__(self):
        ans=" "*self.level+f',ID:{self.id},层级:{self.level},顶级域:{self.is_top_area},区域名{self.name},token数:{len(self.vars)},区域数:{len(self.areas)}\n'
        if self.vars!=[]:
            ans+=" "*self.level+"--展示变量中--\n"
            for i in self.vars:
                ans+=" "*(self.level+1)+str(i)+"\n"
        if self.areas!=[]:
            ans+=" "*self.level+"--展示区域中--\n"
            for i in self.areas:
                ans+=" "*self.level+str(i)
        return ans
    def __repr__(self):
        return self.__str__()
    def find_area(self,area_name):#
        bfs=[]
        bfs.append(self.father)
        bfs.append(self)
        find_ans=None
        while len(bfs)!=0:
            tmp=bfs.pop()
            if(tmp==None): continue
            bfs.append(tmp.father)
            if tmp.name==area_name:
                find_ans=tmp
                break
        return find_ans
    def find_token(self,name):#沿树寻找
        bfs=[]
        bfs.append(self.father)
        bfs.append(self)
        while len(bfs)!=0:
            tmp=bfs.pop()
            if(tmp==None): continue
            bfs.append(tmp.father)
            #if(area_name!=tmp.name): continue
            if hasattr(tmp,"vars"):
                for i in tmp.vars:
                    if i.name==name:
                        return i   
        return None          
def test(area_tree):
    sub_area=area_tree.new_area(True) #添加子节点
    area_tree=sub_area #使得子节点成为当前节点
if __name__=="__main__":
    a=varea(None)
    print(a)
    test(a)
    print(a)
    
    
    # b=varea(a)
    # a.append_area(b)
    # a.append_var(y_token(token_type.variable))
    # print(a)
    # print(y_token.trans_var("a[10][c].b[i][j]"))