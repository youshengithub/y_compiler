// memory.y — 动态内存管理库
// 提供 malloc/free 的封装函数

// malloc 和 free 是编译器内置函数，直接使用即可
// 此文件提供辅助函数

int calloc(int count, int size){
    int total;
    total = count * size;
    int *p;
    p = malloc(total);
    // 清零
    int i;
    for(i = 0; i < total; i++){
        *(p + i) = 0;
    }
    return p;
}

int realloc_copy(int *old_ptr, int old_size, int new_size){
    int *new_ptr;
    new_ptr = malloc(new_size);
    int i;
    int copy_size;
    if(old_size < new_size){
        copy_size = old_size;
    } else {
        copy_size = new_size;
    }
    for(i = 0; i < copy_size; i++){
        *(new_ptr + i) = *(old_ptr + i);
    }
    free(old_ptr);
    return new_ptr;
}
