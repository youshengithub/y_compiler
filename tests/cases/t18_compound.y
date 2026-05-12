// 测试18: 复合运算 (多步计算)
// 期望输出: Z (2*3+4*5=6+20=26, 26+64=90='Z')
int a;
int b;
int c;
int d;
int r;
a=2;
b=3;
c=4;
d=5;
r=a*b;
r=r+c*d;
r=r+64;
out(r);
