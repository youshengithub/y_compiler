// 测试67: 数组作为全局变量被函数修改
// 期望输出: B
int arr[3];
arr[0] = 65;
void modify(){
    arr[0] += 1;
}
modify();
out(arr[0]);
