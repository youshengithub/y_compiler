import re

#include
#define
class preprocesser:
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
                file_path=line[8:-1]
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except FileNotFoundError:
                    print("错误：文件未找到。请检查文件路径是否正确。")
                except IOError:
                    print("错误：无法读取文件。")
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
                defines=line[7].split(" ")
                tags[defines[0]]=defines[1]
            else:
                for k,v in tags.items():
                    line=line.replace(k,v)
                code+=line+"\n"
        return code
    def process_space(self,text):
        return text.replace('\n', '').replace(' ', '').replace('\t', '')
    def process(self,text):#处理预处理器命令#
        text=self.process_include(text)
        text=self.process_define(text)
        text=self.process_note(text)
        text=self.process_space(text)
        return text