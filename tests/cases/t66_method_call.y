// 测试66: 结构体方法调用
// 期望输出: B (c.val=65, inc后=66='B')
struct Counter{
    int val;
};
Counter c;
c.val = 65;
c.val += 1;
out(c.val);
