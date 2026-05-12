// 测试104: switch 结合函数调用
// 期望输出: C (67)
int classify(int n){
    int r;
    r = 0;
    switch(n){case 1:r=65;break;case 2:r=66;break;case 3:r=67;break;default:r=68;break;}
    return r;
}
int v;
v = classify(3);
out(v);
