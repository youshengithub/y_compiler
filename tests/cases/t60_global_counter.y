// 测试60: 全局变量作为计数器
// 期望输出: 3
int g;
g = 0;
void inc(){
    g += 1;
}
inc();
inc();
inc();
g = g + 48;
out(g);
