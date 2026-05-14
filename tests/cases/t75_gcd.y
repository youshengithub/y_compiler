// 测试75: GCD算法 gcd(48,36)=12
// 期望输出: 12
int gcd(int a, int b){
    while(b>0){
        int t;
        t = b;
        b = a % b;
        a = t;
    }
    return a;
}
int r;
r = gcd(48, 36);
outnum(r);
