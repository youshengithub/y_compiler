// 测试99: 方法内使用循环
// 期望输出: 5 (53)
struct Counter{
    int val;
    void countTo(int n){
        int i;
        val = 0;
        for(i=0;i<n;i++){
            val = val + 1;
        }
    }
};
Counter c;
c.countTo(5);
int r;
r = c.val + 48;
out(r);
