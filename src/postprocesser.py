import re

#除去里面的标志 ALLOC @ 换成NOP  JMP @设置指定位置
class Postprocesser:
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
    def process(self,text):
        text=self.process_note(text)
        tags={}
        revise_code=text.split("\n")[:-1]
        code=""
        for i in range(len(revise_code)):
            tokens=revise_code[i].split(" ")
            if(tokens[0]=="ALLOC" and tokens[1].startswith("@")):
                name=tokens[1][1:]
                assert(name not in tags)
                tags[name]=i
                revise_code[i]="NOP"
            elif(tokens[0]=="JMP" and tokens[1].startswith("@")):   
                name=tokens[1][1:]
                assert(name in tags)
                toend=tags[name]-i+2
                revise_code[i]="JMP "+str(toend)
            code+=revise_code[i]+"\n"
        return code