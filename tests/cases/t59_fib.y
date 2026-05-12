// 测试59: 斐波那契递归 fib(7)=13, 13%10=3, 3+48=51='3'
// 期望输出: 3
int fib(int n){
    if(n<=1){
        return n;
    }
    return fib(n-1)+fib(n-2);
}
int r;
r = fib(7);
int d;
d = r % 10;
d = d + 48;
out(d);
