// 测试183: 字符串处理 — 统计元音字母
// 字符串 "Hello World" (ASCII: 72,101,108,108,111,32,87,111,114,108,100)
// 元音: e(101), o(111), o(111) = 3个
// 期望输出: 3
int isVowel(int ch){
    if(ch == 97){ return 1; }
    if(ch == 101){ return 1; }
    if(ch == 105){ return 1; }
    if(ch == 111){ return 1; }
    if(ch == 117){ return 1; }
    if(ch == 65){ return 1; }
    if(ch == 69){ return 1; }
    if(ch == 73){ return 1; }
    if(ch == 79){ return 1; }
    if(ch == 85){ return 1; }
    return 0;
}
int countVowels(int str[11], int len){
    int i;
    int count;
    count = 0;
    for(i=0;i<len;i++){
        if(isVowel(str[i]) == 1){
            count++;
        }
    }
    return count;
}
int text[11];
text[0]=72; text[1]=101; text[2]=108; text[3]=108; text[4]=111;
text[5]=32; text[6]=87; text[7]=111; text[8]=114; text[9]=108; text[10]=100;
int r;
r = countVowels(text, 11);
outnum(r);
