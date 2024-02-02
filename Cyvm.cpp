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
opcode turns2i(std::string&str){
    return string2int.find(str)->second;
}
enum type_op{POS,REAL};
enum base_op{BASE,NOT_BASE};
class Runner {
private:
    std::vector<double> memory;
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
        memory.resize(max_memory + REGS.size(), 0);
    }

    // 计算位置函数
    std::pair<type_op, int> calc_pos(const std::string &text) {
        if (text.find("$") != std::string::npos) {
            int ans = 0;
            size_t colon_pos = text.find(":");
            ans = std::stoi(text.substr(1, colon_pos - 1));
            if (colon_pos != std::string::npos) {
                std::string second_part = text.substr(colon_pos + 1);
                if (second_part[0] == '$') {
                    ans += memory[std::stoi(second_part.substr(1))];
                } else {
                    ans += std::stoi(second_part);
                }
            } else {
                if (ans < 0) {
                    return {type_op::POS, ans};
                }
            }
            if (text.find("%") != std::string::npos) {
                return {type_op::POS, ans};
            } else {
                return {type_op::POS, ans + memory[REGS["EBP"]]};
            }
        } else {
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

    // 运行代码
    void RUN(const std::vector<std::string> &lines) {
        

        std::vector<std::vector<std::string>> keywordss;
        std::vector<opcode> opcodelist;
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
        while (true) {
            //std::cout<<memory[REGS["EIP"]]<<std::endl;
            int ip = memory[REGS["EIP"]];
            if (ip >= lines.size()) {
                break;
            }
            const auto &keywords = keywordss[ip];
            // for(auto &i :keywords) std::cout<<i<<" ";
            // std::cout<<std::endl;
            //std::cout<<ip<<std::endl;
            std::pair<type_op, int> k1, k2;
            if (keywords.size() >= 2) k1 = calc_pos(keywords[1]);
            if (keywords.size() >= 3) k2 = calc_pos(keywords[2]);
            int op1 = k1.second, op2 = k2.second;
            type_op& flag1=k1.first;
            type_op& flag2=k2.first;
            // 主指令处理逻辑
            auto n_opcode=opcodelist[ip];
            switch(n_opcode){
                case ALLOC: {
                    if(op1>=max_memory){
                        std::cout<<"Exceed the max memory limts"<<std::endl;
                        exit(0);
                    }
                    memory[REGS["ESP"]]=op1+1;
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
                        memory[op1] =int(memory[op1])% int(memory[op2]);
                    } else {
                        memory[op1] = int(memory[op1]) %int(op2);
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
                        memory[REGS["ESP"]] = int(memory[op1]);
                    } else {
                        memory[REGS["ESP"]] = int(op1);
                    }
                    memory[REGS["ESP"]]+=1;
                    break;                

                case POP:
                    assert(flag1 == type_op::POS);
                    memory[REGS["ESP"]]-=1;
                    memory[op1] = memory[REGS["ESP"]];
                    break;                
                

                case GREATER:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = memory[op1]>memory[op2];
                        } else {
                            memory[REGS["EFG"]] = memory[op1]>op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = op1>memory[op2];
                        } else {
                            memory[REGS["EFG"]] = op1>op2;
                        }

                    }
                    memory[REGS["EFG"]]=!memory[REGS["EFG"]];
                    break;               

                case EQUAL:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = memory[op1]==memory[op2];
                        } else {
                            memory[REGS["EFG"]] = memory[op1]==op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = op1==memory[op2];
                        } else {
                            memory[REGS["EFG"]] = op1==op2;
                        }

                    }
                    memory[REGS["EFG"]]=!memory[REGS["EFG"]];
                    break;                

                case LESS:
                    if(flag1== type_op::POS){

                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = memory[op1]<memory[op2];
                        } else {
                            memory[REGS["EFG"]] = memory[op1]<op2;
                        }
                    }else{
                        if (flag2 == type_op::POS) {
                            memory[REGS["EFG"]] = op1<memory[op2];
                        } else {
                            memory[REGS["EFG"]] = op1<op2;
                        }

                    }
                    memory[REGS["EFG"]]=!memory[REGS["EFG"]];
                    break;                

                case RF:
                    memory[REGS["EFG"]]=!memory[REGS["EFG"]];
                    break;
                case JPIF:
                    if(memory[REGS["EFG"]]!=0){
                        if (flag1 == type_op::REAL) {
                            memory[REGS["EIP"]] += op1;
                        } else {
                            memory[REGS["EIP"]] += memory[op1];
                        }
                        continue; // 需要立即跳到新位置，无需递增 EIP
                    }
                    break;    
                

                case JPNIF:
                    if(memory[REGS["EFG"]]==false){
                        if (flag1 == type_op::REAL) {
                            memory[REGS["EIP"]] += op1;
                        } else {
                            memory[REGS["EIP"]] += memory[op1];
                        }
                        continue; // 需要立即跳到新位置，无需递增 EIP
                    }
                    break; 

                case JMP:
                    if (flag1 == type_op::REAL) {
                        memory[REGS["EIP"]] += op1;
                    } else {
                        memory[REGS["EIP"]] += memory[op1];
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
                
            memory[REGS["EIP"]] += 1; // 递增指令指针
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed_time = end_time - start_time;
        std::cout << "\nVirtual Meachine Runing time: " << elapsed_time.count() << " seconds" << std::endl;
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