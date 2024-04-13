#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <fstream>
#include <cassert>
#include <cctype>
#include <cstring>
#include <map>
enum opcode{ALLOC,MOV,TO,ADD,SUB,MUL,DIV,AND,OR,XOR,MOD,NOT,LEA,SEA,PUSH,POP,GREATER,EQUAL,LESS,RF,JPIF,JPNIF,JMP,OUT,IN};
std::map<std::string,opcode> string2int{
{"ALLOC",opcode::ALLOC},
{"MOV",opcode::MOV},
{"TO",opcode::TO},
{"ADD",opcode::ADD},
{"SUB",opcode::SUB},
{"MUL",opcode::MUL},
{"DIV",opcode::DIV},
{"AND",opcode::AND},
{"OR",opcode::OR},
{"XOR",opcode::XOR},
{"MOD",opcode::MOD},
{"NOT",opcode::NOT},
{"LEA",opcode::LEA},
{"SEA",opcode::SEA},
{"PUSH",opcode::PUSH},
{"POP",opcode::POP},
{"GREATER",opcode::GREATER},
{"EQUAL",opcode::EQUAL},
{"LESS",opcode::LESS},
{"RF",opcode::RF},
{"JPIF",opcode::JPIF},
{"JPNIF",opcode::JPNIF},
{"JMP",opcode::JMP},
{"OUT",opcode::OUT},
{"IN",opcode::IN}
};
enum reg_id{EAX=-1,EBX=-2,EBP=-3,ESP=-4,EIP=-5,EFG=-6,ETP=-7};
opcode turns2i(std::string&str){
    return string2int.find(str)->second;
}
enum type_op{POS,REAL};
//           EBP+M[a+M[b]] EBP+M[a]+b M[a+M[b]]      M[a]+b        a
enum num_type{BASE_INDIRCT,BASE_DIRCT,NOBASE_INDIRCT,NOBASE_DIRCT,DIRECT};
class Runner {
private:
    double* memory;
    std::unordered_map<std::string, int> REGS;
    const int max_memory = 100000;

public:
    Runner() {
        // 初始化寄存器
        REGS = {
            {"EAX", -1}, {"EBX", -2}, {"EBP", -3}, {"ESP", -4},
            {"EIP", -5}, {"EFG", -6}, {"ETP", -7}
        };
        // 初始化内存
        int regs_num=REGS.size();
        memory=new double[max_memory+regs_num];
        memory=memory+regs_num;
        //memory.resize(max_memory + REGS.size(), 0);
    }
    ~Runner() {
        memory-=REGS.size();
        delete memory;
    }
    // 计算位置函数
     std::pair<type_op, int> calc_pos(const std::string &text,std::vector<int>&opnum) {
        if (text.find("$") != std::string::npos) {
            int ans = 0;
            size_t colon_pos = text.find(":");
            ans = std::stoi(text.substr(1, colon_pos - 1));
            if (colon_pos != std::string::npos) {
                std::string second_part = text.substr(colon_pos + 1);
                if (second_part[0] == '$') {
                    opnum.push_back(num_type::BASE_INDIRCT);
                    opnum.push_back(ans);
                    opnum.push_back(std::stoi(second_part.substr(1)));
                    ans += memory[std::stoi(second_part.substr(1))];
                } else {
                    opnum.push_back(num_type::BASE_DIRCT);
                    opnum.push_back(ans);
                    opnum.push_back(std::stoi(second_part));
                    ans += std::stoi(second_part);
                }
                return {type_op::POS, ans + memory[reg_id::EBP]};
            } else { //只找到了一段
                if (ans < 0) {
                    opnum.push_back(num_type::NOBASE_DIRCT);
                    opnum.push_back(ans);
                    opnum.push_back(0);
                    return {type_op::POS, ans};
                }
                assert(1==0);
            }
        } else {
            opnum.push_back(num_type::DIRECT);
            opnum.push_back(std::stoi(text));
            return {type_op::REAL, std::stoi(text)};
        }
    }

