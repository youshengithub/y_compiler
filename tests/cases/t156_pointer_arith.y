// expected: H
int arr[3];
arr[0] = 72;
arr[1] = 73;
arr[2] = 74;
int *p;
p = &arr;
int v1;
v1 = *p;
out(v1);
