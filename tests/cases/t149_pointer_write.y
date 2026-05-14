// expected: 99
int x;
x = 10;
int *p;
p = &x;
*p = 99;
outnum(x);
