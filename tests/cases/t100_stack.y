// 测试100: 综合测试 - 栈数据结构
// 期望输出: CBA (67,66,65)
struct Stack{
    int data[10];
    int top;
    void init(){
        top = 0;
    }
    void push(int v){
        data[top] = v;
        top = top + 1;
    }
    int pop(){
        top = top - 1;
        return data[top];
    }
};
Stack s;
s.init();
s.push(65);
s.push(66);
s.push(67);
int v;
v = s.pop();
out(v);
v = s.pop();
out(v);
v = s.pop();
out(v);
