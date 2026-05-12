// 测试64: 多return路径
// 期望输出: B (abs(-66)=66)
int my_abs(int x){
    if(x<0){
        return 0-x;
    }
    return x;
}
int r;
r = my_abs(-66);
out(r);
