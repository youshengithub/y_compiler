// 测试68: 嵌套结构体
// 期望输出: A
struct Inner{
    int val;
};
struct Outer{
    int x;
    Inner inner;
};
Outer o;
o.x = 65;
out(o.x);
