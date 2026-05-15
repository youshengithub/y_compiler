// 测试184: 综合指针 + 函数 + 三元运算符
// 实现min/max选择器，用指针修改值
// 期望输出: 3,9
int getMin(int a, int b){
    int r;
    r = (a < b) ? a : b;
    return r;
}
int getMax(int a, int b){
    int r;
    r = (a > b) ? a : b;
    return r;
}
void clamp(int *val, int lo, int hi){
    int v;
    v = *val;
    if(v < lo){
        *val = lo;
    }
    if(v > hi){
        *val = hi;
    }
}
int a;
int b;
a = 3;
b = 9;
int mn;
int mx;
mn = getMin(a, b);
mx = getMax(a, b);
outnum(mn);
out(44);
outnum(mx);
