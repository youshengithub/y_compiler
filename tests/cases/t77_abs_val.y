// 测试77: 多条件判断
// 期望输出: 42
int my_abs(int x){
    if(x<0){
        return 0-x;
    }
    return x;
}
int r;
r = my_abs(-42);
outnum(r);
