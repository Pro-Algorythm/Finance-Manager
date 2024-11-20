import sys
from argparse import ArgumentParser
import csv
from datetime import datetime, date as datetime_date
from customtkinter import *
import os
import shutil
import hashlib as hash
import functools
import tabulate as tab
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as StatCanvas
import matplotlib.pyplot as plt 
import calendar as cal

"""
Run the following command to install all dependencies:
pip install -r requirements.txt

Sample account:
Username : sample
Password : 1

"""


def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--diary', choices = ['write', 'read', 'del'])
    parser.add_argument('-f', '--finance', choices = ['read', 'append', 'del'])
    parser.add_argument('-b', '--budget', action = 'store_true')
    parser.add_argument('-o', '--overview', action = 'store_true')
    parser.add_argument('-v', '--view_budgets', action = 'store_true')
    parser.add_argument('-s', '--stats', action = 'store_true')
    parser.add_argument('-q', '--query', choices = ['finance', 'diary'])
    parser.add_argument('-r', '--report', action = 'store_true')
    parser.add_argument('-u', '--gui', action = 'store_true')
    parser.add_argument('-t', '--terminate', action = 'store_true')
    args = parser.parse_args()
    if args.gui:
        GUI()
    elif args.diary:
        if args.diary == 'write':
            write(authenticate(input('Name : '),input('Password : ')), input('Date of diary entry(leave empty to input todays date) \nFormat : dd/mm/yyyy: '), input('Category: '), input_entry())
        elif args.diary == 'read':
            read(authenticate(input('Name : '),input('Password : ')), input('Date of diary entry (dd/mm/yyyy):'))
        else:
            delete_entry(authenticate(input('Name : '),input('Password : ')), input('Date of diary entry (dd/mm/yyyy): '))
    elif args.finance in ['read', 'append']:
        finance(authenticate(input('Name : '),input('Password : ')), args.finance)
    elif args.finance == 'del':
        delete_transaction(authenticate(input('Name : '),input('Password : ')), input('Transaction ID : '))
    elif args.budget:
        set_budget(authenticate(input('Name : '),input('Password : ')))
    elif args.view_budgets:
        get_budgets(authenticate(input('Name : '),input('Password : ')), print_results = True)
    elif args.overview:
        overview(authenticate(input('Name : '),input('Password : ')))
    elif args.terminate:
        del_acc(authenticate(input('Name : '),input('Password : ')), gui = False)
    elif args.stats:
        stats(authenticate(input('Name : '),input('Password : ')))
    elif args.query:
        get_query_results(authenticate(input('Name : '),input('Password : ')), args.query)
    elif args.report:
        get_report(authenticate(input('Name : '),input('Password : ')))
    else:
        create_acc(input('Name : '),input('Enter password : '), input('Current balance : '))

def create_acc(name, password, bal, gui = False):
    password = hash.sha256(bytes(password, 'utf-8')).hexdigest()
    try:
        os.chdir(f'{name}')
        if gui:
            return 'Username is not available.'
        print('Username is not available.')
        return False
    except FileNotFoundError:
        try:
            with open('passwords.csv', 'r') as pwd:
                pass
            with open('passwords.csv', 'a') as pwd:
                writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
                writer.writerow({'username': name, 'password': password})
        except FileNotFoundError:
            with open('passwords.csv', 'a') as pwd:
                writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
                writer.writeheader()
                writer.writerow({'username': name, 'password': password})

        os.mkdir(f'{name}')
        os.chdir(f'{name}')
        with open(f'diary.csv', 'a') as db:
            d_writer = csv.DictWriter(db, fieldnames = ['date', 'category', 'entry'])
            d_writer.writeheader()
        with open('finance.csv', 'a') as fin:
            fin_writer = csv.DictWriter(fin, fieldnames = ['id', 'date', 'detail', 'category', 'amount', 'dr_cr',  'balance'])
            fin_writer.writeheader()
            fin_writer.writerow({'id':0,'date': datetime.now().today().strftime('%d-%m-%Y'), 'detail': 'Initial Balance', 'category' : '--', 'amount': bal, 'dr_cr': 'debit', 'balance': bal})
        with open('budgets.csv', 'a') as budgets:
            b_writer = csv.DictWriter(budgets, ['type', 'category', 'amount'])
            b_writer.writeheader()
        os.chdir(os.pardir)
        return True

def del_acc(name, gui = True):
    if not gui:
        if not input('Type y/n to confirm delete : ') in ['yes','y']:
            print('Delete cancelled.')
            return

    shutil.rmtree(f'{name}')
    with open('passwords.csv','r') as db:
        reader = csv.DictReader(db, fieldnames = ['username', 'password'])
        rows = []
        for row in reader:
            if row['username'] == name:
                continue
            rows.append(row)
    os.remove('passwords.csv')
    with open('passwords.csv','w') as db:
        writer = csv.DictWriter(db, fieldnames = ['username', 'password'])
        writer.writeheader()
        writer.writerows(rows[1::])
    
def input_entry():
    print("Entry (Type 'end' on a new line when done): \n\n")
    entry = ''
    while True:
        line = input()
        if line.lower().strip() != 'end':
            entry += '\n'+line
        else:
            break
    return entry

def overview(name):
    os.chdir(name)
    print(f'\nDiary entries : {len(list(csv.DictReader(open('diary.csv', 'r'))))}\nBalance : {list(csv.DictReader(open('finance.csv', 'r')))[-1]['balance']}')
    os.chdir(os.pardir)

def authenticate(name, password, gui = False):
    access = False
    password = hash.sha256(bytes(password, 'utf-8')).hexdigest()
    try:
        with open('passwords.csv', 'r') as pwd:
            pass
    except FileNotFoundError:
        with open('passwords.csv', 'w') as pwd:
            writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
            writer.writeheader()

    with open('passwords.csv', 'r') as pwd:
        reader = csv.DictReader(pwd)
        for row in reader:
            if row['username'] == name and row['password'] == password:
                access = True
        if access:
            if gui:
                return True
            return name
        else:
            if gui:
                return 'Wrong username or password.'
            print('Wrong username or password!')
            sys.exit()

def read(name, date):
    if convert_Date(date) == False:
        print('Invalid date.')
        return

    os.chdir(f'{name}')
    with open('diary.csv','r') as file:
        reader = csv.DictReader(file)
        entry = [row['entry'] for row in reader if row['date'] == date]
        if entry:
            print('\n', *entry)
            os.chdir(os.pardir)
            return entry
        else:
            print('\nNo entry on that date or invalid date.')
            os.chdir(os.pardir)

