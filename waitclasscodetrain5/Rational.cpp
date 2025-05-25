#include <iostream>
#include "Rational.h"

Rational::Rational(int num, int den) {
    if (den == 0) {
        std::cerr << "Denominator cannot be zero. Setting to 1.\n";
        den = 1;
    }

    numerator = num;
    denominator = den;
    reduce();
}

int Rational::gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

void Rational::reduce() {
    int g = gcd(abs(numerator), abs(denominator));
    numerator /= g;
    denominator /= g;
    if (denominator < 0) {
        numerator = -numerator;
        denominator = -denominator;
    }
}

Rational Rational::add(const Rational& other) const {
    int num = numerator * other.denominator + other.numerator * denominator;
    int den = denominator * other.denominator;
    return Rational(num, den);
}

Rational Rational::subtract(const Rational& other) const {
    int num = numerator * other.denominator - other.numerator * denominator;
    int den = denominator * other.denominator;
    return Rational(num, den);
}

Rational Rational::multiply(const Rational& other) const {
    return Rational(numerator * other.numerator, denominator * other.denominator);
}

Rational Rational::divide(const Rational& other) const {
    return Rational(numerator * other.denominator, denominator * other.numerator);
}

void Rational::printFraction() const {
    std::cout << numerator << "/" << denominator;
}

void Rational::printFloat() const {
    std::cout << static_cast<double>(numerator) / denominator;
}

