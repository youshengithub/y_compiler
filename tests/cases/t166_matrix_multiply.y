// 测试166: 矩阵乘法 - 2x2矩阵相乘
// A = [[1,2],[3,4]], B = [[5,6],[7,8]]
// C = A*B = [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
//         = [[19, 22], [43, 50]]
// 输出 C[0][0] + C[1][1] = 19 + 50 = 69
// 期望输出: 69
int a[4];
int b[4];
int c[4];
a[0]=1; a[1]=2; a[2]=3; a[3]=4;
b[0]=5; b[1]=6; b[2]=7; b[3]=8;
int i;
int j;
int k;
int sum;
int idx;
int ai;
int bj;
for(i=0;i<2;i++){
    for(j=0;j<2;j++){
        sum = 0;
        for(k=0;k<2;k++){
            ai = i*2+k;
            bj = k*2+j;
            sum += a[ai] * b[bj];
        }
        idx = i*2+j;
        c[idx] = sum;
    }
}
int result;
result = c[0] + c[3];
outnum(result);
