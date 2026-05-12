// 测试14: for循环
// 期望输出: 5 (循环5次, 5+48=53='5')
int a;
int cnt;
cnt=0;
for(a=0;a<5;a=a+1){
    cnt=cnt+1;
}
cnt=cnt+48;
out(cnt);
