// 测试93: 方法修改成员 + 外部读取
// 期望输出: A (65)
struct Acc{
    int sum;
    void add(int n){
        sum = sum + n;
    }
};
Acc a;
a.sum = 0;
a.add(30);
a.add(35);
out(a.sum);
