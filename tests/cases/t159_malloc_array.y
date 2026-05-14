// expected: ABCDE
int *arr;
arr = malloc(5);
int i;
for(i = 0; i < 5; i++){
    *(arr + i) = 65 + i;
}
for(i = 0; i < 5; i++){
    int v;
    v = *(arr + i);
    out(v);
}
free(arr);
