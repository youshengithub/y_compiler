// 测试118: 数组参数传递给另一个函数
// 函数A接收数组，再传给函数B
// 期望输出: A
int get(int a[3], int i){
    return a[i];
}
int first(int a[3]){
    return get(a, 0);
}
int arr[3];
arr[0] = 65;
arr[1] = 66;
arr[2] = 67;
int r;
r = first(arr);
out(r);
