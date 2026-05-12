// 测试90: 成员函数多次调用
// Counter c 初始为 65, inc 3次 → 68 = 'D'
// 期望输出: D (68)
struct Counter{
    int val;
    void inc(){
        val = val + 1;
    }
    int get(){
        return val;
    }
};
Counter c;
c.val = 65;
c.inc();
c.inc();
c.inc();
int r;
r = c.get();
out(r);
