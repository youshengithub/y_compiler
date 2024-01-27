import csv
companys=set()
filename = "example.csv"
import re
def remove_chinese_chars(text):
    # 使用正则表达式删除中文字符
    return re.sub(r'[\u4e00-\u9fff]+', '', text)
def extract_lines(filename):
    out=[]
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    extract = False
    extracted_lines = []
    for line in lines:
        if "联系我们" in line:
            extract = True
            continue
        if extract:
            if line.strip() == "":  # 检测空行
                if(extracted_lines[-1] not in companys):
                    companys.add(extracted_lines[-1] )
                    revise=[remove_chinese_chars(extracted_lines[-1])]+extracted_lines[:-1]
                    out.append(revise)
                extract = False
                extracted_lines = []
            else:
                extracted_lines.append(line.strip())
    return out
# 使用这个函数并打印结果
filename = 'data.txt'  # 替换为你的文件名
out=extract_lines(filename)
filename = "output.csv"
# 打开文件进行写入
with open(filename, "w", newline='', encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    # 写入数据
    for row in out:
        writer.writerow(row)
print(f"数据已写入到 CSV 文件 {filename}")