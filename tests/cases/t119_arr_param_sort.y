// 测试119: 数组参数排序（冒泡排序）
// 通过函数对数组进行排序
// arr = [3,1,2] → 排序后 [1,2,3]
// arr[0]=1, 1+48=49='1'
// 期望输出: 1
int sort(int a[3], int n){
    int i;
    int j;
    int tmp;
    int lim;
    int k;
    for(i=0;i<n-1;i++){
        lim = n-1;
        lim -= i;
        for(j=0;j<lim;j++){
            k = j+1;
            if(a[j]>a[k]){
                tmp = a[j];
                a[j] = a[k];
                a[k] = tmp;
            }
        }
    }
    return 0;
}
int arr[3];
arr[0] = 3;
arr[1] = 1;
arr[2] = 2;
sort(arr, 3);
int r;
r = arr[0] + 48;
out(r);
