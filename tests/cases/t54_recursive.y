// 测试54: 递归调用（阶乘）
// factorial(5)=120, 120%10=0 → '0'=48
// 期望输出: 0
int fact(int n){
    if(n<=1){
        return 1;
    }
    return n*fact(n-1);
}
int r;
r = fact(5);
int d;
d = r % 10;
d = d + 48;
out(d);
