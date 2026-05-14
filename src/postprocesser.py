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

    def constant_fold(self, text):
        """常量折叠优化：将编译期可确定的运算直接折叠为结果。
        关键：保持总行数不变（用NOP替代被折叠的行），避免破坏JMP偏移。
        """
        lines = text.split("\n")
        i = 0
        folded_count = 0
        while i + 1 < len(lines):
            line = lines[i].strip()
            next_line = lines[i+1].strip()
            # 模式1：MOV $N <const> + OP $N <const>
            m1 = re.match(r'^MOV (\$\d+) (-?\d+)$', line)
            m2 = re.match(r'^(ADD|SUB|MUL|DIV|MOD|AND|OR|XOR) (\$\d+) (-?\d+)$', next_line) if m1 else None
            if m1 and m2 and m1.group(1) == m2.group(2):
                val1 = int(m1.group(2))
                op = m2.group(1)
                val2 = int(m2.group(3))
                result = self._try_fold(op, val1, val2)
                if result is not None:
                    lines[i] = f"MOV {m1.group(1)} {result}"
                    lines[i+1] = "NOP"
                    folded_count += 1
                    i += 2
                    continue
            # 模式2：MOV EAX <const> + OP EAX <const>
            m1r = re.match(r'^MOV EAX (-?\d+)$', line)
            m2r = re.match(r'^(ADD|SUB|MUL|DIV|MOD) EAX (-?\d+)$', next_line) if m1r else None
            if m1r and m2r:
                val1 = int(m1r.group(1))
                op = m2r.group(1)
                val2 = int(m2r.group(2))
                result = self._try_fold(op, val1, val2)
                if result is not None:
                    lines[i] = f"MOV EAX {result}"
                    lines[i+1] = "NOP"
                    folded_count += 1
                    i += 2
                    continue
            i += 1
        result_text = "\n".join(lines)
        # 递归折叠（折叠后可能产生新的可折叠序列）
        if folded_count > 0:
            return self.constant_fold(result_text)
        return result_text

    def _try_fold(self, op, val1, val2):
        """尝试常量折叠运算，返回结果或 None"""
        try:
            if op == "ADD": return val1 + val2
            elif op == "SUB": return val1 - val2
            elif op == "MUL": return val1 * val2
            elif op == "DIV" and val2 != 0: return val1 // val2
            elif op == "MOD" and val2 != 0: return val1 % val2
            elif op == "AND": return val1 & val2
            elif op == "OR": return val1 | val2
            elif op == "XOR": return val1 ^ val2
        except:
            pass
        return None

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
        # 常量折叠优化（保持行数不变，用NOP替代被折叠的行）
        code = self.constant_fold(code)
        return code