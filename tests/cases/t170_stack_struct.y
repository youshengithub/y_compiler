// 测试170: 栈数据结构（用数组+结构体模拟）
// push 10,20,30 → pop得30,20,10 → 求和=60
// 期望输出: 60
struct Stack{
    int data[10];
    int top;
    void init(){
        top = -1;
    }
    void push(int val){
        top++;
        data[top] = val;
    }
    int pop(){
        int val;
        val = data[top];
        top--;
        return val;
    }
    int isEmpty(){
        if(top == -1){
            return 1;
        }
        return 0;
    }
};
Stack s;
s.init();
s.push(10);
s.push(20);
s.push(30);
int sum;
int v;
sum = 0;
v = s.pop();
sum += v;
v = s.pop();
sum += v;
v = s.pop();
sum += v;
outnum(sum);
