// 测试82: switch/case default 分支
// x=5，没有匹配的case → 执行 default
// 期望输出: D (68)
int x;
x = 5;
switch(x){case 1:out(65);break;case 2:out(66);break;default:out(68);break;}
