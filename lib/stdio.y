// ═══════════════════════════════════════════
//  Y Compiler Standard Library — stdio.y
//  输入输出函数库
// ═══════════════════════════════════════════

#ifndef __STDIO_Y__
#define __STDIO_Y__

// ── print_int: 输出一个整数（十进制）──
// 支持正数、负数和零
void print_int(int n){
    if(n==0){
        out(48);
        return;
    }
    if(n<0){
        out(45);
        n=0-n;
    }
    int buf[20];
    int len;
    len=0;
    while(n>0){
        int d;
        d=n%10;
        buf[len]=d+48;
        len++;
        n=n/10;
    }
    int i;
    i=len-1;
    while(i>=0){
        out(buf[i]);
        i--;
    }
}

// ── println_int: 输出一个整数并换行 ──
void println_int(int n){
    print_int(n);
    out(10);
}

// ── print_char: 输出一个字符 ──
void print_char(int ch){
    out(ch);
}

// ── println: 输出换行 ──
void println(){
    out(10);
}

// ── print_str: 输出字符串数组（以0结尾）──
void print_str(int s[256], int len){
    int i;
    for(i=0;i<len;i++){
        if(s[i]==0){
            return;
        }
        out(s[i]);
    }
}

// ── print_bool: 输出布尔值（true/false）──
void print_bool(int b){
    if(b!=0){
        // "true"
        out(116); out(114); out(117); out(101);
    }else{
        // "false"
        out(102); out(97); out(108); out(115); out(101);
    }
}

// ── read_int: 从键盘读取一个整数（以回车结束）──
// 注意：需要虚拟机支持 in() 指令
int read_int(){
    int result;
    result=0;
    int neg;
    neg=0;
    int ch;
    ch=in();
    if(ch==45){
        neg=1;
        ch=in();
    }
    while(ch>=48){
        if(ch>57){
            // 非数字就停
            if(neg==1){
                return 0-result;
            }
            return result;
        }
        result=result*10+(ch-48);
        ch=in();
    }
    if(neg==1){
        return 0-result;
    }
    return result;
}

#endif
