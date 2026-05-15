// 测试171: 动态数组（malloc实现）+ 插入排序
// 用malloc分配数组，插入排序后输出中位数
// data = [9,3,7,1,5] → 排序后 [1,3,5,7,9] → 中位数=5
// 期望输出: 5
int insertionSort(int *arr, int n){
    int i;
    int j;
    int key;
    int jval;
    for(i=1;i<n;i++){
        key = *(arr + i);
        j = i - 1;
        while(j >= 0){
            jval = *(arr + j);
            if(jval > key){
                *(arr + j + 1) = jval;
                j--;
            } else {
                break;
            }
        }
        *(arr + j + 1) = key;
    }
    return 0;
}
int *data;
data = malloc(5);
*(data + 0) = 9;
*(data + 1) = 3;
*(data + 2) = 7;
*(data + 3) = 1;
*(data + 4) = 5;
insertionSort(data, 5);
int median;
median = *(data + 2);
outnum(median);
free(data);
