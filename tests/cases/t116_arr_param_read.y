// 测试116: 数组作为函数参数 - 读取
// 函数接收数组参数，读取其中元素
// sum(arr, 3) = arr[0]+arr[1]+arr[2] = 65+1+2 = 68 = 'D'
// 期望输出: D
int sum(int a[3], int n){
    int s;
    int i;
    s = 0;
    for(i=0;i<n;i++){
        s += a[i];
    }
    return s;
}
int arr[3];
arr[0] = 65;
arr[1] = 1;
arr[2] = 2;
int r;
r = sum(arr, 3);
out(r);
