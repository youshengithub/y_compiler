// 测试: continue 语句（跳过偶数，只累加奇数）
// i=0,1,2,3,4: 跳过0,2,4，累加1,3 → sum=2
// 期望输出: 2 (2+48=50='2')
int i;
int sum;
int mod;
sum = 0;
for(i = 0; i < 5; i = i + 1){
    mod = i % 2;
    if(mod == 0){
        continue;
    }
    sum = sum + 1;
}
sum = sum + 48;
out(sum);
