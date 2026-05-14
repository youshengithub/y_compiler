// 测试: #undef 取消宏定义
#define VAL 65
int a;
a = VAL;
out(a);

#undef VAL
#define VAL 66
int b;
b = VAL;
out(b);
