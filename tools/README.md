# C++ and Python helper tools

These are real, standalone utilities for maintaining the Dharamraj Cartel website and preparing draft quotes. They are not blank files added just to influence GitHub's language display.

## Python: static website audit

From the repository root, run:

```bash
python3 tools/catalog_audit.py
```

The script checks root-level HTML pages for missing local assets/links and duplicate element IDs. It warns about images with no `alt` attribute and does not make network requests. A non-zero exit code indicates an audit error.

You can audit a different checkout path using `--root`:

```bash
python3 tools/catalog_audit.py --root /path/to/repository
```

## C++: draft quotation calculator

Compile with a C++17 compiler:

```bash
g++ -std=c++17 -O2 -Wall -Wextra -pedantic tools/quote_calculator.cpp -o quote-calculator
./quote-calculator
```

Enter item names, quantities, unit prices, a discount percentage, and the applicable VAT/tax percentage. The calculator shows line totals and a grand total. It does not assume a currency, supplier price, or tax rate.

## Important deployment note

GitHub Pages serves the existing static HTML website. The Python and C++ programs are offline maintenance/business tools; they do not run as part of the live website. A live Python backend or compiled C++ service would need a separate host and an explicit integration plan.
