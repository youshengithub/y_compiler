// 测试71: while循环求和 1+2+...+10=55
// 期望输出: 55
int i;
int sum;
i = 1;
sum = 0;
while(i<=10){
    sum += i;
    i++;
}
outnum(sum);
