// 测试76: 递归幂运算 pow(2,8)=256
// 期望输出: 256
int pow(int base, int exp){
    if(exp<=0){
        return 1;
    }
    return base * pow(base, exp-1);
}
int r;
r = pow(2, 8);
outnum(r);
