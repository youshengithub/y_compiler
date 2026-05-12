// 测试91: 两个结构体实例各自独立
// 期望输出: AB (p1.x=65, p2.x=66)
struct Point{
    int x;
    int y;
};
Point p1;
Point p2;
p1.x = 65;
p2.x = 66;
out(p1.x);
out(p2.x);
