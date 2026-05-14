// 测试23: 多重循环嵌套
// 期望输出: 9 (3*3=9, 9+48=57='9')
int i;
int j;
int cnt;
cnt=0;
for(i=0;i<3;i=i+1){
    for(j=0;j<3;j=j+1){
        cnt=cnt+1;
    }
}
cnt=cnt+48;
out(cnt);
