// 测试111: 嵌套函数调用
// 期望输出: A
int inc(int x){
    return x + 1;
}
int r;
r = inc(inc(63));
out(r);