    // 处理一行代码
    void process_line(std::string &line) {
        for (auto &kv : REGS) {
            size_t pos = line.find(kv.first);
            while (pos != std::string::npos) {
                line.replace(pos, kv.first.length(), "$" + std::to_string(kv.second));
                pos = line.find(kv.first, pos + 1);
            }
        }
    }
    inline void from_info_get_flag(std::vector<int>&info_num,int &op1,type_op&flag1){
                flag1=POS;
                switch (info_num[0]){
                    case num_type::DIRECT:
                        flag1=REAL;
                        op1=info_num[1];
                        break;
                    case num_type::BASE_DIRCT:
                        op1=info_num[1]+info_num[2]+memory[EBP];
                        break;
                    case num_type::BASE_INDIRCT:
                        op1=info_num[1]+memory[info_num[2]+int(memory[EBP])];
                        break;
                    case num_type::NOBASE_DIRCT:
                        op1=info_num[1]+info_num[2];
                        break;
                    case num_type::NOBASE_INDIRCT:
                        op1=info_num[1]+memory[info_num[2]];
                        break;
                }   
    }
    // 运行代码
    void RUN(const std::vector<std::string> &lines) {
        std::vector<std::vector<std::string>> keywordss;
        std::vector<opcode> opcodelist;
        std::vector<std::vector<std::vector<int>> > opnum_list;//先传进来

        for (const auto &line : lines) {
            //std::cout<<line<<" -------> ";
            std::string processed_line = line;
            process_line(processed_line);
            // 分割处理后的行为单词
            std::vector<std::string> keywords;
            size_t pos = 0, prev = 0;
            while ((pos = processed_line.find(" ", prev)) != std::string::npos) {
                keywords.push_back(processed_line.substr(prev, pos - prev));
                prev = pos + 1;
            }
            keywords.push_back(processed_line.substr(prev));
            keywordss.push_back(keywords);
            opcodelist.push_back(turns2i(keywords[0]));
        }
        auto start_time = std::chrono::high_resolution_clock::now();
        long long int instructs_times=0;
        for(auto &i:keywordss){
            std::vector<std::vector<int>>tpans;
            if(i.size()>=2){
            std::vector<int>temp;
            auto ans=calc_pos(i[1],temp);
            tpans.push_back(temp);
            }
            if(i.size()>=3){
            std::vector<int>temp;
            auto ans=calc_pos(i[2],temp);
            tpans.push_back(temp);
            }
            opnum_list.push_back(tpans);
        }
        while (true) {
            instructs_times++;
            //std::cout<<memory[reg_id::EIP]<<std::endl;
            int ip = memory[reg_id::EIP];
            if (ip >= lines.size()) {
                break;
            }
            const auto &keywords = keywordss[ip];
            type_op flag1=POS;
            type_op flag2=POS;
            int op1 = 0, op2 = 0;
            auto V_num=opnum_list[ip];
            if(V_num.size()>=1) from_info_get_flag(V_num[0],op1,flag1);
            if(V_num.size()>=2) from_info_get_flag(V_num[1],op2,flag2);

            // 主指令处理逻辑
            auto n_opcode=opcodelist[ip];
            switch(n_opcode){
                case ALLOC: {
                    if(op1>=max_memory){
                        std::cout<<"Exceed the max memory limts"<<std::endl;
                        exit(0);
                    }
                    memory[reg_id::ESP]=op1+1;
                    // ...
                    }break; 
                case MOV:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] = memory[op2];
                    } else {
                        memory[op1] = op2;
                    }
                    break; 
                case ADD:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] += memory[op2];
                    } else {
                        memory[op1] += op2;
                    }
                    break;
                case SUB:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] -= memory[op2];
                    } else {
                        memory[op1] -= op2;
                    }
                    break;
                case MUL:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] *= memory[op2];
                    } else {
                        memory[op1] *= op2;
                    }
                    break;                

                case  DIV:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] /= memory[op2];
                    } else {
                        memory[op1] /= op2;
                    }
                    break;                

                case  AND:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] =int(memory[op1])& int(memory[op2]);
                    } else {
                        memory[op1] = int(memory[op1]) &int(op2);
                    }
                    break;                

                case  OR:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] =int(memory[op1])| int (memory[op2]);
                    } else {
                        memory[op1] = int(memory[op1]) |int(op2);
                    }
                 break;               

                case  XOR:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] =int(memory[op1]) ^ int(memory[op2]);
                    } else {
                        memory[op1] = int(memory[op1]) ^int(op2);
                    }
                    break;                

                case  MOD:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] =int(memory[op1]) % int(memory[op2]);
                    } else {
                        memory[op1] = int(memory[op1])%int(op2);
                    }
                    break;                

                case  NOT:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[op1] = ~int(memory[op2]);
                    } else {
                        memory[op1] = ~int(op2);
                    }
                    break;                

                case  LEA:
                    assert(flag1 == type_op::POS);
                    assert(flag2 == type_op::POS);
                    memory[op1] = memory[op2];
                    break;        
                

                case SEA:
                    assert(flag1 == type_op::POS);
                    if (flag2 == type_op::POS) {
                        memory[int(memory[op1])] = int(memory[op2]);
                    } else {
                        memory[int(memory[op1])] = int(op2);
                    }
                    break;                

                case PUSH:
                    if (flag1 == type_op::POS) {
                        memory[reg_id::ESP] = int(memory[op1]);
                    } else {
                        memory[reg_id::ESP] = int(op1);
                    }
                    memory[reg_id::ESP]+=1;
                    break;                

                case POP:
                    assert(flag1 == type_op::POS);
                    memory[reg_id::ESP]-=1;
                    memory[op1] = memory[reg_id::ESP];
                    break;                
                

                case GREATER:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = memory[op1]>memory[op2];
                        } else {
                            memory[reg_id::EFG] = memory[op1]>op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = op1>memory[op2];
                        } else {
                            memory[reg_id::EFG] = op1>op2;
                        }

                    }
                    memory[reg_id::EFG]=!memory[reg_id::EFG];
                    break;               

                case EQUAL:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = memory[op1]==memory[op2];
                        } else {
                            memory[reg_id::EFG] = memory[op1]==op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = op1==memory[op2];
                        } else {
                            memory[reg_id::EFG] = op1==op2;
                        }

                    }
                    memory[reg_id::EFG]=!memory[reg_id::EFG];
                    break;                

                case LESS:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = memory[op1]<memory[op2];
                        } else {
                            memory[reg_id::EFG] = memory[op1]<op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[reg_id::EFG] = op1<memory[op2];
                        } else {
                            memory[reg_id::EFG] = op1<op2;
                        }

                    }
                    memory[reg_id::EFG]=!memory[reg_id::EFG];
                    break;                

                case RF:
                    memory[reg_id::EFG]=!memory[reg_id::EFG];
                    break;
                case JPIF:
                    if(memory[reg_id::EFG]!=0){
                        if (flag1 == type_op::REAL) {
                            memory[reg_id::EIP] += op1;
                        } else {
                            memory[reg_id::EIP] += memory[op1];
                        }
                        continue; // 需要立即跳到新位置，无需递增 EIP
                    }
                    break;    
                

                case JPNIF:
                    if(memory[reg_id::EFG]==false){
                        if (flag1 == type_op::REAL) {
                            memory[reg_id::EIP] += op1;
                        } else {
                            memory[reg_id::EIP] += memory[op1];
                        }
                        continue; // 需要立即跳到新位置，无需递增 EIP
                    }
                    break; 

                case JMP:
                    if (flag1 == type_op::REAL) {
                        memory[reg_id::EIP] += op1;
                    } else {
                        memory[reg_id::EIP] += memory[op1];
                    }
                    continue; // 需要立即跳到新位置，无需递增 EIP

                case OUT:
                    if (flag1 == type_op::POS) {
                        std::cout << static_cast<char>(memory[op1]);
                    } else {
                        std::cout << static_cast<char>(op1);
                    }
                    std::cout.flush();
                    break; 
                case IN:
                    char ch = getchar(); // 这是 conio.h 中的函数
                    assert(flag1 == type_op::POS);
                    memory[op1] = static_cast<int>(ch);
                    break; 
            }
            //if(instructs_times==7000242) break;
            memory[reg_id::EIP] += 1; // 递增指令指针
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed_time = end_time - start_time;
        std::cout <<"\nInstructs Calls:"<<instructs_times<< "\nVirtual Meachine Runing time: " << elapsed_time.count() << " seconds" << std::endl;
    }

    // 从代码字符串运行
    void Run_from_code(const std::vector<std::string> &lines) {
        std::cout << "********SYSTEM RUNNING********" << std::endl;
        RUN(lines);
    }

    // 从文件运行
    void Run_from_file(const std::string &file_path) {
        std::vector<std::string> lines;
        std::ifstream file(file_path);
        std::string line;
        while (std::getline(file, line)) {
            lines.push_back(line);
        }
        RUN(lines);
    }
};

int main() {
    Runner a;
    a.Run_from_file("IR.txt");
    exit(0);
    return 0;
}