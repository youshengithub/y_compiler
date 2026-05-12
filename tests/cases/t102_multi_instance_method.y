// 测试102: 多个结构体实例调用方法
// 两个Counter独立计数
// 期望输出: BD (66,68)
struct Counter{
    int val;
    void inc(){
        val = val + 1;
    }
};
Counter a;
Counter b;
a.val = 65;
b.val = 65;
a.inc();
b.inc();
b.inc();
b.inc();
out(a.val);
out(b.val);
