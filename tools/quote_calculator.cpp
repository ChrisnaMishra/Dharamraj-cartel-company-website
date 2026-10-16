// Dharamraj Cartel — offline quotation calculator
// Build: g++ -std=c++17 -O2 -Wall -Wextra -pedantic tools/quote_calculator.cpp -o quote-calculator
// Run:   ./quote-calculator
//
// Prices and tax rates are entered by the user. This utility does not assume
// supplier prices, exchange rates, duties, or a fixed VAT rate.

#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

struct LineItem {
    std::string name;
    double quantity{};
    double unit_price{};
};

bool read_number(const std::string& prompt, double& value,
                 double minimum, double maximum) {
    while (true) {
        std::cout << prompt;
        if (std::cin >> value && value >= minimum && value <= maximum) {
            return true;
        }

        if (std::cin.eof()) {
            return false;
        }
        std::cout << "Please enter a number between " << minimum << " and "
                  << maximum << ".\n";
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
}

int main() {
    std::cout << "===========================================\n"
              << "  DHARAMRAJ CARTEL | QUOTE CALCULATOR\n"
              << "===========================================\n"
              << "Enter the quantities and prices for this quote.\n"
              << "Use the currency and units relevant to your order.\n\n";

    std::vector<LineItem> items;
    char add_more = 'y';

    while (add_more == 'y' || add_more == 'Y') {
        LineItem item;
        std::cout << "Product / item name: ";
        std::cin >> std::ws;
        if (!std::getline(std::cin, item.name)) {
            return 0;
        }
        if (item.name.empty()) {
            std::cout << "The item name cannot be blank. Try again.\n";
            continue;
        }

        if (!read_number("Quantity: ", item.quantity, 0.000001, 1.0e12) ||
            !read_number("Unit price: ", item.unit_price, 0.0, 1.0e15)) {
            std::cout << "\nInput ended. Quote cancelled.\n";
            return 1;
        }
        items.push_back(item);

        std::cout << "Add another item? (y/n): ";
        if (!(std::cin >> add_more)) {
            return 0;
        }
        std::cout << '\n';
    }

    if (items.empty()) {
        std::cout << "No items entered; no quote was created.\n";
        return 0;
    }

    double discount_percent = 0.0;
    double tax_percent = 0.0;
    if (!read_number("Discount percentage (0-100): ", discount_percent,
                     0.0, 100.0) ||
        !read_number("Tax/VAT percentage (0-100): ", tax_percent, 0.0, 100.0)) {
        std::cout << "\nInput ended. Quote cancelled.\n";
        return 1;
    }

    double subtotal = 0.0;
    std::cout << "\n---------------- QUOTE ----------------\n"
              << std::left << std::setw(27) << "Item"
              << std::right << std::setw(10) << "Qty"
              << std::setw(16) << "Unit price"
              << std::setw(16) << "Line total" << '\n';
    std::cout << std::string(69, '-') << '\n';
    std::cout << std::fixed << std::setprecision(2);

    for (const auto& item : items) {
        const double line_total = item.quantity * item.unit_price;
        subtotal += line_total;
        const std::string label = item.name.size() > 26
            ? item.name.substr(0, 23) + "..."
            : item.name;
        std::cout << std::left << std::setw(27) << label
                  << std::right << std::setw(10) << item.quantity
                  << std::setw(16) << item.unit_price
                  << std::setw(16) << line_total << '\n';
    }

    const double discount = subtotal * discount_percent / 100.0;
    const double taxable_amount = subtotal - discount;
    const double tax = taxable_amount * tax_percent / 100.0;
    const double grand_total = taxable_amount + tax;

    std::cout << std::string(69, '-') << '\n'
              << std::left << std::setw(40) << "Subtotal"
              << std::right << std::setw(29) << subtotal << '\n'
              << std::left << std::setw(40) << "Discount"
              << std::right << std::setw(29) << -discount << '\n'
              << std::left << std::setw(40) << "Taxable amount"
              << std::right << std::setw(29) << taxable_amount << '\n'
              << std::left << std::setw(40)
              << ("Tax / VAT (" + std::to_string(tax_percent) + "%)")
              << std::right << std::setw(29) << tax << '\n'
              << std::left << std::setw(40) << "TOTAL"
              << std::right << std::setw(29) << grand_total << '\n'
              << "-----------------------------------------\n"
              << "This is an estimate. Confirm prices and applicable taxes\n"
              << "before issuing a formal invoice.\n";
    return 0;
}
