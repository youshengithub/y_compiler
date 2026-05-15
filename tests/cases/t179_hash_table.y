// 测试179: 哈希表模拟（开放寻址法）
// 用数组模拟简单哈希表，插入并查找
// 哈希函数: key % 7
// 插入 keys: 10,17,24,31 (都映射到slot 3, 需要探测)
// 查找 24 → 返回24证明找到
// 期望输出: 24
int hashTable[7];
int hashUsed[7];
int i;
for(i=0;i<7;i++){
    hashTable[i] = 0;
    hashUsed[i] = 0;
}
int hashInsert(int table[7], int used[7], int key){
    int slot;
    slot = key % 7;
    while(used[slot] == 1){
        slot++;
        if(slot >= 7){
            slot = 0;
        }
    }
    table[slot] = key;
    used[slot] = 1;
    return slot;
}
int hashFind(int table[7], int used[7], int key){
    int slot;
    int start;
    int notFound;
    notFound = 0 - 1;
    slot = key % 7;
    start = slot;
    while(used[slot] == 1){
        if(table[slot] == key){
            return table[slot];
        }
        slot++;
        if(slot >= 7){
            slot = 0;
        }
        if(slot == start){
            return notFound;
        }
    }
    return notFound;
}
hashInsert(hashTable, hashUsed, 10);
hashInsert(hashTable, hashUsed, 17);
hashInsert(hashTable, hashUsed, 24);
hashInsert(hashTable, hashUsed, 31);
int found;
found = hashFind(hashTable, hashUsed, 24);
outnum(found);
