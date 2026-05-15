// 测试180: 多维状态机 — 简单正则匹配
// 匹配模式 "ab*c": a后跟0+个b再跟c
// 测试 "abbc" → 匹配成功(1), "adc" → 失败(0)
// 输出 1+0 = 1... 简化为匹配"abbc"→1
// 状态: 0=初始, 1=见到a, 2=在b*中, 3=见到c(接受)
// 期望输出: 1
int match(int str[10], int len){
    int state;
    int i;
    int ch;
    state = 0;
    for(i=0;i<len;i++){
        ch = str[i];
        switch(state){
            case 0:
                if(ch == 97){
                    state = 1;
                } else {
                    return 0;
                }
                break;
            case 1:
                if(ch == 98){
                    state = 2;
                } else {
                    if(ch == 99){
                        state = 3;
                    } else {
                        return 0;
                    }
                }
                break;
            case 2:
                if(ch == 98){
                    state = 2;
                } else {
                    if(ch == 99){
                        state = 3;
                    } else {
                        return 0;
                    }
                }
                break;
            default:
                return 0;
                break;
        }
    }
    if(state == 3){
        return 1;
    }
    return 0;
}
int input[4];
input[0] = 97;
input[1] = 98;
input[2] = 98;
input[3] = 99;
int r;
r = match(input, 4);
outnum(r);
