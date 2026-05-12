// 测试120: 全局数组作为函数参数
// 全局数组传递给函数
// 期望输出: C
int get_elem(int a[5], int i){
    return a[i];
}
int g[5];
g[0] = 65;
g[1] = 66;
g[2] = 67;
g[3] = 68;
g[4] = 69;
int r;
r = get_elem(g, 2);
out(r);
