import re
class Preprocesser:
    pass
    def process_note(self,text):
        # 先处理多行注释 /* ... */
        while '/*' in text:
            start = text.find('/*')
            end = text.find('*/', start + 2)
            if end == -1:
                text = text[:start]  # 未闭合则删到末尾
            else:
                text = text[:start] + text[end + 2:]
        # 再处理单行注释 //
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
                content=""
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except FileNotFoundError:
                    print("错误：文件未找到。请检查文件路径是否正确:",file_path)
                    continue
                except IOError:
                    print("错误：无法读取文件:",file_path)
                    continue
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
                defines=line[len("#define "):].split(" ")
                tags[defines[0]]=defines[1]
            elif(line.startswith("#undefine")):
                defines=line[len("#undefine "):].split(" ")
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
        # 只保留"字母数字 字母数字"之间的空格
        # 其他所有空格（符号前/符号后）都删掉
        result=[]
        i = 0
        while i < len(s):
            if s[i].isspace():
                # 向前看：前一个字符是字母数字，后一个字符也是字母数字 → 保留
                if result and result[-1].isalnum():
                    # 找到下一个非空格字符
                    j = i + 1
                    while j < len(s) and s[j].isspace():
                        j += 1
                    if j < len(s) and s[j].isalnum():
                        result.append(' ')
                # 否则跳过空格
                i += 1
                while i < len(s) and s[i].isspace():
                    i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)
    def process_space(self,text): #这样处理会失去边界定义需要换一条句子dim-> 表示 to这个怎么样 我觉得还行
        pre=self.remove_spaces_outside_quotes(text.replace('\n', '').replace('\t', ''))
        next=self.remove_spaces_around_symbols(pre)
        ans=next.replace('\x00', ' ')
        # 合并 else if → elif（方便语法解析）
        ans=ans.replace('else if', 'elif')
        # 将 && || 替换为特殊 token，避免与位运算 & | 冲突
        ans=ans.replace('&&', '~and~')
        ans=ans.replace('||', '~or~')
        return ans
    def process(self,text):#处理预处理器命令#
        text=self.process_include(text)
        text=self.process_define(text)
        text=self.process_note(text)
        text=self.process_space(text)
        return text