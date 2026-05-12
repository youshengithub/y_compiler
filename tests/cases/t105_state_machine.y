// 测试105: 综合测试 - 简单状态机
// 状态0→状态1→状态2→输出
// 期望输出: A (65)
int state;
int output;
state = 0;
output = 0;
while(state != 3){
    switch(state){case 0:state=1;break;case 1:state=2;break;case 2:output=65;state=3;break;default:state=3;break;}
}
out(output);
