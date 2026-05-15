// 测试188: 递归快排（Lomuto分区）
// 排序 [6,2,8,4,1,9,3,7,5,10] 后输出第5个元素(索引4)=5
// 期望输出: 5
int arr[10];
int partition(int a[10], int lo, int hi){
    int pivot;
    int i;
    int j;
    int tmp;
    pivot = a[hi];
    i = lo - 1;
    for(j=lo;j<hi;j++){
        if(a[j] <= pivot){
            i++;
            tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
        }
    }
    i++;
    tmp = a[i];
    a[i] = a[hi];
    a[hi] = tmp;
    return i;
}
int quicksort(int a[10], int lo, int hi){
    int p;
    if(lo < hi){
        p = partition(a, lo, hi);
        quicksort(a, lo, p-1);
        quicksort(a, p+1, hi);
    }
    return 0;
}
arr[0]=6; arr[1]=2; arr[2]=8; arr[3]=4; arr[4]=1;
arr[5]=9; arr[6]=3; arr[7]=7; arr[8]=5; arr[9]=10;
quicksort(arr, 0, 9);
outnum(arr[4]);
