// 测试182: 动态规划 — 0/1背包问题
// 物品: weights=[2,3,4,5], values=[3,4,5,6], 容量W=8
// 最优解: 选物品1+2+3或1+2(w=2+3=5,v=3+4=7) vs 选2+3(w=3+4=7,v=4+5=9)
// dp[i][w] = max(dp[i-1][w], dp[i-1][w-wi]+vi)
// 最优值=10 (选物品0+2+3: w=2+4=6<=8? no, w=2+3+5=10>8)
// 实际: 选0,1,2: w=2+3+4=9>8; 选0,1,3: w=2+3+5=10>8
// 选1,2: w=3+4=7<=8, v=4+5=9; 选1,3: w=3+5=8<=8, v=4+6=10 ✓
// 期望输出: 10
int weights[4];
int values[4];
weights[0]=2; weights[1]=3; weights[2]=4; weights[3]=5;
values[0]=3; values[1]=4; values[2]=5; values[3]=6;
int dp[9];
int i;
int w;
for(w=0;w<=8;w++){
    dp[w] = 0;
}
for(i=0;i<4;i++){
    w = 8;
    while(w >= weights[i]){
        int newVal;
        int prevIdx;
        prevIdx = w - weights[i];
        newVal = dp[prevIdx] + values[i];
        if(newVal > dp[w]){
            dp[w] = newVal;
        }
        w--;
    }
}
outnum(dp[8]);
