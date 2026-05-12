// 测试84: 成员函数带返回值
// 期望输出: A (65)
struct Box{
    int val;
    int get(){
        return val;
    }
};
Box b;
b.val = 65;
int r;
r = b.get();
out(r);
