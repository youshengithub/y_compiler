// 测试172: 素数筛法（埃拉托斯特尼筛）
// 统计1-50范围内的素数个数 = 15
// (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)
// 期望输出: 15
int sieve[51];
int i;
int j;
int count;
for(i=0;i<51;i++){
    sieve[i] = 1;
}
sieve[0] = 0;
sieve[1] = 0;
for(i=2;i<8;i++){
    if(sieve[i] == 1){
        j = i * i;
        while(j <= 50){
            sieve[j] = 0;
            j += i;
        }
    }
}
count = 0;
for(i=2;i<=50;i++){
    if(sieve[i] == 1){
        count++;
    }
}
outnum(count);
