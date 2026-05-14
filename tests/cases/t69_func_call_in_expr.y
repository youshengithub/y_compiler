// 测试69: 函数调用作为表达式的一部分
// 期望输出: A (get_val()+5 = 60+5=65)
int get_val(){
    return 60;
}
int r;
r = get_val() + 5;
out(r);
