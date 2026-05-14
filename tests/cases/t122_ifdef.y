// 测试: 条件编译 #ifdef / #ifndef / #endif
#define DEBUG

#ifdef DEBUG
int a;
a = 65;
out(a);
#endif

#ifndef RELEASE
int b;
b = 66;
out(b);
#endif

#ifdef RELEASE
int c;
c = 67;
out(c);
#endif
