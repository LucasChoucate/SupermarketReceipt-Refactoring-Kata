# Supermarket Receipt

You are working on the software for a supermarket, in particular for the teller machine that cashiers use to calculate the price of a shopping cart full of items and give the customer a receipt. The supermarket has a catalog of products for sale at various prices. Normally the price of a shopping cart is the sum of the prices of all the items in it. However, at any given time there might be special offers and price reductions on particular products. For example:

- 10% discount
- 3 for the price of 2
- 2 items for a reduced price
- 5 items for a reduced price

The starting position for this exercise contains the code for setting up the Teller object, a catalog of products, the shopping cart, and any special offers. It can calculate the price of a shopping cart and generate a receipt, but so far there aren't many test cases.

## Setup

From this folder (`python_pytest/`):

1. Create a virtual environment.
2. **Upgrade `pip` inside it.** Versions of `pip` below 26.2.2 have known vulnerabilities (alerts A-02 and A-03 in the [security analysis](../docs/seguranca_antes_depois.md#6-classificação-dos-alertas)).
3. Install the pinned requirements.
4. Run the tests with pytest.

Linux, macOS or WSL:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest
```
