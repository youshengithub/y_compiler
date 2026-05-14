// expected: 20,10
int a;
int b;
a = 10;
b = 20;
int *pa;
int *pb;
pa = &a;
pb = &b;
int temp;
temp = *pa;
*pa = *pb;
*pb = temp;
outnum(a);
out(44);
outnum(b);
