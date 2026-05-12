// 测试88: 字符串内置函数 - strlen
// 手动实现 strlen 用 while 循环
// 期望输出: 5 (53)
int s[10] = "Hello";
int len;
len = 0;
int i;
i = 0;
while(s[i] != 0){
    len = len + 1;
    i = i + 1;
}
len = len + 48;
out(len);
