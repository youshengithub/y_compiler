// 测试168: 选择排序 + 线性查找
// 对数组 [5,3,4,1,2] 排序后查找 3 的位置
// 排序后: [1,2,3,4,5], 3的下标是2
// 期望输出: 2
int data[5];
data[0]=5; data[1]=3; data[2]=4; data[3]=1; data[4]=2;
int i;
int j;
int minIdx;
int tmp;
int valJ;
int valMin;
for(i=0;i<4;i++){
    minIdx = i;
    j = i + 1;
    while(j < 5){
        valJ = data[j];
        valMin = data[minIdx];
        if(valJ < valMin){
            minIdx = j;
        }
        j++;
    }
    if(minIdx != i){
        tmp = data[i];
        data[i] = data[minIdx];
        data[minIdx] = tmp;
    }
}
// 线性查找 3
int target;
int found;
target = 3;
found = 0 - 1;
for(i=0;i<5;i++){
    if(data[i] == target){
        found = i;
        break;
    }
}
outnum(found);
