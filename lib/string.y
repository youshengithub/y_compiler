// ═══════════════════════════════════════════
//  Y Compiler Standard Library — string.y
//  字符串操作库
//  注意：字符串使用 int 数组存储，以 0 结尾
// ═══════════════════════════════════════════

#ifndef __STRING_Y__
#define __STRING_Y__

// ── strlen: 返回字符串长度（不含结尾 0）──
int strlen(int s[256], int max_len){
    int i;
    i=0;
    while(i<max_len){
        if(s[i]==0){
            return i;
        }
        i++;
    }
    return i;
}

// ── strcmp: 比较两个字符串 ──
// 返回 0 表示相等，正数表示 a>b，负数表示 a<b
int strcmp(int a[256], int b[256], int max_len){
    int i;
    for(i=0;i<max_len;i++){
        if(a[i]==0){
            if(b[i]==0){ return 0; }
            return 0-1;
        }
        if(b[i]==0){ return 1; }
        if(a[i]<b[i]){ return 0-1; }
        if(a[i]>b[i]){ return 1; }
    }
    return 0;
}

// ── strcpy: 复制字符串 b 到 a ──
void strcpy(int a[256], int b[256], int max_len){
    int i;
    for(i=0;i<max_len;i++){
        a[i]=b[i];
        if(b[i]==0){
            return;
        }
    }
}

// ── strcat: 将字符串 b 追加到 a 后面 ──
void strcat(int a[256], int b[256], int a_max, int b_max){
    int a_len;
    a_len=strlen(a, a_max);
    int i;
    for(i=0;i<b_max;i++){
        if(b[i]==0){
            a[a_len+i]=0;
            return;
        }
        a[a_len+i]=b[i];
    }
    a[a_len+i]=0;
}

// ── char_at: 返回字符串第 idx 个字符 ──
int char_at(int s[256], int idx){
    return s[idx];
}

// ── to_upper: 小写转大写 ──
int to_upper(int ch){
    if(ch>=97){
        if(ch<=122){
            return ch-32;
        }
    }
    return ch;
}

// ── to_lower: 大写转小写 ──
int to_lower(int ch){
    if(ch>=65){
        if(ch<=90){
            return ch+32;
        }
    }
    return ch;
}

// ── is_alpha: 判断是否为字母 ──
int is_alpha(int ch){
    if(ch>=65){
        if(ch<=90){ return 1; }
    }
    if(ch>=97){
        if(ch<=122){ return 1; }
    }
    return 0;
}

// ── is_digit: 判断是否为数字字符 ──
int is_digit(int ch){
    if(ch>=48){
        if(ch<=57){ return 1; }
    }
    return 0;
}

// ── is_space: 判断是否为空白字符 ──
int is_space(int ch){
    if(ch==32){ return 1; }
    if(ch==9){ return 1; }
    if(ch==10){ return 1; }
    if(ch==13){ return 1; }
    return 0;
}

// ── int_to_str: 整数转字符串，存入 buf 数组 ──
// 返回字符串长度
int int_to_str(int n, int buf[20]){
    if(n==0){
        buf[0]=48;
        buf[1]=0;
        return 1;
    }
    int neg;
    neg=0;
    if(n<0){
        neg=1;
        n=0-n;
    }
    int tmp[20];
    int len;
    len=0;
    while(n>0){
        tmp[len]=n%10+48;
        len++;
        n=n/10;
    }
    int pos;
    pos=0;
    if(neg==1){
        buf[0]=45;
        pos=1;
    }
    int i;
    i=len-1;
    while(i>=0){
        buf[pos]=tmp[i];
        pos++;
        i--;
    }
    buf[pos]=0;
    return pos;
}

#endif
