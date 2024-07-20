#说明

本项目是一个基于python的类C/C++语法编译器，其中C++语法还在支持中。
The aim for this project is develop a compiler for C/C++. 
#Step
git checkout master
python Compile.py
然后运行code.txt的代码，其会不断的计算素数, Then code.txt will be run, This is a prime calculator.
#文件结构
/lib
  lib.txt 库代码 , Library code
code.txt 源代码 ,Source code
Compile.txt 编译程序, Compiler
Config.txt 语法配置文件 ,  Config for grammar.
Cyvm.cpp 基于C++的解释器 , A virtual runner by C++
IR.txt 中间代码 , IR code
Postprocesser.py 后处理操作
Preprocesser.py 预处理操作
runer.py 基于python解释器, A virtual runner by python
archive.zip pou.txt pou2.txt 不重要的文件，unimportant file
