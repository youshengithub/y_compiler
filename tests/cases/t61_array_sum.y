// 测试61: 数组求和
// 期望输出: 6 (1+2+3=6)
int a[3];
a[0]=1;
a[1]=2;
a[2]=3;
int sum;
sum=0;
int i;
for(i=0;i<3;i++){
    sum += a[i];
}
outnum(sum);
