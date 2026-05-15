// 测试190: 综合压力测试 — 递归归并排序
// 对 [5,2,8,1,9,3,7,4] 进行归并排序
// 排序后 [1,2,3,4,5,7,8,9]，输出前4个之和=1+2+3+4=10
// 期望输出: 10
int arr[8];
int tmp[8];
int merge(int a[8], int t[8], int lo, int mid, int hi){
    int i;
    int j;
    int k;
    for(i=lo;i<=hi;i++){
        t[i] = a[i];
    }
    i = lo;
    j = mid + 1;
    k = lo;
    while(i <= mid){
        if(j > hi){
            a[k] = t[i];
            i++;
            k++;
        } else {
            if(t[i] <= t[j]){
                a[k] = t[i];
                i++;
                k++;
            } else {
                a[k] = t[j];
                j++;
                k++;
            }
        }
    }
    while(j <= hi){
        a[k] = t[j];
        j++;
        k++;
    }
    return 0;
}
int mergesort(int a[8], int t[8], int lo, int hi){
    int mid;
    if(lo >= hi){
        return 0;
    }
    mid = (lo + hi) / 2;
    mergesort(a, t, lo, mid);
    mergesort(a, t, mid+1, hi);
    merge(a, t, lo, mid, hi);
    return 0;
}
arr[0]=5; arr[1]=2; arr[2]=8; arr[3]=1;
arr[4]=9; arr[5]=3; arr[6]=7; arr[7]=4;
mergesort(arr, tmp, 0, 7);
int sum;
int i;
sum = 0;
for(i=0;i<4;i++){
    sum += arr[i];
}
outnum(sum);
