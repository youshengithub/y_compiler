// 测试85: 成员函数带参数（构造函数模式）
// 期望输出: AB (65,66)
struct Point{
    int x;
    int y;
    void init(int ax, int ay){
        x = ax;
        y = ay;
    }
};
Point p;
p.init(65, 66);
out(p.x);
out(p.y);
