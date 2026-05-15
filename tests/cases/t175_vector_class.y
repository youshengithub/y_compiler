// 测试175: 综合OOP - 向量运算类
// Vector2D: 加法、点积、长度平方
// v1=(3,4), v2=(1,2)
// v1+v2=(4,6), dot=3*1+4*2=11, lenSq(v1)=9+16=25
// 输出 dot + lenSq = 11 + 25 = 36
// 期望输出: 36
struct Vector2D{
    int x;
    int y;
    void init(int ax, int ay){
        x = ax;
        y = ay;
    }
    int dot(int ox, int oy){
        int r;
        r = x*ox + y*oy;
        return r;
    }
    int lengthSq(){
        int r;
        r = x*x + y*y;
        return r;
    }
    void addVec(int ox, int oy){
        x += ox;
        y += oy;
    }
};
Vector2D v1;
Vector2D v2;
v1.init(3, 4);
v2.init(1, 2);
int dotResult;
dotResult = v1.dot(v2.x, v2.y);
int lenSq;
lenSq = v1.lengthSq();
int total;
total = dotResult + lenSq;
outnum(total);
