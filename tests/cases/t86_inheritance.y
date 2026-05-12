// 测试86: 组合继承
// Dog 包含 Animal 作为成员
// 期望输出: 4 (52)
struct Animal{
    int legs;
};
struct Dog{
    Animal base;
    int tail;
};
Dog d;
d.base.legs = 4;
d.tail = 1;
int r;
r = d.base.legs + 48;
out(r);
