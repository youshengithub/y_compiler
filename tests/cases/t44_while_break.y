// 测试: while 中 break
// 循环 0,1,2 在 i==2 时 break, 累加 0+1=1
// 期望输出: 1 (1+48=49='1')
int i;
int s;
i = 0;
s = 0;
while(i < 10){
    if(i == 2){
        break;
    }
    s = s + i;
    i = i + 1;
}
s = s + 48;
out(s);
