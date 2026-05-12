// ═══════════════════════════════════════════
//  Y Compiler Standard Library — array.y
//  数组工具函数库
// ═══════════════════════════════════════════

#ifndef __ARRAY_Y__
#define __ARRAY_Y__

// ── array_fill: 用指定值填充数组 ──
void array_fill(int arr[256], int n, int val){
    int i;
    for(i=0;i<n;i++){
        arr[i]=val;
    }
}

// ── array_sum: 计算数组元素总和 ──
int array_sum(int arr[256], int n){
    int s;
    s=0;
    int i;
    for(i=0;i<n;i++){
        s+=arr[i];
    }
    return s;
}

// ── array_max: 返回数组最大值 ──
int array_max(int arr[256], int n){
    int m;
    m=arr[0];
    int i;
    for(i=1;i<n;i++){
        if(arr[i]>m){
            m=arr[i];
        }
    }
    return m;
}

// ── array_min: 返回数组最小值 ──
int array_min(int arr[256], int n){
    int m;
    m=arr[0];
    int i;
    for(i=1;i<n;i++){
        if(arr[i]<m){
            m=arr[i];
        }
    }
    return m;
}

// ── array_reverse: 反转数组 ──
void array_reverse(int arr[256], int n){
    int i;
    int j;
    i=0;
    j=n-1;
    while(i<j){
        int tmp;
        tmp=arr[i];
        arr[i]=arr[j];
        arr[j]=tmp;
        i++;
        j--;
    }
}

// ── array_copy: 复制数组 src → dst ──
void array_copy(int dst[256], int src[256], int n){
    int i;
    for(i=0;i<n;i++){
        dst[i]=src[i];
    }
}

// ── bubble_sort: 冒泡排序 ──
void bubble_sort(int arr[256], int n){
    int i;
    int j;
    for(i=0;i<n;i++){
        int lim;
        lim=n-1;
        lim-=i;
        for(j=0;j<lim;j++){
            int j1;
            j1=j+1;
            if(arr[j]>arr[j1]){
                int tmp;
                tmp=arr[j];
                arr[j]=arr[j1];
                arr[j1]=tmp;
            }
        }
    }
}

// ── array_find: 线性查找，返回下标，找不到返回 -1 ──
int array_find(int arr[256], int n, int val){
    int i;
    for(i=0;i<n;i++){
        if(arr[i]==val){
            return i;
        }
    }
    return 0-1;
}

// ── array_count: 统计值出现次数 ──
int array_count(int arr[256], int n, int val){
    int cnt;
    cnt=0;
    int i;
    for(i=0;i<n;i++){
        if(arr[i]==val){
            cnt++;
        }
    }
    return cnt;
}

#endif
