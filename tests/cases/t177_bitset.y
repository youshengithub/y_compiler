// 测试177: 位运算实现集合操作
// 用int的每一位表示集合中是否包含元素0-15
// A = {1,3,5,7} = 0b10101010 = 170
// B = {2,3,6,7} = 0b11001100 = 204
// A∩B = A&B = {3,7} → 位数=2
// A∪B = A|B = {1,2,3,5,6,7} → 位数=6
// 输出: 交集大小+并集大小 = 2+6 = 8
// 期望输出: 8
int popcount(int x){
    int count;
    count = 0;
    while(x > 0){
        if(x % 2 == 1){
            count++;
        }
        x /= 2;
    }
    return count;
}
int setA;
int setB;
setA = 170;
setB = 204;
int intersect;
int unionAB;
intersect = setA & setB;
unionAB = setA | setB;
int countI;
int countU;
countI = popcount(intersect);
countU = popcount(unionAB);
int result;
result = countI + countU;
outnum(result);
