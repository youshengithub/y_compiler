// 测试187: 图的BFS遍历（邻接矩阵）
// 5个节点的无向图: 0-1, 0-2, 1-3, 2-3, 3-4
// 从节点0开始BFS，统计可达节点数=5
// 用数组模拟队列
// 期望输出: 5
int adj[25];
int visited[5];
int queue[5];
int front;
int rear;
int i;
int j;
int idx;
for(i=0;i<25;i++){
    adj[i] = 0;
}
for(i=0;i<5;i++){
    visited[i] = 0;
}
int setEdge(int adj[25], int u, int v){
    int idx1;
    int idx2;
    idx1 = u*5+v;
    idx2 = v*5+u;
    adj[idx1] = 1;
    adj[idx2] = 1;
    return 0;
}
setEdge(adj, 0, 1);
setEdge(adj, 0, 2);
setEdge(adj, 1, 3);
setEdge(adj, 2, 3);
setEdge(adj, 3, 4);
front = 0;
rear = 0;
queue[rear] = 0;
rear++;
visited[0] = 1;
int count;
int cur;
int neighbor;
int edgeIdx;
count = 0;
while(front < rear){
    cur = queue[front];
    front++;
    count++;
    for(neighbor=0;neighbor<5;neighbor++){
        edgeIdx = cur*5+neighbor;
        if(adj[edgeIdx] == 1){
            if(visited[neighbor] == 0){
                visited[neighbor] = 1;
                queue[rear] = neighbor;
                rear++;
            }
        }
    }
}
outnum(count);
