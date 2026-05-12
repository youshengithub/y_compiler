// 测试70: 互相不依赖的多函数
// 期望输出: C (add(30,35)=65, inc(65)=66, inc(66)=67)
int add(int a, int b){
    return a+b;
}
int inc(int x){
    return x+1;
}
int r;
r = add(30, 35);
r = inc(r);
r = inc(r);
out(r);
