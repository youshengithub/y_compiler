// 测试: 条件编译 #ifdef #else #endif
#define MODE 1

#ifdef MODE
int a;
a = 65;
out(a);
#else
int a;
a = 66;
out(a);
#endif
