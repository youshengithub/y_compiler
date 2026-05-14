// expected: AB
int *p;
p = malloc(2);
*p = 65;
*(p + 1) = 66;
out(*p);
out(*(p + 1));
free(p);
