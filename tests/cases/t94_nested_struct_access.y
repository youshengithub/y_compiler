// 测试94: 嵌套结构体方法
// 期望输出: A (65)
struct Inner{
    int x;
    int getX(){
        return x;
    }
};
struct Outer{
    Inner inner;
    int val;
};
Outer o;
o.inner.x = 65;
o.val = 1;
out(o.inner.x);
