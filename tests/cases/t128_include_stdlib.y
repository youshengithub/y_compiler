// 测试: #include <stdlib.y> 全部导入
#include <stdlib.y>

// 使用 math 库的 clamp
int a;
a = clamp(100, 60, 70);
// clamp(100, 60, 70) = 70 → 'F'
out(a);
