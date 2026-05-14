// 测试92: switch 无 fall-through
// 当前实现：不支持 C 风格的 fall-through
// 每个 case 必须有 break 或独立执行
// x=1 匹配 case 1, 执行 out(65), 无break → case 2 不匹配 → 执行 default
// 期望输出: AC (65,67)
int x;
x = 1;
switch(x){case 1:out(65);case 2:out(66);break;default:out(67);break;}
