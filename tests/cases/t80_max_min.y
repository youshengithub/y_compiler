// 测试80: 函数求最大值
// 期望输出: 9
int max(int a, int b){
    if(a>b){
        return a;
    }
    return b;
}
int r;
r = max(3, 9);
outnum(r);
