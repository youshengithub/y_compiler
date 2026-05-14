// 简单循环性能计数验证
int s;
s = 0;
int i;
for(i = 0; i < 10; i++) {
    s += 1;
}
// s=10
s += 48;
out(s);
