// 测试176: 动态链表（用malloc模拟节点）
// 每个节点: [data, next_ptr]，占2个单元
// 创建 10->20->30->NULL，遍历求和=60
// 期望输出: 60
int *n1;
int *n2;
int *n3;
n1 = malloc(2);
n2 = malloc(2);
n3 = malloc(2);
*(n1 + 0) = 10;
*(n1 + 1) = n2;
*(n2 + 0) = 20;
*(n2 + 1) = n3;
*(n3 + 0) = 30;
*(n3 + 1) = 0;
int sum;
int curAddr;
int nextAddr;
int data;
sum = 0;
curAddr = n1;
while(curAddr != 0){
    int *cur;
    cur = curAddr;
    data = *(cur + 0);
    sum += data;
    nextAddr = *(cur + 1);
    curAddr = nextAddr;
}
outnum(sum);
free(n1);
free(n2);
free(n3);
