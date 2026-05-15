// 测试189: 表达式求值器（后缀表达式）
// 用栈计算后缀表达式: "3 4 + 2 * 5 -" = (3+4)*2-5 = 9
// 编码: 正数=自身, +=-1, -=-2, *=-3 (用100+x编码避免负数)
// tokens: 3,4,101,2,103,5,102 (101=+, 102=-, 103=*)
// 期望输出: 9
int tokens[7];
tokens[0]=3; tokens[1]=4; tokens[2]=101;
tokens[3]=2; tokens[4]=103; tokens[5]=5; tokens[6]=102;
int stack[10];
int top;
top = 0;
int i;
int tok;
int a;
int b;
int result;
for(i=0;i<7;i++){
    tok = tokens[i];
    if(tok < 100){
        stack[top] = tok;
        top++;
    } else {
        top--;
        b = stack[top];
        top--;
        a = stack[top];
        if(tok == 101){
            result = a + b;
        }
        if(tok == 102){
            result = a - b;
        }
        if(tok == 103){
            result = a * b;
        }
        stack[top] = result;
        top++;
    }
}
top--;
outnum(stack[top]);
