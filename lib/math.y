// ═══════════════════════════════════════════
//  Y Compiler Standard Library — math.y
//  数学函数库
// ═══════════════════════════════════════════

#ifndef __MATH_Y__
#define __MATH_Y__

// ── abs: 绝对值 ──
int abs(int x){
    if(x<0){
        return 0-x;
    }
    return x;
}

// ── max: 两个整数取最大值 ──
int max(int a, int b){
    if(a>b){
        return a;
    }
    return b;
}

// ── min: 两个整数取最小值 ──
int min(int a, int b){
    if(a<b){
        return a;
    }
    return b;
}

// ── pow_int: 整数幂运算 a^n ──
int pow_int(int base, int exp){
    int result;
    result=1;
    int i;
    for(i=0;i<exp;i++){
        result=result*base;
    }
    return result;
}

// ── gcd: 最大公约数（欧几里得算法）──
int gcd(int a, int b){
    if(a<0){ a=0-a; }
    if(b<0){ b=0-b; }
    while(b!=0){
        int t;
        t=b;
        b=a%b;
        a=t;
    }
    return a;
}

// ── lcm: 最小公倍数 ──
int lcm(int a, int b){
    if(a==0){ return 0; }
    if(b==0){ return 0; }
    int g;
    g=gcd(a,b);
    return a/g*b;
}

// ── clamp: 将值限制在 [lo, hi] 范围内 ──
int clamp(int val, int lo, int hi){
    if(val<lo){ return lo; }
    if(val>hi){ return hi; }
    return val;
}

// ── sign: 符号函数，返回 -1 / 0 / 1 ──
int sign(int x){
    if(x>0){ return 1; }
    if(x<0){ return 0-1; }
    return 0;
}

// ── isqrt: 整数平方根（向下取整）──
int isqrt(int n){
    if(n<=0){ return 0; }
    int x;
    x=n;
    int y;
    y=(x+1)/2;
    while(y<x){
        x=y;
        y=(x+n/x)/2;
    }
    return x;
}

// ── factorial: 阶乘 ──
int factorial(int n){
    if(n<=1){ return 1; }
    return n*factorial(n-1);
}

#endif
