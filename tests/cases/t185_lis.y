// 测试185: 最长递增子序列长度（LIS）— O(n²) DP
// arr = [10,9,2,5,3,7,101,18]
// LIS = [2,3,7,101] 或 [2,3,7,18] → 长度4
// 期望输出: 4
int arr[8];
arr[0]=10; arr[1]=9; arr[2]=2; arr[3]=5;
arr[4]=3; arr[5]=7; arr[6]=101; arr[7]=18;
int dp[8];
int i;
int j;
int maxLen;
for(i=0;i<8;i++){
    dp[i] = 1;
}
for(i=1;i<8;i++){
    for(j=0;j<i;j++){
        if(arr[j] < arr[i]){
            if(dp[j] + 1 > dp[i]){
                dp[i] = dp[j] + 1;
            }
        }
    }
}
maxLen = 0;
for(i=0;i<8;i++){
    if(dp[i] > maxLen){
        maxLen = dp[i];
    }
}
outnum(maxLen);
