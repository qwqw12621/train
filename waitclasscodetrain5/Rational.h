#ifndef RATIONAL_H
#define RATIONAL_H

class Rational {
private:
    int numerator;
    int denominator;
    void reduce();
    int gcd(int a, int b);

public:
    Rational(int num = 0, int den = 1);

    Rational add(const Rational& other) const;
    Rational subtract(const Rational& other) const;
    Rational multiply(const Rational& other) const;
    Rational divide(const Rational& other) const;

    void printFraction() const;
    void printFloat() const;
};

#endif

