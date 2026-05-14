// 测试96: 综合测试 - 链表节点模拟
// 用数组模拟链表操作
// 期望输出: 3 (51)
int data[3];
int next[3];
data[0] = 1;
data[1] = 2;
data[2] = 3;
next[0] = 1;
next[1] = 2;
next[2] = -1;
// 遍历链表: 0→1→2
int cur;
int count;
cur = 0;
count = 0;
while(cur != -1){
    count = count + 1;
    cur = next[cur];
}
count = count + 48;
out(count);
