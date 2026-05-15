// 测试169: 递归汉诺塔 — 计算移动次数
// hanoi(n) 需要 2^n - 1 次移动
// hanoi(6) = 63
// 期望输出: 63
int hanoi(int n){
    if(n == 1){
        return 1;
    }
    int left;
    int right;
    left = hanoi(n - 1);
    right = hanoi(n - 1);
    return left + right + 1;
}
int r;
r = hanoi(6);
outnum(r);
