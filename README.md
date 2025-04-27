# Finance-Manager

## Overview
This is a Python program with both GUI and CLI functionality. Its main purpose is to manage financial transactions, produce monthly reports, and provide suggestions. As an additional feature, it also records diary entries.

## Requirements
- `customtkinter` : Used to create the GUI
- `argparse` : Used to parse command line arguments
- `tabulate` : Used to display tables in CLI
- `pandas` : Used for statistics

Install required packages:
```bash
pip install customtkinter pandas tabulate
```
## Usage

### Create New Account
```bash
python main.py
```
- No arguments: Creates a new account by taking the following parameters:
  - Username
  - Password
  - Financial Balance

### Diary Management
```bash
python main.py -d <write/read/del>
```
- `write`: Authenticates the user and saves a diary entry (date, category, content).
- `read`: Authenticates the user and reads a diary entry by date.
- `del`: Authenticates the user and deletes a diary entry by date.

### Financial Transactions
```bash
python main.py -f <append/read/del>
```
- `append`: Adds a transaction (date, detail, amount, debit/credit).
- `read`: Displays a table of all financial transactions.
- `del`: Authenticates the user and deletes a transaction by ID.

### Financial Statistics
```bash
python main.py -s
```
Provides statistics such as:
- Total money spent in a month
- Total money received in a month
- Item with most money spent
- Most frequently bought item

### Query Function
```bash
python main.py -q <finance/diary>
```
- `finance`: Filter finance transactions (by Date, Detail, Amount, Dr/Cr).
- `diary`: Filter diary entries (by Date, Category).

### Monthly Report
```bash
python main.py -r
```
Authenticates the user and generates a monthly financial report.

### GUI Mode
```bash
python main.py -u
```
Launches the GUI version of the application.

### Terminate Account
```bash
python main.py -t
```
Authenticates the user and terminates the associated account.

---

## License

This project is open-source and available under the MIT License.

---

**Made with 💻 by [Pro-Algorythm](https://github.com/Pro-Algorythm)**
