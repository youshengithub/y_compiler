// 测试63: 表达式作为函数参数
// 期望输出: A (double_val(30+2)=64, +1=65)
int double_val(int x){
    return x*2;
}
int r;
r = double_val(32);
r = r + 1;
out(r);
