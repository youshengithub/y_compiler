// 测试186: 综合OOP — 学生成绩管理系统
// 3个学生各3门课成绩，求每人平均分、班级最高平均分
// 直接用函数+数组参数实现，避免结构体数组成员在全局的限制
// student 0: 85,90,78 → avg=84
// student 1: 92,88,95 → avg=91
// student 2: 76,82,89 → avg=82
// 最高平均分=91
// 期望输出: 91
int calcAvg(int scores[3]){
    int sum;
    int i;
    sum = 0;
    for(i=0;i<3;i++){
        sum += scores[i];
    }
    return sum / 3;
}
int s0[3];
int s1[3];
int s2[3];
s0[0]=85; s0[1]=90; s0[2]=78;
s1[0]=92; s1[1]=88; s1[2]=95;
s2[0]=76; s2[1]=82; s2[2]=89;
int avg0;
int avg1;
int avg2;
avg0 = calcAvg(s0);
avg1 = calcAvg(s1);
avg2 = calcAvg(s2);
int best;
best = avg0;
if(avg1 > best){
    best = avg1;
}
if(avg2 > best){
    best = avg2;
}
outnum(best);
