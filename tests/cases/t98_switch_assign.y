// 测试98: switch 中使用变量
// 期望输出: B (66)
int x;
int y;
x = 2;
y = 0;
switch(x){case 1:y=65;break;case 2:y=66;break;default:y=67;break;}
out(y);
