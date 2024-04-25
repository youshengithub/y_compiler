#此数据结构用于记录各个token的属性
from enum import Enum
class token_type(Enum):
    function=1
    variable=2
    structure=3
class y_token:
    def __init__(self,type,name=""):
        self.type=type
        self.name=name
        pass
class varea:#用于实现 函数 变量和 结构体的 作用域 oplist仍然需要用于操作数 每当有一个{}就需要实现一个添加一个新的作用域
    def __init__(self,father,name=" "):
        self.father=father
        self.name=name
    def new_area(self):
        if not hasattr(self,"areas"):
            self.areas=[]
        area=varea(self)
        self.areas.append(area)
        return area
    def append_area(self,area):
        if not hasattr(self,"areas"):
            self.areas=[]
        self.areas.append(area)
    def append_var(self,var):
        if not hasattr(self,"vars"):
            self.vars=[]
        self.vars.append(var)
    def find_token(self,name,area_name=" "):#沿树寻找
        bfs=[]
        bfs.append(self.father)
        bfs.append(self)
        while bfs.count()!=0:
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
