// 测试174: 多函数互调 — 判断偶数个数
// isEven和isOdd互相递归调用（改用循环避免栈溢出）
// 统计[1..20]中偶数个数 = 10
// 期望输出: 10
int isEven(int n){
    if(n < 0){
        n = 0 - n;
    }
    while(n >= 2){
        n -= 2;
    }
    if(n == 0){
        return 1;
    }
    return 0;
}
int countEven(int arr[20], int size){
    int i;
    int count;
    count = 0;
    for(i=0;i<size;i++){
        if(isEven(arr[i]) == 1){
            count++;
        }
    }
    return count;
}
int nums[20];
int i;
for(i=0;i<20;i++){
    nums[i] = i + 1;
}
int result;
result = countEven(nums, 20);
outnum(result);
