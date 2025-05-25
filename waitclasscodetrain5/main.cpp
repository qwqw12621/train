#include <iostream>
#include "Rational.h"
//g++ main.cpp Rational.cpp -o rational_prograqm


void displayMenu() {
    std::cout << "1. 加法\n2. 減法\n3. 乘法\n4. 除法\n";
    std::cout << "選擇: ";
}

int main() {
    while (1) {
        std::cout << "\n請輸入兩個分數 (格式：分子 分母 分子 分母，例如 1 2 3 4 代表 1/2 和 3/4)： ";
        int n1, d1, n2, d2;
        std::cin >> n1 >> d1 >> n2 >> d2;

        Rational r1(n1, d1);
        Rational r2(n2, d2);

        displayMenu();

        std::string choice;
        std::cin >> choice;

        Rational result;
        
        if (choice == "1") {
            result = r1.add(r2);
        } else if (choice == "2") {
            result = r1.subtract(r2);
        } else if (choice == "3") {
            result = r1.multiply(r2);
        } else if (choice == "4") {
            result = r1.divide(r2);
        } else if (choice == "x" || choice == "X") {
            std::cout << "程式結束。\n";
            break;
        }
		else {
            std::cout << "無效的選項。\n";
            break;
        }

        std::cout << "選擇輸出格式（5 = 分數，6 = 浮點）: ";
        std::cin >> choice;

        if (choice == "5") {
            std::cout << "結果為：";
            result.printFraction();
            std::cout << std::endl;
        } else if (choice == "6") {
            std::cout << "結果為：";
            result.printFloat();
            std::cout << std::endl;
        } else if (choice == "x" || choice == "X") {
            std::cout << "程式結束。\n";
            break;
        } else {
            std::cout << "無效格式選擇。\n";
        }
    }

    return 0;
}

