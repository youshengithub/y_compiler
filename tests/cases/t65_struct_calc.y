// 测试65: 结构体字段运算
// 期望输出: A (30+35=65)
struct Point{
    int x;
    int y;
};
Point p;
p.x = 30;
p.y = 35;
int r;
r = p.x + p.y;
out(r);
