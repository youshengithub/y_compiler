// 测试101: 方法内使用 if/else
// 期望输出: Y (89)
struct Checker{
    int val;
    int isPositive(){
        if(val > 0){
            return 1;
        }else{
            return 0;
        }
    }
};
Checker c;
c.val = 5;
int r;
r = c.isPositive();
if(r == 1){
    out(89);
}else{
    out(78);
}
