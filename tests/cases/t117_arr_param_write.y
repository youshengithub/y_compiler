// 测试117: 数组作为函数参数 - 写入
// 函数接收数组并修改其元素
// 期望输出: B
int fill(int a[5], int val){
    int i;
    for(i=0;i<5;i++){
        a[i] = val;
    }
    return 0;
}
int arr[5];
arr[0] = 0;
arr[1] = 0;
arr[2] = 0;
arr[3] = 0;
arr[4] = 0;
fill(arr, 66);
out(arr[2]);
