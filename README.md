# Finance-Manager 
## Overview
This is a python program that has GUI and CLI functionality. Its main function is to manage financial transaction and produce monthly reports and provide suggestions. As an additional feature, it also record diary entries.

## Requirements
- customtkinter : Used to create the GUI
- argparse : Used to parse the command line arguments
- tabulate : Used to display information specifically tables in CLI
- pandas : Used for statistics

## Usage
- `python project.py` : No argument creates a new account by taking the following parameters : Username, Password and Financial Balance
- `python project.py <-d/--diary> <write/read/del>` : 
    - `python project.py <-d/--diary> write` : Authenticates the user and takes the date, category and content of the diary entry as input and saves it.
    - `python project.py <-d/--diary> read` : Authenticates the user and takes the date of required diary entry and displays the entry and gives an error message if no entry is found.
    - `python project.py <-d/--diary> del` : Authenticates the user and takes the date and deletes the diary entry.
    
- `python project.py <-f/--finance> <append/read/del>` : Shows all the financial transactions in a table or adds a transaction.
    - `python project.py <-f/--finance> append` : Adds a transaction taking the follwong paramaters : Date, detail, amount and debit/credit.
    - `python project.py <-f/--finances> read` : Displays a table of all the financial transactions using tabulate.
    - `python project.py <-f/--finances> del` : Authenticates the user and takes the transaction id and then, it deletes the transaction.

- `python project.py <-s/--stats>` : Provides the following statistics regarding the financila postion : 
    - Total money spent in a month
    - Total money recieved in a month
    - Item on which most money was spent
    - Most frequently bought item.

- `python project.py <-q/--query> <finance/diary>` 
    - `python project.py <-q/--query> finance` : Takes some filter parameters (Date, Detail, Amount, Dr/Cr) and returns search reults in a table using tabulate.
    - `python project.py <-q/--query> diary` : Asks for some filter parameters (Date, Caategory) and returns search reults in a table using tabulate.

- `python project.py <-r/--report>` : Authenticates the user and generates a monthly financial report according to the data.

- `python project.py <-u/--gui>` : Acivates GUI mode.

- `python project.py <-t/--terminate>` : Authenticates the user and terminates the account associated.