// 测试173: 递归组合数 C(8,3) = 56
// C(n,k) = C(n-1,k-1) + C(n-1,k), C(n,0)=1, C(n,n)=1
// 期望输出: 56
int comb(int n, int k){
    if(k == 0){
        return 1;
    }
    if(k == n){
        return 1;
    }
    int a;
    int b;
    a = comb(n-1, k-1);
    b = comb(n-1, k);
    return a + b;
}
int r;
r = comb(8, 3);
outnum(r);
