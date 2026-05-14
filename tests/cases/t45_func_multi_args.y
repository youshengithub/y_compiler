// 测试: 函数多参数
// add(20, 20, 25) = 65
// 期望输出: A (65)
int sum3(int a, int b, int c){
    int r;
    r = a + b;
    r = r + c;
    return r;
}
int r;
r = sum3(20, 20, 25);
out(r);
