import sqlite3

# Add to list
def AddList(tbl_name, id, type, details, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute('INSERT INTO {} (id, type, details, amount) VALUES (?, ?, ?, ?)'.format(tbl_name), (id, type, details, amount))
    con.commit()
    
    cur.close()
    con.close()

# Add budget
def AddBudgetMoney(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT budget_money FROM overview WHERE uname = ?", [uname])
    budget_money = float(cur.fetchone()[0])

    budget_money = budget_money + amount
    
    cur.execute("UPDATE overview SET budget_money = ? WHERE uname = ?", (budget_money, uname))
    con.commit()

    cur.close()
    con.close()

# Deduct budget
def DeductBudgetMoney(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT budget_money FROM overview WHERE uname = ?", [uname])
    budget_money = float(cur.fetchone()[0])

    budget_money = budget_money - amount

    cur.execute("UPDATE overview SET budget_money = ? WHERE uname = ?", (budget_money, uname))
    con.commit()

    cur.close()
    con.close()

# Add budget transaction
def TransactionBudget(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT budget_trans FROM overview WHERE uname = ?", [uname])
    budget_trans = int(cur.fetchone()[0])

    budget_trans = budget_trans + 1

    cur.execute("SELECT budget_trans_total FROM overview WHERE uname = ?", [uname])
    budget_trans_total = float(cur.fetchone()[0])

    budget_trans_total = budget_trans_total + amount

    cur.execute("UPDATE overview SET budget_trans = ?, budget_trans_total = ? WHERE uname = ?", (budget_trans, budget_trans_total, uname))
    con.commit()

    cur.close()
    con.close()

# Add savings
def AddSavingsMoney(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT savings_money FROM overview WHERE uname = ?", [uname])
    savings_money = float(cur.fetchone()[0])

    savings_money = savings_money + amount
    
    cur.execute("UPDATE overview SET savings_money = ? WHERE uname = ?", (savings_money, uname))
    con.commit()

    cur.close()
    con.close()
    
# Deduct savings
def DeductSavingsMoney(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT savings_money FROM overview WHERE uname = ?", [uname])
    savings_money = float(cur.fetchone()[0])

    savings_money = savings_money - amount

    cur.execute("UPDATE overview SET savings_money = ? WHERE uname = ?", (savings_money, uname))
    con.commit()

    cur.close()
    con.close()

# Add savings transaction
def TransactionSavings(uname, amount):
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    cur.execute("SELECT savings_trans FROM overview WHERE uname = ?", [uname])
    savings_trans = int(cur.fetchone()[0])

    savings_trans = savings_trans + 1

    cur.execute("SELECT savings_trans_total FROM overview WHERE uname = ?", [uname])
    savings_trans_total = float(cur.fetchone()[0])

    savings_trans_total = savings_trans_total + amount

    cur.execute("UPDATE overview SET savings_trans = ?, savings_trans_total = ? WHERE uname = ?", (savings_trans, savings_trans_total, uname))
    con.commit()

    cur.close()
    con.close()