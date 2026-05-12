// 测试97: 方法中调用另一个方法
// 期望输出: C (67)
struct Calc{
    int val;
    void set(int v){
        val = v;
    }
    void add(int n){
        val = val + n;
    }
    int getVal(){
        return val;
    }
};
Calc c;
c.set(65);
c.add(2);
int r;
r = c.getVal();
out(r);
