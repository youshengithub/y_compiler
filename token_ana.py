#此数据结构用于记录各个token的属性
from enum import Enum
class token_type(Enum):
    function=1
    variable=2
    structure=3
class y_token:
    def __init__(self,type=token_type.function,name=""):
        self.type=type
        self.name=name
    def set_as_function(self,name,paras=[]):
        self.type=token_type.function
        self.paras=paras
        self.name=name
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
        self.fuctions=functions
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
        pass
    @staticmethod
    def trans_var(var):
        tokens=var.split(".")
        ans=[]
        for i in tokens:
            ans.append(y_token.trans_token(i))
        return ans
class varea:#用于实现 函数 变量和 结构体的 作用域 oplist仍然需要用于操作数 每当有一个{}就需要实现一个添加一个新的作用域
    def __init__(self,father,is_top_area=True,name=" "): 
        self.father=father
        self.name=name
        self.is_top_area=is_top_area
        self.current_pos=0
    def new_area(self,is_top_area):
        if not hasattr(self,"areas"):
            self.areas=[]
        area=varea(self,is_top_area)
        self.areas.append(area)
        return area
    def append_area(self,area):
        if not hasattr(self,"areas"):
            self.areas=[]
        self.areas.append(area)
    def add_current_pos(self,size):
        self.current_pos+=size
    def append_var(self,var,size=0): #有的是类型，有的是函数,只有变量才需要size  注意到类型不需要大小！
        if not hasattr(self,"vars"):
            self.vars=[]
        self.vars.append(var)
        self.find_top_father().add_current_pos(size) #只在顶级域里面加入size 每一个函数都是一个顶级域,
    def find_top_father(self):
        if(self.is_top_area) :return self
        else: return self.father.find_top_father()
    def clac_current_pos(self):
        return self.find_top_father().current_pos
    def find_token(self,name,area_name=" "):#沿树寻找
        bfs=[]
        bfs.append(self.father)
        bfs.append(self)
        while len(bfs)!=0:
            tmp=bfs.pop()
            if(tmp==None): continue
            bfs.append(tmp.father)
            if(area_name!=tmp.name): continue
            if hasattr(tmp,"vars"):
                for i in tmp.vars:
                    if i.name==name:
                        return i   
        return None                 
if __name__=="__main__":
    a=varea(None)
    b=varea(a)
    a.append_area(b)
    a.append_var(y_token(token_type.variable))
    print(a)
    print(y_token.trans_var("a[10][c].b[i][j]"))
    