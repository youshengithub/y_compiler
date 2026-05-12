// 测试: break 语句
// 期望输出: 3 (3+48=51)
int i;
int r;
r = 0;
for(i = 0; i < 10; i = i + 1){
    if(i == 3){
        break;
    }
    r = r + 1;
}
r = r + 48;
out(r);
