// 测试167: 快速幂算法 — 计算 2^10 = 1024
// 期望输出: 1024
int power(int base, int exp){
    int result;
    result = 1;
    while(exp > 0){
        if(exp % 2 == 1){
            result *= base;
        }
        base *= base;
        exp /= 2;
    }
    return result;
}
int r;
r = power(2, 10);
outnum(r);
