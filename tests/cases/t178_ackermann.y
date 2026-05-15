// 测试178: 多重递归 — Ackermann函数简化版
// ack(0,n)=n+1, ack(m,0)=ack(m-1,1), ack(m,n)=ack(m-1,ack(m,n-1))
// ack(2,3) = 9 (完整Ackermann会爆栈, 用m<=2安全)
// ack(2,3) = ack(1,ack(2,2)) = ack(1,ack(1,ack(2,1)))
//          = ack(1,ack(1,ack(1,ack(2,0)))) = ack(1,ack(1,ack(1,ack(1,1))))
//          = ack(1,ack(1,ack(1,3))) = ack(1,ack(1,5)) = ack(1,7) = 9
// 期望输出: 9
int ack(int m, int n){
    if(m == 0){
        return n + 1;
    }
    if(n == 0){
        int r;
        r = ack(m-1, 1);
        return r;
    }
    int inner;
    inner = ack(m, n-1);
    int result;
    result = ack(m-1, inner);
    return result;
}
int r;
r = ack(2, 3);
outnum(r);
