// 测试112: 数组表达式下标
// 期望输出: CE
int a[5];
int i;
for(i=0; i<5; i++){
    a[i] = i + 65;
}
int j;
j = 1;
out(a[j+1]);
out(a[j*2+2]);
