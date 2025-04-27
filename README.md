# Finance-Manager 
## Overview
This is a python program that has GUI and CLI functionality. Its main function is to manage financial transaction and produce monthly reports and provide suggestions. As an additional feature, it also records diary entries.

## Requirements
- customtkinter : Used to create the GUI
- argparse : Used to parse the command line arguments
- tabulate : Used to display tables in CLI
- pandas : Used for statistics

## Usage
- `python main.py` : No argument creates a new account by taking the following parameters : Username, Password and Financial Balance
- `python main.py <-d/--diary> <write/read/del>` : 
    - `python main.py <-d/--diary> write` : Authenticates the user and takes the date, category and content of the diary entry as input and saves it.
    - `python main.py <-d/--diary> read` : Authenticates the user and takes the date of required diary entry and displays the entry and gives an error message if no entry is found.
    - `python main.py <-d/--diary> del` : Authenticates the user and takes the date and deletes the diary entry.
    
- `python main.py <-f/--finance> <append/read/del>` : Shows all the financial transactions in a table or adds a transaction.
    - `python main.py <-f/--finance> append` : Adds a transaction taking the follwong paramaters : Date, detail, amount and debit/credit.
    - `python main.py <-f/--finances> read` : Displays a table of all the financial transactions using tabulate.
    - `python main.py <-f/--finances> del` : Authenticates the user and takes the transaction id and then, it deletes the transaction.

- `python main.py <-s/--stats>` : Provides the following statistics regarding the financila postion : 
    - Total money spent in a month
    - Total money recieved in a month
    - Item on which most money was spent
    - Most frequently bought item.

- `python main.py <-q/--query> <finance/diary>` 
    - `python main.py <-q/--query> finance` : Takes some filter parameters (Date, Detail, Amount, Dr/Cr) and returns search reults in a table using tabulate.
    - `python main.py <-q/--query> diary` : Asks for some filter parameters (Date, Caategory) and returns search reults in a table using tabulate.

- `python main.py <-r/--report>` : Authenticates the user and generates a monthly financial report according to the data.

- `python main.py <-u/--gui>` : Acivates GUI mode.

- `python main.py <-t/--terminate>` : Authenticates the user and terminates the account associated.

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
