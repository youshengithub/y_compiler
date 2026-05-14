// 测试103: 综合测试 - 队列数据结构
// 期望输出: AB (65,66)
struct Queue{
    int data[10];
    int head;
    int tail;
    void init(){
        head = 0;
        tail = 0;
    }
    void enqueue(int v){
        data[tail] = v;
        tail = tail + 1;
    }
    int dequeue(){
        int v;
        v = data[head];
        head = head + 1;
        return v;
    }
};
Queue q;
q.init();
q.enqueue(65);
q.enqueue(66);
q.enqueue(67);
int v;
v = q.dequeue();
out(v);
v = q.dequeue();
out(v);
