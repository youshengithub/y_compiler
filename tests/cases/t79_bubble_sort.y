// 测试79: 冒泡排序
// 期望输出: 123
int a[3];
a[0]=3;
a[1]=1;
a[2]=2;
int i;
int j;
int t;
int k;
for(i=0;i<2;i++){
    for(j=0;j<2;j++){
        k = j + 1;
        if(a[j]>a[k]){
            t = a[j];
            a[j] = a[k];
            a[k] = t;
        }
    }
}
for(i=0;i<3;i++){
    int v;
    v = a[i] + 48;
    out(v);
}
