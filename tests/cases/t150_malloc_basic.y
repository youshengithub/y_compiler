// expected: A
int *p;
p = malloc(5);
*p = 65;
int v;
v = *p;
out(v);
free(p);
