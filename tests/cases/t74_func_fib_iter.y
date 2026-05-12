// 测试74: 迭代斐波那契 fib(10)=55
// 期望输出: 55
int fib(int n){
    int a;
    int b;
    int t;
    int i;
    a = 0;
    b = 1;
    for(i=0;i<n;i++){
        t = b;
        b = a + b;
        a = t;
    }
    return a;
}
int r;
r = fib(10);
outnum(r);
