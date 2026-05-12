// 测试20: 内联汇编 asm
// 期望输出: A
int a;
a=0;
asm("MOV $0 65\n");
out(a);
