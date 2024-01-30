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

        return text
    def process_define(self,text):
        return text
    def process_space(self,text):
        return text.replace('\n', '').replace(' ', '').replace('\t', '')
    def process(self,text):#处理预处理器命令#
        text=self.process_include(text)
        text=self.process_define(text)
        text=self.process_note(text)
        text=self.process_space(text)
        return text