def write(name, date, category, entry, gui = False):
    os.chdir(name)
    with open('diary.csv', 'a') as file:
        writer = csv.DictWriter(file, fieldnames = ['date', 'category', 'entry'])
        if date:
            validation = convert_Date(date)
            if validation == False:
                if gui:
                    os.chdir(os.pardir)
                    return 'Invalid date.'
                else:
                    print('Invalid date.')
                    os.chdir(os.pardir)
                    return
        else:
            date = str(datetime.now().date().strftime('%d-%m-%Y'))

        if date in get_info(name, 'date'):
            os.chdir(os.pardir)
            if gui:
                return 'Entry already exists on that date.'
            else:
                print('\nEntry already exists on that date.')
                return
        writer.writerow({'date': date, 'category': category, 'entry': entry})

        if gui:
            os.chdir(os.pardir)
            return 'Entry added'
        print('\nEntry added.')
        os.chdir(os.pardir)

def get_info(name, item):
    try:
        os.chdir(f'{name}')
        flag = True
    except FileNotFoundError:
        flag = False

    with open('diary.csv', 'r') as db:
        reader = csv.DictReader(db)
        items = [row[item] for row in reader ]
        items = set(items)

    if flag:
        os.chdir(os.pardir)

    return items

def finance(name, action = 'append', date = None, detail = None, category = None, amount = None, dr_cr = None, gui = False):
    os.chdir(name)
    reader = list(csv.DictReader(open('finance.csv', 'r')))

    if action =='read':
        table_data = []
        for row in reader:
            table_data.append([row['id'], row['date'], row['detail'], row['category'], row['amount'], row['dr_cr'].title(), row['balance']])
        if len(table_data) > 0:
            print(tab.tabulate(table_data, headers=['ID', 'Date', 'Detail', 'Category', 'Amount', 'Dr/Cr', 'Balance'], tablefmt='grid'))
            return
        print('\nNo data available.')

    elif action == 'append':

        balance = float([row['balance'] for row in reader][-1])
        id = int([row['id'] for row in reader][-1])+1

        if not gui:
            date = input('Date: ')
            detail = input('Detail: ')
            if detail == '':
                print('Detail cannot be empty.')
                return
            categories = ['Loan', 'Education', 'Salary', 'Groceries', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous']
            category = input('Category: ')
            while True:
                if category.title() in categories:
                    break
                else:
                    category = input('Choose from \n' + '\n'.join(categories)+'\nCategory : ')
            while True:
                try:
                    amount = float(input('Amount: '))
                    break
                except:
                    print('Invalid amount.')
            dr_cr = input('Debit or credit: ')
            while dr_cr not in ['debit', 'credit']:
                dr_cr = input('Debit or credit: ')
            if dr_cr == 'credit' and amount > balance:
                print('\nInsufficient balance.')
                return
        date = convert_Date(date, return_type='str')
        if date == False:
            if gui:
                os.chdir(os.pardir)
                return 'Invalid date.'
            else:
                os.chdir(os.pardir)
                print('Invalid date.')
                return

        if dr_cr == 'credit':
            if float(amount) > balance:
                os.chdir(os.pardir)
                return 'Insufficient balance.'
            balance-=float(amount)
        else:
            balance += float(amount)
        
        with open('finance.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames = ['id', 'date', 'detail', 'category', 'amount', 'dr_cr', 'balance'])
            writer.writerow({'id' : id,'date': date, 'detail': detail, 'category' : category, 'amount': amount,'dr_cr': dr_cr, 'balance': balance})
        if gui:
            os.chdir(os.pardir)
            return 'Transaction added.'
        else:
            os.chdir(os.pardir)
            print('\nTransaction recorded.')

def set_budget(name, type = None, budgets = None, gui = False):
    os.chdir(name)

    categories = ['Education', 'Groceries', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous']
    
    if not gui:
        overall = input('Overall budget : ')
        if not overall.isdigit():
            print('Invalid budget.')
            return
        overall = float(overall)
        budgets = []
        budgets.append(('overall', overall))
        for category in categories:
            budget = input(f'Budget for {category} (Enter without any value to skip the category): ')
            
            if budget.isdigit():
                try:
                    float(budget)

                except:
                    print('Invalid budget.')
                    return
                
                budgets.append((category, float(budget)))
                if sum([float(budget[1]) for budget in budgets if budget[0] != 'overall']) > overall:
                    print('Total budget exceeds overall budget.')
                    return

    with open('budgets.csv', 'w') as budget_file:
        writer = csv.DictWriter(budget_file, ['type', 'category', 'amount'])

        writer.writeheader()
        
        for category, amount in budgets:
            if category == 'overall':
                writer.writerow({'type': 'overall', 'category': '--', 'amount' : amount})
            else:
                writer.writerow({'type': 'categorical', 'category': category, 'amount' : amount})
    if not gui:
        print('Budgets set successfully.')
        return
    os.chdir(os.pardir)
    return True

def get_budgets(name, print_results=False):
    os.chdir(name)
    reader = list(csv.DictReader(open('budgets.csv', 'r')))
    budgets = []
    if len(reader) == 0:
        if print_results:
            print('No data available.')
        else:
            os.chdir(os.pardir)
            return []
        
    for row in reader:
        if print_results:
            print(f'{row["type"].title()}: {row["category"]} - {row["amount"]}')
        else:
            budgets.append((row['type'], row['category'], row['amount']))
    os.chdir(os.pardir)
    return budgets

def delete_transaction(name, transaction_id, gui=False):
    os.chdir(name)
    db = list(csv.DictReader(open('finance.csv', 'r')))
    transaction = None
    if transaction_id == '0':
        print('Initial balance cant be removed.')
        return

    for i in range(len(db)):
        if db[i]['id'] == transaction_id:
            transaction = db[i]
            db.remove(db[i])
            break

    if not(transaction):
        os.chdir(os.pardir)
        print('\nTransaction not found.')
        return
        
    for i in range(i, len(db)):
        if transaction['dr_cr'] == 'debit':
            db[i]['balance'] = float(db[i]['balance']) - float(transaction['amount'])
        else:
            db[i]['balance'] = float(db[i]['balance']) + float(transaction['amount'])
        db[i]['id'] = int(db[i]['id']) -1

    
    with open('finance.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames = ['id', 'date', 'detail', 'category', 'amount', 'dr_cr', 'balance'])
        writer.writeheader()
        writer.writerows(db)
    if not gui:
        print('Transaction deleted successfully.')
    os.chdir(os.pardir)
    return True

def delete_entry(name, date, gui = False):
    if not date in get_info(name, 'date'):
        print('Entry not found')
        return
    
    os.chdir(name)
    db = list(csv.DictReader(open('diary.csv', 'r+')))
    
    for i in range(len(db)):
        if db[i]['date'] == date:
            db.remove(db[i])
            break
    
    with open('diary.csv', 'w') as diary:
        writer = csv.DictWriter(diary, fieldnames=['date', 'category', 'entry'])
        writer.writeheader()
        writer.writerows(db)
    if not gui:
        print('Entry deleted successfully.')
    os.chdir(os.pardir)
    return True

def convert_Date(date, return_type = 'datetime'):
    try:
        date = datetime_date(int(date.split('-')[2]), int(date.split('-')[1]), int(date.split('-')[0]))
        if return_type == 'datetime':
            return datetime.strptime(date.strftime('%d-%m-%Y'), '%d-%m-%Y')
        else:
            return '-'.join([str(date.day).zfill(2), str(date.month).zfill(2), str(date.year).zfill(4)])
    except:
        return False

def stats(name, gui = False):
    os.chdir(name)
    reader = list(csv.DictReader(open('finance.csv', 'r')))
    if len(reader) == 1:
        if gui:
            os.chdir(os.pardir)
            return 'No data available.'
        else:
            os.chdir(os.pardir)
            print('\nNo data available.')
            return

    items = set([row['detail'] for row in reader if row['detail'] != 'Initial Balance'])
    #Amount spent in a month
    amount_month_cr = sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)])

    #Amount recieved in a month
    amount_month_dr = sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['category'] != 'Loan')  and (row['dr_cr'] == 'debit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)])

    items_amount = []
    for item in items:
        items_amount.append((item, sum([float(row['amount']) for row in reader if (row['detail'] == item) and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)] )))

    items_amount = [row['detail'] for row in reader if (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)]

    item_count = [(str(i), items_amount.count(i)) for i in items ]
    most_frequent_item = []
    for item in item_count:
        if max([i[1] for i in item_count]) != 0 and item[1] == max([i[1] for i in item_count]):
            most_frequent_item.append((str(item[0]), max([i[1] for i in item_count])))

    categories = set([row['category'] for row in reader if row['category'] not in ['--', 'Loan', 'Salary']])
    categories = sorted(list(categories), key = lambda item : len(item), reverse = True)
    amount_categories = {}
    for category in categories:
        amount = sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (row['category'] == category)])
        amount_categories[amount] = category

    most_spent_category = (max(amount_categories.keys()), amount_categories[max(amount_categories.keys())] )


    amount_items = {}
    for item in items:
        amount = sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (row['category'] == category)])
        amount_items[amount] = category

    items_Spent = [(row['detail'], row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) ]

    transactions = len(reader)
    expensive_item = ('', 0)
    for i in items_Spent:
        if float(i[1]) > float(expensive_item[1]):
            expensive_item = (i[0], i[1])
    balance = [row['balance'] for row in reader][-1]

    week1 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(1,8))]))
    week2 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(8,15))]))
    week3 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(15,22))]))
    week4 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(22,29))]))
    if cal.monthrange(datetime.now().date().year, datetime.now().date().month)[1] == 30:
        week5 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(29,31))])) * 3.5
    else:
        week5 = float(sum([float(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (convert_Date(row['date']).day in range(29,32))]) * (7/3), 2)
    weekly_spendage = round((amount_month_cr / cal.monthrange(datetime.now().date().year, datetime.now().date().month)[1]) *7)
    weekly_analysis = {
        'Week 1' : week1,
        'Week 2' : week2,
        'Week 3' : week3,
        'Week 4' : week4,
        'Projected Week 5' : week5,
        'average' : round(weekly_spendage, 2)
    }
    for week in weekly_analysis:
        if max(list(weekly_analysis.values())[0:4]) == weekly_analysis[week]:
            weekly_analysis['Week with most spendage'] =  (week, weekly_analysis[week])
            break
    for week in weekly_analysis:
        if min([i for i in list(weekly_analysis.values())[0:4] if i != 0]) == weekly_analysis[week]:
            weekly_analysis['Week with least spendage'] =  (week, weekly_analysis[week])
            break

    if not gui:
        print("Current Balance : ", balance)
        print('Amount spent in this month :', amount_month_cr)
        print('Amount recieved in this month :', amount_month_dr)
        print('Most amount spent on an item in this month :', expensive_item[0], 'for', expensive_item[1])
        print("Most frequently bought items in this month :", *most_frequent_item)
        print("Category with highest spendings :", most_spent_category)
        print("Average weekly spendage : ", weekly_spendage)
        print("Total number of transactions :", transactions)
        os.chdir(os.pardir)
        return
    else:
        os.chdir(os.pardir)
        return {'Items': items, "Money spent": amount_month_cr, "Money recieved": amount_month_dr, "Most expensive item": expensive_item, "Most frequently bought item": most_frequent_item, "Category with highest spending" : most_spent_category, "Categories and amount spent": amount_categories, "Number of transactions" : transactions, "Balance" : balance, 'weekly analysis' : weekly_analysis}

def get_query_results(name, domain,data = None, gui = False):
    os.chdir(name)
    
    if domain == 'diary':
        df = pd.read_csv('diary.csv')

        if not(gui):
            data = {
                'date' : input('Date (Leave empty for any) : '), 
                'category' : input('Category (Leave empty for any) : ')
                }

        query = ' & '.join([f"{key} == '{value}'" for key, value in data.items() if value])
        if query == '':
            os.chdir(os.pardir)
            return df
        res = df.query(query)
        if not(gui):
            print(f'{len(res)} Results\n----------------------------------')
            for i in range(len(res)):
                print(res.iloc[i,0])
                print(res.iloc[i,1], '\n')
                print(res.iloc[i,2], '\n----------------------------------')
            os.chdir(os.pardir)
            return
        os.chdir(os.pardir)
        return res
        
    else:
        df = pd.read_csv("finance.csv")

        if not(gui):
            data = {'date' : input('Date (Leave empty for any) : '), 'detail' : input('Detail (Leave empty for any) : '), 'amount' : input('Amount (Leave empty for any) : '), 'dr_cr': input('Debit or Credit (Leave empty for any) : ')}
            if data['amount'] != '':
                try:
                    data['amount'] = float(data['amount'])
                except:
                    print("Amount has to be a number.")
                    sys.exit(1)
        
        if data['date'] != '':
            date = convert_Date(data['date'])
            if date == False:
                if not gui:
                    print("Invalid date")


        query = []
        for key, value in data.items():
            if value!= '':
                if key == 'amount':
                    query.append(f"{key} == {value}")
                else:
                    query.append(f"{key} == '{value}'")
        query =' & '.join(query)

        if query == '':
            os.chdir(os.pardir)
            return df
        
        results = df.query(query)
        if gui:
            os.chdir(os.pardir)
            return results

        print(f'{len(results)} Results\n----------------------------------')
        print(tab.tabulate(results, tablefmt='grid', headers=["Sr. no.", "ID", "Date", "Detail","Category" ,"Amount", "Dr/Cr", "Balance"]))

        os.chdir(os.pardir)
        return
        
def get_report(name, gui = False):
    items, spent, recieved, most_expensive, most_frequent, expensive_category, categories_amount, transactions, balance, weekly_analysis = stats(name, gui = True).values()
    categories_amount = {value: key for key, value in categories_amount.items()}
    budgets = get_budgets(name)
    
    report = f"In this month, {spent} has been spent and {recieved} has been recieved. "
    categories = ['Loan', 'Salary', 'Groceries', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous']
    if expensive_category[1] in ['Entertainment', 'Dining out']:
        report += f" The category in which most money is spent is {expensive_category[1]}. This spendage is out of control and has to be reduced. "
    elif expensive_category[1]  == 'Clothing' and expensive_category[0] > 150:
        report += f"{expensive_category[0]} is spent on just clothing. This also has to be reduced. "
    elif expensive_category[1] == 'Groceries' and (expensive_category[0]*100) / spent >=  70:
        report += f"Groceries are being spent on a high percentage of the total spending. This should be reduced as much as possible. "
    else:
        report += f"{expensive_category[1]} with a total of {expensive_category[0]} is the category with most money spent. Its suggested to reduce the spendage in this category. "
    
    if budgets != []:
        for budget in budgets:
            if budget[0] == 'overall' and spent > float(budget[2]):
                report += f"Your monthly budget was {budget[2]}. You have exceeded your budget by {spent - float(budget[2])}. Consider adjusting ypur spending habits. "
                continue
            elif budget[0] == 'overall' and spent <= float(budget[2]):
                report += f"Your monthly budget was {budget[2]}. You are within your budget. "
                continue
            try:
                category_spent = categories_amount[budget[1].title()]
            except KeyError:
                category_spent = 0
            if category_spent > float(budget[2]):
                report += f"Your monthly budget for {budget[1].title()} was {budget[2]}. You have exceeded your budget by {categories_amount[budget[1].title()] - float(budget[2])}. Consider adjusting ypur spending habits. "
            else:
                report += f"Your monthly budget for {budget[1].title()} was {budget[2]}. You are within your budget. "
            
    
    if float(balance) < 200:
        report += f"The balance is {balance}, which is very low. It is essential to maintain a balance above 200. "
    if gui:
        report1 = ""
        for i in range(len(report)):
            if i%66 == 0 and i != 0:
                if report[i].isalpha():
                    report1 += report[i] + '-\n'
                else:
                    report1 += report[i] + '\n'
            else:
                report1 += report[i]
        return report1
    print("Financial report of this month : \n", report)
    return 

def GUI():
    def close():
        plt.close('all')
        app.quit()
        app.destroy()

    app = CTk()
    app.geometry('1100x600')
    app.title('Life-Record')
    app.resizable(False, False)
    app.protocol("WM_DELETE_WINDOW", close)

    main = CTkFrame(app, width = 900, height = 600, corner_radius=0, border_color='#404040', border_width = 2)
    main.pack_propagate(False)
    main.place(x=200, y=0)

    global title
    title = CTkLabel(app, text = 'Log in', font = ('Georgia', 40), fg_color='#2b2b2b')
    title.pack(anchor = CENTER, pady = 10)

    global name
    global sign_out_btn
    name = None
    sign_out_btn = None

    def sign_out():
        global name
        name = None
        for widget in app.winfo_children():
            if widget._name == '!ctkbutton':
                widget.destroy()
        login()

    def login():
        global sign_out_btn
        global name
        for widget in main.winfo_children():
            if widget._name != '!ctklabel':
                widget.destroy()

        title.configure(text = 'Log in')
        CTkButton(main, text = '', width = 750, height = 450, fg_color = '#4d4b48', hover_color='#4d4b48').place(x=75, y=75)
        error = CTkLabel(main, text = '', font = ('georgia', 20), bg_color='#4d4b48')
        error.place(x=110, y= 240)
        CTkLabel(main, text = 'Username', font = ('georgia', 20), bg_color = '#4d4b48').place(x=100, y=100)
        CTkLabel(main, text = 'Password', font = ('georgia', 20),bg_color='#4d4b48').place(x=100, y=150)
        usr = CTkEntry(main, font = ('georgia', 20), bg_color='#4d4b48')
        usr.place(x=200, y=100)
        pwd = CTkEntry(main, show = '*' , font = ('georgia', 20), bg_color='#4d4b48')
        pwd.place(x=200, y=150)

        def done():
            global sign_out_btn
            global name
            res = authenticate(usr.get(), pwd.get(), gui = True)
            if res == True:
                name = usr.get()
                sign_out_btn = CTkButton(app, text = 'Sign out', fg_color = 'red', width = 50, hover_color = '#800000', command = sign_out).place(x=1035, y=5)
                dashboard()
            else:
                error.configure(text = res)

        action = CTkButton(main, text = 'Log in', font = ('georgia',20), command = done, bg_color='#4d4b48')
        action.place(x=350, y=150)
        action_switch = CTkButton(main, text = 'Dont have an account', font = ('georgia',15), command = lambda : signup(usr, pwd, action, action_switch, error), bg_color='#4d4b48')
        action_switch.place(x=350, y=100)

    def signup(usr, pwd, action, action_switch, error):

        title.configure(text = 'Sign Up')
        action_switch.configure(text = 'Already have an account.', command = login, bg_color='#4d4b48')
        CTkLabel(main, text = 'Balance', font = ('georgia',20), bg_color='#4d4b48').place(x=100, y=200)
        global bal
        bal = CTkEntry(main, font = ('georgia',20), bg_color='#4d4b48')
        bal.place(x=200, y=200)

        def done():
            global name
            global bal
            try:
                bal = float(bal.get())
            except:
                error.configure(text = 'Balance should be a number.')
                return

            if usr.get() and pwd.get():
                res = create_acc(usr.get(), pwd.get(), bal, gui = True)
                if res == True:
                    name = usr.get()
                    dashboard()
                else:
                    error.configure(text = res)

            else:
                error.configure(text = 'All fields are required.')

        action.configure(text = 'Sign up', command = done)

    login()

    menu = CTkFrame(app, width = 200, height = 600, corner_radius = 0, border_color='#404040', border_width = 2)
    menu.pack_propagate(False)
    menu.place(x=0, y=0)

    def gui_write():
        for widget in main.winfo_children():
            widget.destroy()

        frame = CTkScrollableFrame(main, width = 900, height = 520, border_width=1 , fg_color='#4D4B48', corner_radius = 0)
        frame.pack_propagate(False)
        frame.place(x=0, y=80)
        CTkLabel(frame, text = 'Date', font = ('georgia', 20)).grid(row = 2, column =1, sticky = W, padx = 5)
        date_entry = CTkEntry(frame,width = 200 , font = ('georgia', 20))
        date_entry.grid(row = 2, column = 2, sticky = W, padx = 10)

        CTkLabel(frame, text = 'Category', font = ('georgia', 20)).grid(row = 3, column =1, sticky = W, padx = 5, pady = 5)
        category_entry = CTkEntry(frame,width = 200 , font = ('georgia', 20))
        category_entry.grid(row = 3, column = 2, stick = W, padx = 10)

        CTkLabel(frame, text = 'Entry', font = ('georgia', 20)).grid(row = 4, column =1, sticky = W, padx = 5)
        entry_entry = CTkTextbox(frame, width = 770, height = 400, font = ('georgia', 20))
        entry_entry.grid(row = 4, column = 2, padx = 10, stick = N)

        def save():
            date = date_entry.get()
            category = category_entry.get()
            entry = entry_entry.get('1.0', END)
            if date == '' or category == '' or entry == '':
                error.configure(text = 'Please fill all fields.')
                return
            flag = write(name, date, category, entry, True)
            if flag != True:
                error.configure(text = flag)
            else:
                date_entry.delete(0, END)
                category_entry.delete(0, END)
                entry_entry.delete('1.0', END)
                error.configure(text = 'Entry added')

        CTkButton(frame, text = 'Save', font = ('georgia', 20), command = save).grid(row =5, column =2, sticky = E, padx=15, pady = 5)
        error = CTkLabel(frame, text = '', font = ('georgia', 20))
        error.place(x=100,y=480)
        
    def gui_set_budgets():
        for widget in main.winfo_children():
            widget.destroy()

        def add():
            if overall.get() == '' or not overall.get().isdigit():
                label.configure(text = 'Invalid overall budget.')

            budgets = [(category[0], float(category[1])) for category in [('groceries', groceries.get()), ('clothing', clothing.get()), ('dining out', dining.get()), ('education', education.get()), ('utilities', utilities.get()), ('transportatoin', transportation.get()), ('miscellaneous', misc.get())] if category[1].isdigit()]
            
            budgets.insert(0, ('overall', float(overall.get())))

            if sum([float(budget[1]) for budget in budgets if budget[0] != 'overall']) > float(overall.get()):
                label.configure(text = 'Total budget exceeds overall budget.', text_color = 'red')
                return
            set_budget(name,budgets = budgets, gui = True)
            label.configure(text = 'Budgets set successfully.')
        
        frame = CTkScrollableFrame(main, width = 896, height = 520, border_width=1 , fg_color='#4D4B48', corner_radius = 0)
        frame.pack_propagate(False)
        frame.place(x=2, y=80)

        CTkLabel(frame, text = 'Overall budget', font = ('georgia', 20)).grid(row = 1, column =1, sticky = W, padx = 5, pady = 5)
        overall = CTkEntry(frame,width = 200, font = ('georgia', 20))
        overall.grid(row = 1, column = 2, sticky = W, padx = 10)
        CTkLabel(frame, text = 'Categorical budgets', font = ('georgia', 20)).grid(row = 2, column =1, sticky = W)

        CTkLabel(frame, text = '   Groceries', font = ('georgia', 20)).grid(row = 3, column =1, sticky = W)
        groceries = CTkEntry(frame, font  = ('georgia', 20))
        groceries.grid(row = 3, column = 2)
        
        CTkLabel(frame, text = '   Clothing', font = ('georgia', 20)).grid(row = 4, column =1, sticky = W)
        clothing = CTkEntry(frame, font  = ('georgia', 20))
        clothing.grid(row = 4, column = 2)

        CTkLabel(frame, text = '   Dining out', font = ('georgia', 20)).grid(row = 5, column =1, sticky = W)
        dining = CTkEntry(frame, font  = ('georgia', 20))
        dining.grid(row = 5, column = 2)

        CTkLabel(frame, text = '   Utilities', font = ('georgia', 20)).grid(row = 6, column =1, sticky = W)
        utilities = CTkEntry(frame, font  = ('georgia', 20))
        utilities.grid(row = 6, column = 2)

        CTkLabel(frame, text = '   Education', font = ('georgia', 20)).grid(row = 7, column =1, sticky = W)
        education = CTkEntry(frame, font  = ('georgia', 20))
        education.grid(row = 7, column = 2)

        CTkLabel(frame, text = '   Transportation', font = ('georgia', 20)).grid(row = 8, column =1, sticky = W)
        transportation = CTkEntry(frame, font  = ('georgia', 20))
        transportation.grid(row = 8, column = 2)

        CTkLabel(frame, text = '   Miscellaneous', font = ('georgia', 20)).grid(row = 9, column =1, sticky = W)
        misc = CTkEntry(frame, font  = ('georgia', 20))
        misc.grid(row = 9, column = 2)

        label = CTkLabel(frame, text = 'Leave empty to skip a category', font = ('georgia', 20), text_color = '#1F6AA5')
        label.grid(row =10, column = 1, pady = 10)

        CTkButton(frame, text = 'Add', font = ('georgia',20), command = add).grid(row = 10, column = 2)

    def dashboard():
        global name
        global title
        if name == None:
            return

        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Dashboard')
        CTkButton(main, text = '', width = 750, height = 450, fg_color = '#4d4b48', hover_color='#4d4b48').place(x=75, y=75)

        CTkButton(main, text = '', height = 220, width = 230, hover_color='#1F6AA5', fg_color = '#1F6AA5', bg_color="#4d4b48").place(x = 175, y = 100)
        CTkButton(main, text = '', height = 220, width = 230, hover_color='#1F6AA5', fg_color = '#1F6AA5', bg_color="#4d4b48").place(x = 495, y = 100)

        CTkLabel(main, text = 'Entries', font = ('roboto', 30), bg_color = '#1F6AA5').place(x=505, y=115)
        entries = CTkLabel(main, text = len(get_info(name, 'date')), font = ('roboto', 30), bg_color = '#1F6AA5')
        entries.place(x=505, y=150)
        CTkButton(main, text = '+', font = ('roboto', 20), width = 28,  fg_color = '#1E5994', bg_color = '#1F6AA5', command = gui_write).place(x=690, y=103)
        
        CTkLabel(main, text = 'Balance', font = ('roboto', 30), bg_color = '#1F6AA5').place(x=185, y=115)
        os.chdir(name)
        with open('finance.csv', 'r') as f:
            reader = csv.DictReader(f)
            bal = [row['balance'] for row in reader][-1]
        os.chdir(os.pardir)
        CTkLabel(main, text = bal, font = ('roboto', 30), bg_color = '#1F6AA5').place(x=185, y=155)
        CTkButton(main, text = '+', font = ('roboto', 20), width = 28,  fg_color = '#1E5994', bg_color = '#1F6AA5', command = add_transaction).place(x=366, y=103)

        #Set budget
        budgets = get_budgets(name)
        if budgets != []:
            CTkLabel(main, text = 'Spent/Overall budget', font = ('roboto', 20), bg_color = '#1F6AA5').place(x=180,y=200)
            budget_label = CTkLabel(main, text = f"{stats(name, gui = True)['Money spent']}/{budgets[0][2]}", font = ('roboto', 20), bg_color = '#1F6AA5').place(x=190, y=225)
        CTkButton(main, text = 'Add budgets', font = ('roboto', 20), bg_color = '#1F6AA5', width = 70, fg_color='#005f5f', command = gui_set_budgets).place(x=185, y=260)

    def diary():
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Diary')

        frame = CTkScrollableFrame(main, width = 885, height = 515, fg_color='grey', corner_radius=0, border_width=1)

        frame.pack_propagate(False)
        frame.place(x=0, y = 95)

        def search():
            date = search_date.get()
            category = search_category.get()
            results = get_query_results(name, 'diary', data = {'date' : date, 'category' : category}, gui = True)
            for widget in frame.winfo_children():
                widget.destroy()
            CTkLabel(frame, text = 'Date   ', font = ('georgia', 17)).grid(row = 1, column = 1, padx = 5)
            CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 60)
            CTkLabel(frame, text = 'Entry', font = ('georgia', 17)).grid(row=1, column = 3)
            
            
            for i, row in enumerate(range(len(results)), start = 2):
                CTkLabel(frame, text = results.iloc[row,0], font = ('roboto', 15)).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = results.iloc[row,1], font = ('roboto', 15)).grid(row = i, column = 2, padx = 60)
                CTkButton(frame, text = 'Read', width = 100, height = 15, font = ('roboto', 15), command = functools.partial(gui_read, {'date' : results.iloc[row,0], 'category' : results.iloc[row, 1],  'entry' : results.iloc[row,2]})).grid(row = i, column = 3)
                CTkButton(frame, text = 'Delete', width = 2, fg_color = 'red', hover_color = "#800000", height = 15, font = ('roboto', 15), command = functools.partial(delete_entry, name, results.iloc[row,0], True)).grid(row = i, column = 4, padx = 10)


        CTkLabel(frame, text = 'Date   ', font = ('georgia', 17)).grid(row = 1, column = 1, padx = 5)
        CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 60)
        CTkLabel(frame, text = 'Entry', font = ('georgia', 17)).grid(row=1, column = 3)

        CTkLabel(frame, text = '').grid(row = 1, column = 1)
        search_frame = CTkFrame(main, width = 900, height = 33, fg_color='#63666A',corner_radius=0, border_width=1)
        search_frame.place(x=0, y=62)
        search_frame.pack_propagate(False)
        CTkLabel(search_frame, text = 'Date', font = ('georgia', 17), bg_color='#63666A').pack(side = LEFT, padx = (30,10))
        search_date = CTkEntry(search_frame, font = ('georgia', 17), bg_color='#63666A', width = 120)
        search_date.pack(side = LEFT)
        
        CTkLabel(search_frame, text = 'Category', font = ('georgia', 17), bg_color='#63666A').pack(side = LEFT, padx = (30, 10))
        search_category = CTkEntry(search_frame, font = ('georgia', 17), bg_color='#63666A', width = 120)
        search_category.pack(side = LEFT)

        CTkButton(search_frame, text = '+', font = ('roboto', 17), width = 28,  fg_color = '#1E5994', bg_color = '#63666A', command = gui_write).pack(side = RIGHT, padx = 5)
        search_btn = CTkButton(search_frame, text = 'Search 🔎', font = ('georgia',17), width = 50, command = search)
        search_btn.pack(side = RIGHT, padx = 10)


        def gui_read(row):
            for widget in main.winfo_children():
                widget.destroy()

            entry_frame = CTkTextbox(main, font = ('georgia', 17), corner_radius = 0, width = 896, height = 515, fg_color = '#1E5994')
            entry_frame.place(x=2, y = 85)
            entry = row['entry'].split('\\n')
            entry_frame.insert('0.0', row['date']+'\n'+row['category']+'\n'+'\n'+'\n'.join(entry))
            entry_frame.configure(state = 'disabled')

        os.chdir(name)
        with open('diary.csv', 'r') as db:
            reader = csv.DictReader(db)
            for i, row in enumerate(reader, start = 3):
                CTkLabel(frame, text = row['date'], font = ('roboto', 15)).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = row['category'], font = ('roboto', 15)).grid(row = i, column = 2, padx = 60)
                CTkButton(frame, text = 'Read', width = 100, height = 15, font = ('roboto', 15), command = functools.partial(gui_read, row)).grid(row = i, column = 3)
                CTkButton(frame, text = 'Delete', width = 2, fg_color = 'red', hover_color = "#800000", height = 15, font = ('roboto', 15), command = functools.partial(delete_entry, name, row['date'], True)).grid(row = i, column = 4, padx = 10)
        os.chdir(os.pardir)

    def add_transaction():
        for widget in main.winfo_children():
            widget.destroy()

        frame = CTkScrollableFrame(main, width = 896, height = 515, fg_color='#4D4B48', corner_radius=0)
        frame.pack_propagate(False)
        frame.place(x=2, y = 90)
        CTkLabel(frame, text = 'Date', font = ('georgia', 25)).grid(row=1, column =1, pady = 10)

        date = CTkEntry(frame, width = 200, font = ('georgia',25))
        date.grid(row = 1, column = 2)
        CTkLabel(frame, text = 'Detail', font = ('georgia', 25)).grid(row = 2, column = 1, padx = 5)
        detail = CTkEntry(frame, width = 200, font = ('georgia',25))
        detail.grid(row = 2, column = 2, padx = 10)
        CTkLabel(frame, text = 'Category', font = ('georgia', 25)).grid(row = 3, column = 1, padx = 5, pady = 10)
        category = CTkOptionMenu(frame, values = ['Groceries', 'Education', 'Salary', 'Loan', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous'], width = 200, font = ('georgia',25))
        category.grid(row = 3, column = 2, padx = 5)
        CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 25)).grid(row = 4, column = 1, padx = 5)
        dr_cr = CTkOptionMenu(frame, values = ['Debit', 'Credit'], width = 200, font=  ('georgia',25))
        dr_cr.grid(row = 4, column = 2, padx = 10)
        CTkLabel(frame, text = 'Amount', font = ('georgia', 25)).grid(row =5, column = 1, padx = 5)
        amount = CTkEntry(frame, width = 200, font = ('georgia', 25))
        amount.grid(row =5, column = 2, pady = 10)
        error = CTkLabel(frame, text = '', font = ('georgia', 25), text_color = '#6b150f')
        error.place(x=7, y= 220)

        def enter():
            if date.get() == '' or detail.get() == '' or amount == '':
                error.configure(text = 'All fields are required.')
                return
            if status:=finance(name, 'append', date.get(), detail.get(), category.get(), amount.get(), dr_cr.get().lower(), gui = True):
                if status != 'Transaction added.':
                    error.configure(text = status, text_color = 'red')
                    return
                error.configure(text = status, text_color = 'light blue')

        CTkButton(frame, text = 'Enter', font = ('georgia', 25), command = enter).grid(row =6, column = 5, sticky = E, padx = 10)
        
    def gui_finance():
        maxlen = 150
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Finance')

        frame = CTkScrollableFrame(main, width = 8960, height = 500, fg_color='grey', corner_radius=0, border_width=1, scrollbar_button_color='dark grey')
        frame.pack_propagate(False)
        frame.place(x=2, y = 95)

        for i in range(1,6):
            frame.grid_columnconfigure(i, minsize = maxlen)

        CTkLabel(frame, text = 'Date', font = ('georgia', 17)).grid(row = 1, column = 1, sticky = 'nsew')
        CTkLabel(frame, text = 'Detail', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 15)
        CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 3)
        CTkLabel(frame, text = 'Amount', font = ('georgia', 17)).grid(row = 1, column = 4, padx = 30)
        CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 17)).grid(row = 1, column =5)
        CTkLabel(frame, text = '', font = ('georgia', 17)).grid(row = 1, column = 6)

        def search():
            dr_cr = search_dr_cr.get()
            if dr_cr == 'Dr':
                dr_cr = 'debit'
            elif dr_cr == 'Cr':
                dr_cr = 'credit'
            else:
                dr_cr = ''
            data = {
                'date': search_date.get(),
                'detail': search_detail.get(),
                'category' : search_category.get(),
                'amount': search_amount.get(),
                'dr_cr': dr_cr,
                'balance': ''
            }

            results = get_query_results(name, domain='finance', data = data, gui = True)
            
            for widget in frame.winfo_children():
                widget.destroy()
            for i in range(1,6):
                frame.grid_columnconfigure(i, minsize = maxlen)

            CTkLabel(frame, text = 'Date', font = ('georgia', 17)).grid(row = 1, column = 1, sticky = 'nsew')
            CTkLabel(frame, text = 'Detail', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 15)
            CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 3)
            CTkLabel(frame, text = 'Amount', font = ('georgia', 17)).grid(row = 1, column = 4, padx = 30)
            CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 17)).grid(row = 1, column =5)
            CTkLabel(frame, text = '', font = ('georgia', 17)).grid(row = 1, column = 6)

            for i, row in enumerate(range(len(results)), start = 2):
                CTkLabel(frame, text = results.iloc[row,1], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = results.iloc[row,2], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 2, padx = 5)
                CTkLabel(frame, text = results.iloc[row,3], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 3, padx = 5)
                CTkLabel(frame, text = results.iloc[row,4], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 4, padx = 5)
                CTkLabel(frame, text = results.iloc[row,5], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 5, padx = 5)
                if str(results.iloc[row,0]) != '0':
                    CTkButton(frame, text = 'Delete', font = ('roboto', 15), width = 2, fg_color ='red', bg_color = 'grey', hover_color='#800000', command = functools.partial(delete_transaction, name, results.iloc[row,0], True)).grid(row = i, column = 6, sticky = 'w', pady = 2)
            CTkButton(frame, text = '+', font = ('roboto', 15), width = 28,  fg_color = '#1E5994', bg_color = 'grey', command = add_transaction).place(x=760, y=2)

        CTkLabel(frame, text = '').grid(row = 1, column = 1)
        search_frame = CTkFrame(main, width = 896, height = 33, fg_color='#63666A',corner_radius=0)
        search_frame.place(x=2, y=62)
        search_frame.pack_propagate(False)
        CTkLabel(search_frame, text = 'Date', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx  =(10,10))
        search_date = CTkEntry(search_frame, font = ('roboto', 16), width = 100, bg_color='#63666A')
        search_date.pack(side = LEFT, padx = (0,20))

        CTkLabel(search_frame, text = 'Detail', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_detail = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 100)
        search_detail.pack(side = LEFT, padx = (0,20))

        CTkLabel(search_frame, text = 'Category', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_category = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 100)
        search_category.pack(side = LEFT, padx = (0,10))
        CTkLabel(search_frame, text = 'Amount', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_amount = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 50)
        search_amount.pack(side = LEFT, padx = (0,20))

        search_dr_cr = CTkOptionMenu(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 50,values=['Any', 'Dr', 'Cr'])
        search_dr_cr.pack(side = LEFT, padx = (0,10))
        search_btn = CTkButton(search_frame, text = 'Search🔎', font = ('georgia',17), width = 50, command = search)
        search_btn.pack(side = RIGHT, padx = (0,10))

        CTkButton(frame, text = '+', font = ('roboto', 15), width = 28,  fg_color = '#1E5994', bg_color = 'grey', command = add_transaction).place(x=860, y=2)
        frame.grid_columnconfigure(6, minsize = 2)
        os.chdir(name)
        with open('finance.csv', 'r') as db:
            reader = csv.DictReader(db)
            for i, row in enumerate(reader, start = 2):
                CTkLabel(frame, text = row['date'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = row['detail'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 2, padx = 5)
                CTkLabel(frame, text = row['category'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 3, padx = 5)
                CTkLabel(frame, text = row['amount'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 4, padx = 5)
                CTkLabel(frame, text = row['dr_cr'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 5, padx = 5)
                if str(row['id']) != '0':
                    CTkButton(frame, text = 'Delete', font = ('roboto', 15), width = 2, fg_color = 'red', bg_color = 'grey', hover_color='#800000', command = functools.partial(delete_transaction, name, row['id'], True)).grid(row = i, column = 6, sticky = 'w', pady =2)
        os.chdir(os.pardir)

    def gui_del_acc(name):
        if name != None:
            del_acc(name)
            name = None
            login()

    def gui_stats():
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Statistics')

        data = stats(name, gui = True)

        
        frame = CTkScrollableFrame(main, width = 876, height =515 ,fg_color='grey')
        frame.pack_propagate(False)
        frame.place(x=2, y=85)

        if type(data) == str:
            CTkLabel(frame, text = data, font = ('roboto', 15)).grid(row = 1, column =1)
        else:
            fig, ax = plt.subplots(figsize = (5,5))
            fig.patch.set_color('grey')
            for text in ax.texts:
                text.set_fontsize(5)
                text.set_position([text.get_position()[0], text.get_position()[1] - 0.15])
            wedges, texts, autotexts = ax.pie(data["Categories and amount spent"].keys(), labels = data['Categories and amount spent'].values(), startangle=90, autopct= '%1.1f%%', colors = ["#FF7F50", "#FFD700", "#87CEFA", "#32CD32", "#FF69B4", "#00CED1", "#EE82EE", "#FFA500", "#7FFF00", "#FF4500", "#ADFF2F"])
            plt.setp(wedges, edgecolor='black', linewidth=1.5)
            ax.axis('equal')
            plt.tight_layout()


            fig1, ax1 = plt.subplots(figsize = (5,5))
            fig1.patch.set_color('grey')
            ax1.bar(range(1, 6), list(data['weekly analysis'].values())[0:5], tick_label=['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Projected Week 5'])
            ax1.set_xlabel('Week')
            ax1.set_ylabel('Spendage in the week')
            ax1.set_title('Weekly spending')
            plt.xticks(rotation = 10)
            plt.tight_layout()

            CTkLabel(frame, text = "Month", font = ("Roboto", 20)).grid(row = 1, column = 1, sticky = W)
            CTkLabel(frame, text = datetime.now().strftime("%B"), font = ("Roboto", 20)).grid(row = 1, column = 2, sticky=W)
            CTkLabel(frame, text = "Money spent", font = ("Roboto", 20)).grid(row = 2, column = 1, sticky = W)
            CTkLabel(frame, text = data['Money spent'], font = ("Roboto", 20)).grid(row = 2, column = 2, sticky = W)
            CTkLabel(frame, text = "Money recieved (Loans excluded)", font = ("Roboto", 20)).grid(row = 3, column = 1, sticky = W)

            CTkLabel(frame, text = data['Money recieved'], font = ("Roboto", 20)).grid(row = 3, column = 2, sticky = W)
            CTkLabel(frame, text = '\n', font = ("Roboto", 20)).grid(row = 4, column = 1, sticky = W)

            #Adjust all rows/columns
            CTkLabel(frame, text = "Weekly Stats", font = ("Roboto", 20)).grid(row = 5, column = 1, sticky = W)
            CTkLabel(frame, text = "  Week with highest spendage", font = ("Roboto", 20)).grid(row = 6, column = 1, sticky = W)
            CTkLabel(frame, text = str(data['weekly analysis']['Week with most spendage'][1]) + ' in ' + data['weekly analysis']['Week with most spendage'][0], font = ("Roboto", 20)).grid(row = 6, column = 2, sticky = W, padx = 5)
            CTkLabel(frame, text = "  Week with least spendage including\nonly non-zero and full weeks\n", font = ("Roboto", 20)).grid(row = 7, column = 1, sticky = W)
            CTkLabel(frame, text = str(data['weekly analysis']['Week with least spendage'][1]) + ' in ' + data['weekly analysis']['Week with least spendage'][0], font = ("Roboto", 20)).grid(row = 7, column = 2, sticky = W, padx = 5)
            CTkLabel(frame, text = '  Average weekly spendage', font = ("Roboto", 20)).grid(row = 8, column = 1, sticky = W)
            CTkLabel(frame, text = data['weekly analysis']['average'], font = ("Roboto", 20)).grid(row = 8, column = 2, sticky = W)


            CTkLabel(frame, text = "", font = ("Roboto", 20)).grid(row = 9, column = 1, sticky = W)
            CTkLabel(frame, text = "\nCategory with most spending", font = ("Roboto", 20)).grid(row = 10, column = 1, sticky = W)
            CTkLabel(frame, text = "  Category", font = ("Roboto", 20)).grid(row = 11, column = 1, sticky = W)
            CTkLabel(frame, text = data["Category with highest spending"][1], font = ("Roboto", 20)).grid(row = 11, column = 2, sticky = W)
            CTkLabel(frame, text = "  Amount", font = ("Roboto", 20)).grid(row = 12, column = 1, sticky = W)
            CTkLabel(frame, text = data["Category with highest spending"][0], font = ("Roboto", 20)).grid(row = 12, column = 2, sticky = W)
            
            CTkLabel(frame, text = '').grid(row = 12,column = 1)

            
            weekly_spendage_bar_graph = StatCanvas(fig1, master=frame)
            weekly_spendage_bar_graph.draw()
            weekly_spendage_bar_graph.get_tk_widget().place(x=770,y=0)
            category_pie_chart = StatCanvas(fig, master=frame)
            category_pie_chart.draw()
            category_pie_chart.get_tk_widget().place(x=740,y=490)

            CTkLabel(frame, text = "Most expensive item", font = ("Roboto", 20)).grid(row = 14, column = 1, sticky = W)
            CTkLabel(frame, text = f"{data["Most expensive item"][1]} for {data["Most expensive item"][0]}", font = ("Roboto", 20)).grid(row = 14, column = 2)
            CTkLabel(frame, text = "\nNumber of transactions", font = ("Roboto", 20)).grid(row = 15, column = 1, sticky = W)
            CTkLabel(frame, text = '\n'+str(data['Number of transactions']), font = ("Roboto", 20)).grid(row = 15, column = 2)

            report =  get_report(name, gui = True)
            CTkLabel(frame, text = '\n\n\n').grid(row = 16,column = 1)
            CTkLabel(frame, text = 'Financial report', font = ("Roboto", 20)).grid(row = 17,column = 1, sticky = W)
            
            CTkLabel(frame, text = report, font = ('Roboto', 20)).place(x=0, y=610)
            CTkLabel(frame, text = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n').grid(row = 18,column = 1)

    CTkLabel(menu, text = 'Menu', font = ('Georgia', 35)).pack(anchor = CENTER, pady = 10)

    dash_btn = CTkButton(menu, text = 'Dashboard', width = 120, height = 40,font = ('georgia',20), command = dashboard)
    dash_btn.pack(anchor = CENTER, pady = 30)

    diary_btn = CTkButton(menu, text = 'Diary', width = 120, height = 40, font = ('georgia',20), command = diary)
    diary_btn.pack(anchor = CENTER)

    finance_btn = CTkButton(menu, text = 'Finance', width = 120, height = 40, font = ('georgia',20), command = gui_finance)
    finance_btn.pack(anchor = CENTER, pady = 30)

    stats_btn = CTkButton(menu, text = 'Stats', width = 120, height = 40, font = ('georgia',20), command = gui_stats)
    stats_btn.pack(anchor = CENTER)

    del_acc_btn = CTkButton(menu, text = 'Delete Account', fg_color = 'red', hover_color='#701010', width = 100, font = ('georgia',15), command = lambda : gui_del_acc(name))
    del_acc_btn.place(x=5, y=565)

    app.mainloop()

if __name__ == '__main__':
    main()
