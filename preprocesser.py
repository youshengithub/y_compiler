import re
class Preprocesser:
    pass
    def process_note(self,text):
        content=""
        file=text.split("\n")
        for line in file:
            pos=line.find("//")
            if pos!=-1:
                content+=line[0:pos]+"\n"
            else:
                content+=line+"\n"
        return content
   
    def process_include(self,text):
        lines=text.split("\n")
        code=""
        for line in lines:
            if(line.startswith("#include")):
                file_path=line[9:-1]
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except FileNotFoundError:
                    print("错误：文件未找到。请检查文件路径是否正确:",file_path)
                except IOError:
                    print("错误：无法读取文件:",file_path)
                code+=self.process_include(content)
            else:
                code+=line+"\n"
        return code
    def process_define(self,text):
        tags={}
        lines=text.split("\n")
        code=""
        for line in lines:
            if(line.startswith("#define")):
                defines=line[8:].split(" ")
                tags[defines[0]]=defines[1]
            elif(line.startswith("#undefine")):
                defines=line[20:].split(" ")
                if(defines[0] in tags):
                    del tags[defines[0]]
            else:
                for k,v in tags.items():
                    line=line.replace(k,v)
                code+=line+"\n"
        return code
    def remove_spaces_outside_quotes(self,text):#删除不在引号的空格
        in_quotes = False
        result = []
        for char in text:
            if char == '"':
                in_quotes = not in_quotes

            if(char==' ' and in_quotes):
                result.append('\x00')#占位符
            else:
                result.append(char)
        return ''.join(result)
    def remove_spaces_around_symbols(self,s):
        result=[]
        last_char_was_non_alpha_numeric = None
        
        for char in s:
            # 检查当前字符是否为空格
            if char.isspace():
                # 如果前一个字符是非字母数字，则跳过此空格
                if last_char_was_non_alpha_numeric:
                    continue
                # 否则，添加空格到结果
                else:
                    result.append(char)
            else:
                # 非空格字符，直接添加到结果
                result.append(char)
                # 更新标志位
                last_char_was_non_alpha_numeric = not char.isalnum()
        
        # 返回处理后的字符串
        return ''.join(result)
    def process_space(self,text): #这样处理会失去边界定义需要换一条句子dim-> 表示 to这个怎么样 我觉得还行
        pre=self.remove_spaces_outside_quotes(text.replace('\n', '').replace('\t', ''))
        next=self.remove_spaces_around_symbols(pre)
        ans=next.replace('\x00', ' ')
        return ans
    def process(self,text):#处理预处理器命令#
        text=self.process_include(text)
        text=self.process_define(text)
        text=self.process_note(text)
        text=self.process_space(text)
        return text