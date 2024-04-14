#此数据结构用于记录各个token的属性
from enum import Enum
class token_type(Enum):
    function=1
    variable=2
    structure=3
class y_token:
    def __init__(self,type):
        self.type=type
        pass
        