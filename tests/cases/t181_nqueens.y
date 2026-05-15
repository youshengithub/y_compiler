// 测试181: 回溯算法 — N皇后计数(4皇后=2种解)
// 4x4棋盘上放4个皇后使互不攻击
// 期望输出: 2
int cols[4];
int count;
int abs(int x){
    if(x < 0){
        return 0 - x;
    }
    return x;
}
int isSafe(int row, int col){
    int i;
    int diff;
    for(i=0;i<row;i++){
        if(cols[i] == col){
            return 0;
        }
        diff = abs(cols[i] - col);
        if(diff == row - i){
            return 0;
        }
    }
    return 1;
}
int solve(int row){
    int col;
    if(row == 4){
        count++;
        return 0;
    }
    for(col=0;col<4;col++){
        if(isSafe(row, col) == 1){
            cols[row] = col;
            solve(row + 1);
        }
    }
    return 0;
}
count = 0;
solve(0);
outnum(count);
