#include <iostream>
#include "Rational.h"
//g++ main.cpp Rational.cpp -o rational_prograqm


void displayMenu() {
    std::cout << "1. �[�k\n2. ��k\n3. ���k\n4. ���k\n";
    std::cout << "���: ";
}

int main() {
    while (1) {
        std::cout << "\n�п�J��Ӥ��� (�榡�G���l ���� ���l �����A�Ҧp 1 2 3 4 �N�� 1/2 �M 3/4)�G ";
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
            std::cout << "�{�������C\n";
            break;
        }
		else {
            std::cout << "�L�Ī��ﶵ�C\n";
            break;
        }

        std::cout << "��ܿ�X�榡�]5 = ���ơA6 = �B�I�^: ";
        std::cin >> choice;

        if (choice == "5") {
            std::cout << "���G���G";
            result.printFraction();
            std::cout << std::endl;
        } else if (choice == "6") {
            std::cout << "���G���G";
            result.printFloat();
            std::cout << std::endl;
        } else if (choice == "x" || choice == "X") {
            std::cout << "�{�������C\n";
            break;
        } else {
            std::cout << "�L�Į榡��ܡC\n";
        }
    }

    return 0;
}

