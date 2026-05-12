// 测试: 结构体定义和成员访问
// 期望输出: AB (65,66)
struct Point{
    int x;
    int y;
};
Point p;
p.x = 65;
p.y = 66;
out(p.x);
out(p.y);
