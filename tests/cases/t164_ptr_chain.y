// expected: 100
int x;
x = 100;
int *p;
p = &x;
int *q;
q = p;
outnum(*q);
