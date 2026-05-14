// 测试: 函数式宏 #define MAX(a,b)
#define MAX(a,b) ((a)>(b)?(a):(b))
// 由于不支持三元运算符，改用函数式宏展开为 if
// 换一种思路：用简单宏测试函数式宏的参数替换
#define ADD_OFFSET(x,y) x+y

int a;
a = ADD_OFFSET(60, 5);
out(a);
