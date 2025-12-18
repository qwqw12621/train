#include <iostream>
#include <map>
#include <iomanip>
#include <cctype>
#include <limits>

using namespace std;

/* =========================
 * Product Class
 * ========================= */
class Product {
private:
    char code;
    string name;
    int priceCents;

public:
    Product() {}
    Product(char c, string n, double price)
        : code(c), name(n), priceCents((int)(price * 100 + 0.5)) {}

    char getCode() const { return code; }
    string getName() const { return name; }
    int getPriceCents() const { return priceCents; }
};

/* =========================
 * SelectedItem Class
 * ========================= */
class SelectedItem {
private:
    Product product;
    int quantity;

public:
    SelectedItem() : quantity(0) {}
    SelectedItem(Product p) : product(p), quantity(0) {}

    Product getProduct() const { return product; }
    int getQuantity() const { return quantity; }

    void increase() { quantity++; }
    void decrease() {
        if (quantity > 0) quantity--;
    }
};

/* =========================
 * VendingMachine Class
 * ========================= */
class VendingMachine {
private:
    map<char, Product> products;
    map<char, SelectedItem> selectedItems;

    int totalDeposit; // cents

    // Bills
    int bill1, bill5, bill10, bill20;
    // Coins
    int coin5, coin10, coin25;

public:
    VendingMachine() {
        initProducts();
        resetTransaction();
    }

    void initProducts() {
        addProduct('A', "Coca Cola", 1.65);
        addProduct('B', "Minute Maid Orange Juice", 3.50);
        addProduct('C', "Evian Mineral Water", 2.80);
        addProduct('D', "M&M's Chocolate", 1.50);
        addProduct('E', "Hershey's Chocolate Bar", 1.85);
        addProduct('F', "Oreo Cookies", 1.00);
        addProduct('G', "Doritos Tortilla Chips", 3.25);
        addProduct('H', "Pringles Potato Chips", 3.40);
    }

    void addProduct(char code, string name, double price) {
        Product p(code, name, price);
        products[code] = p;
        selectedItems[code] = SelectedItem(p);
    }

    /* ===== Button a: Deposit Money ===== */
    void depositMoney() {
        cout << "\n[Deposit Money] B: Bill, C: Coin, Others: Exit\n";

        while (true) {
            cout << "Input (B/C): ";
            char type;
            cin >> type;
            type = toupper(type);

            if (type == 'B') depositBills();
            else if (type == 'C') depositCoins();
            else break;
        }
    }

    void depositBills() {
        cout << "Insert bill (1,5,10,20) or 0 to stop\n";
        int v;

        while (true) {
            cin >> v;

            if (cin.fail()) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "Invalid bill ignored\n";
                continue;
            }

            if (v == 0) break;

            switch (v) {
                case 1:  bill1++;  totalDeposit += 100; break;
                case 5:  bill5++;  totalDeposit += 500; break;
                case 10: bill10++; totalDeposit += 1000; break;
                case 20: bill20++; totalDeposit += 2000; break;
                default:
                    cout << "Invalid bill ignored\n";
            }
        }
    }

    void depositCoins() {
        cout << "Insert coin (5,10,25) or 0 to stop\n";
        int v;

        while (true) {
            cin >> v;

            if (cin.fail()) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "Invalid coin ignored\n";
                continue;
            }

            if (v == 0) break;

            switch (v) {
                case 5:  coin5++;  totalDeposit += 5; break;
                case 10: coin10++; totalDeposit += 10; break;
                case 25: coin25++; totalDeposit += 25; break;
                default:
                    cout << "Invalid coin ignored\n";
            }
        }
    }

    /* ===== Button b: Select Product ===== */
    void selectProduct() {
        cout << "\nSelect product A~H, Q to quit\n";
        char c;

        while (true) {
            cin >> c;
            c = toupper(c);

            if (c == 'Q') break;
            if (products.count(c)) {
                selectedItems[c].increase();
            }
        }
    }

    /* ===== Button c: Cancel Product ===== */
    void cancelProduct() {
        cout << "Cancel product A~H: ";
        char c;
        cin >> c;
        c = toupper(c);

        if (selectedItems.count(c)) {
            selectedItems[c].decrease();
        }
    }

    /* ===== Button d: Purchase ===== */
    void purchase() {
        int totalPrice = getTotalPrice();

        if (totalDeposit < totalPrice) {
            cout << "Insufficient Deposit\n";
            depositMoney();
            return;
        }

        cout << "\nDispensing products...\n";
        printSelectedItems();

        int change = totalDeposit - totalPrice;
        returnChange(change);
        resetTransaction();
    }

    /* ===== Button e: Abort ===== */
    void abortTransaction() {
        cout << "\nTransaction Aborted\n";
        cout << "Returning money...\n";
        cout << "Total Returned: $" << fixed << setprecision(2)
             << totalDeposit / 100.0 << endl;

        resetTransaction();
    }

    /* ===== Utilities ===== */
    int getTotalPrice() {
        int sum = 0;
        for (auto &p : selectedItems)
            sum += p.second.getQuantity()
                 * p.second.getProduct().getPriceCents();
        return sum;
    }

    void returnChange(int cents) {
        cout << "Change Returned:\n";
        cout << "25-cent coin x " << cents / 25 << endl; cents %= 25;
        cout << "10-cent coin x " << cents / 10 << endl; cents %= 10;
        cout << "5-cent coin  x " << cents / 5 << endl;
    }

    void printSelectedItems() {
        for (auto &p : selectedItems) {
            if (p.second.getQuantity() > 0) {
                cout << p.first << " "
                     << p.second.getProduct().getName()
                     << " x " << p.second.getQuantity() << endl;
            }
        }
    }

    void resetTransaction() {
        totalDeposit = 0;
        bill1 = bill5 = bill10 = bill20 = 0;
        coin5 = coin10 = coin25 = 0;

        for (auto &p : selectedItems)
            while (p.second.getQuantity() > 0)
                p.second.decrease();
    }

    void showStatus() {
        cout << "\n---- Transaction Status ----\n";
        cout << "Deposit: $" << fixed << setprecision(2)
             << totalDeposit / 100.0 << endl;
        cout << "Total Price: $" << fixed << setprecision(2)
             << getTotalPrice() / 100.0 << endl;
        cout << "----------------------------\n";
    }
};

/* =========================
 * Main
 * ========================= */
int main() {
    VendingMachine vm;
    char cmd;

    while (true) {
        cout << "\n[a]Deposit [b]Select [c]Cancel [d]Purchase [e]Abort [x]Exit\n";
        cin >> cmd;
        cmd = tolower(cmd);

        if (cmd == 'a') vm.depositMoney();
        else if (cmd == 'b') vm.selectProduct();
        else if (cmd == 'c') vm.cancelProduct();
        else if (cmd == 'd') vm.purchase();
        else if (cmd == 'e') vm.abortTransaction();
        else if (cmd == 'x') break;

        vm.showStatus();
    }
    return 0;
}