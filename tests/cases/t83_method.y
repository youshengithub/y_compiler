// 测试83: 结构体成员函数（方法）
// Counter 有 val 成员和 inc 方法
// 期望输出: B (66)
struct Counter{
    int val;
    void inc(){
        val = val + 1;
    }
};
Counter c;
c.val = 65;
c.inc();
out(c.val);
