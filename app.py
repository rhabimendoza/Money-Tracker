# Import libraries
from flask import Flask, request, render_template, redirect, flash, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from email.message import EmailMessage
from cryptography.fernet import Fernet
from flask_session import Session
from functools import wraps
import sqlite3
import smtplib
import jinja2
import string
import random
import ssl
import re

# Import functions from another file
from priv_key import *
from mt_functions import *

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Use jinja
jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("template"))

# Make app
app = Flask(__name__)

# Set secret key
app.secret_key = "76137hsdhjg939"

# Ensure templates are auto reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create key
key = "5fy9uKa_s7PU9V8evkon14Ik98G9szhaU5gbQwF-fhE="
cryp = Fernet(key)

# Create pattern
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Define after request
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Define login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    # Clear session
    session.clear()

    # To do if post
    if request.method == "POST":

        # Get typed username and password
        uname = str(request.form.get("li_uname"))
        pword = str(request.form.get("li_pword"))

        # Strip username and password
        uname = uname.strip(' ')
        pword = pword.strip(' ')

        # Check if username or password are invalid
        if len(uname) == 0 or len(pword) == 0:
            flash("Complete details!", "danger")
        elif len(uname) < 8 or len(pword) < 8:
            flash("Username and password should contain atleast 8 characters!", "danger")
        elif not uname.isalnum() or not pword.isalnum():
            flash("Username and passwords can only contain letters and numbers!", "danger")

        # Valid username and password
        else: 

            # Connect to database
            con = sqlite3.connect("moneytracker.db")
            cur = con.cursor()

            # Get all usernames from table
            unames = cur.execute("SELECT uname FROM users")
        
            # Create a checker variable
            check = 0
        
            # Check if username exist in database
            for result in unames:

                # Store username in variable
                a = str(result[0])

                # Check if username is equal to variable
                if uname == a:

                    # Change check to 1
                    check = 1

            # Username does not exist
            if check == 0:

                # Display flash
                flash("Username does not exist!", "danger")

                # Close cursor and connection
                cur.close()
                con.close()

            # Username exist
            else:

                # Get password from database using username
                cur.execute("SELECT pword FROM users WHERE uname = ?", [uname])
                enPword = str(cur.fetchone()[0]) 
                
                # Password is correct
                if(check_password_hash(enPword, pword)):
                    
                    # Check if admin
                    if uname == "1mt1admin1":

                        # Add usernmae to session, close cursor and connection, and redirect to home
                        session["user_id"] = uname
                        cur.close()
                        con.close()
                        return redirect("/admin")
                    
                    # User
                    else:
                        
                        # Add username to session, close cursor and connection, and redirect to home
                        session["user_id"] = uname
                        cur.close()
                        con.close()
                        return redirect("/")

                # Password is incorrect
                else: 

                    # Display flash
                    flash("Username and password did not match!", "danger")

                    # Close cursor and connection
                    cur.close()
                    con.close()
        
    # Render login page
    return render_template("login.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # To do if post
    if request.method == "POST":

        # Get typed information
        uname = str(request.form.get("su_uname"))
        pword = str(request.form.get("su_pword"))
        email = str(request.form.get("su_email"))
        fname = str(request.form.get("su_fname"))
        lname = str(request.form.get("su_lname"))

        # Strip typed information
        uname = uname.strip(' ')
        pword = pword.strip(' ')
        email = email.strip(' ')
        fname = fname.strip(' ')
        lname = lname.strip(' ')

        # Check if information are invalid
        if len(uname) == 0 or len(pword) == 0 or len(email) == 0 or len(fname) == 0 or len(lname) == 0:
            flash("Complete details!", "danger")
        elif len(fname) < 3 or len(lname) < 3:
            flash("First name and last name should contain atleast 3 characters!", "danger")
        elif len(email) < 11:
            flash("Invalid email!", "danger")
        elif len(uname) < 8 or len(pword) < 8:
            flash("Username and password should contain atleast 8 characters!", "danger")    
        elif not all(a.isalpha() or a.isspace() for a in fname) or not all(b.isalpha() or b.isspace() for b in lname):
            flash("First name and last name can only contain letters and spaces!", "danger")
        elif not(re.fullmatch(regex, email)):
            flash("Invalid email!", "danger")
        elif not uname.isalnum() or not pword.isalnum():
            flash("Username and passwords can only contain letters and numbers!", "danger")
        
        # Valid information
        else:

            # Connect to database
            con = sqlite3.connect("moneytracker.db")
            cur = con.cursor()

            # Get all email from table
            emails = cur.execute("SELECT email FROM users")

            # Create a checker variable
            check = 0
            
            # Check if email is already in used
            for result in emails:

                # Store to variable
                a = str(result[0])

                # Check if email is same from database
                if email == a:
                    
                    # Change check to 1
                    check = 1

            # Email is already used
            if check == 1:

                # Display flash
                flash("Email is already used by another account!", "danger")

                # Close cursor and connection
                cur.close()
                con.close()

            # Email is not yet used
            else:

                # Try creating account
                try:

                    # Encrypt password
                    pword = generate_password_hash(pword)

                    # Add in users
                    cur.execute("INSERT INTO users (uname, pword, email, fname, lname) VALUES (?, ?, ?, ?, ?)", (uname, pword, email, fname, lname))

                    # Add in overview
                    cur.execute("INSERT INTO overview (uname, budget_trans, budget_trans_total, budget_money, savings_trans, savings_trans_total, savings_money) VALUES (?, ?, ?, ?, ?, ?, ?)",(uname, 0, 0, 0, 0, 0, 0))

                    # Create own table for budget
                    tbl_name = "budget_" + uname
                    query = 'CREATE TABLE {} (id TEXT, type TEXT, details TEXT, amount REAL)'.format(tbl_name)
                    cur.execute(query)

                    # Create own table for savings
                    tbl_name = "savings_" + uname
                    query = 'CREATE TABLE {} (id TEXT, type TEXT, details TEXT, amount REAL)'.format(tbl_name)
                    cur.execute(query)    

                    # Save executes            
                    con.commit()

                    # Display flash
                    flash("Account successfully created!", "success")
                    
                    # Close cursor and connection
                    cur.close()
                    con.close()
                
                # Username already exist in database
                except:
                    
                    # Display flash
                    flash("Username is already used by another account!", "danger")

                    # Close cursor and connection
                    cur.close()
                    con.close()

    # Render signup page
    return render_template("signup.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Reset page
@app.route("/reset", methods=["GET", "POST"])
def reset():
    
    # To do if post
    if request.method == "POST":
    
        # Get typed username
        uname = str(request.form.get("rp_uname"))

        # Strip uname
        uname = uname.strip(' ')

        # Check if username is invalid
        if len(uname) == 0:
            flash("Complete details!", "danger")
        elif len(uname) < 8:
            flash("Username should contain atleast 8 characters!", "danger")
        elif not uname.isalnum():
            flash("Username can only contain letters and numbers!", "danger")
        
        # Valid username
        else:

            # Connect to database
            con = sqlite3.connect("moneytracker.db")
            cur = con.cursor()

            # Get all usernames from table
            unames = cur.execute("SELECT uname FROM users")

            # Create a checker variable
            check = 0

            # Check if username is used by an account
            for result in unames:

                # Store username to a variable
                a = str(result[0])

                # Check if username is equal to the variable
                if uname == a:

                    # Change check to 1
                    check = 1

            # Username does not exist
            if check == 0:

                # Display flash
                flash("Username does not exist!", "danger")

                # Close cursor and connection
                cur.close()
                con.close()

            # Username exist
            else:
                
                # Generate random password
                charSource = string.ascii_lowercase + string.ascii_uppercase + string.digits  
                newPass = ( ''.join(random.choice(charSource) for ctr in range(10)))

                # GET email from database using username
                cur.execute("SELECT email FROM users WHERE uname = ?", [uname])
                userEmail = str(cur.fetchone()[0])

                # Get info of sender
                sender = priv_info.acc_mail
                senPass = priv_info.acc_pword

                # Create contents of message
                subject = "NEW PASSWORD | MONEYTRACKER"
                body = "Log in to your account with this new password: " + newPass

                # Setup message to send
                emailMessage = EmailMessage()
                emailMessage["From"] = sender
                emailMessage["To"] = userEmail
                emailMessage["Subject"] = subject
                emailMessage.set_content(body)

                # Send new password to user
                context = ssl.create_default_context()           
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:

                    # Login sender and send message
                    smtp.login(sender, senPass)
                    smtp.sendmail(sender, userEmail, emailMessage.as_string())
                
                # Encrypt password
                newPass = generate_password_hash(newPass)

                # Update new password
                cur.execute("UPDATE users SET pword = ? WHERE uname = ?", (newPass, uname))
                flash("New password sent to email connected to your account!", "success")
                con.commit()  
                  
                # Close cursor and connection
                cur.close()
                con.close()

    # Render reset page
    return render_template("reset.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Go to overview page
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # Get username of current user
    uname = session["user_id"]

    # Create connection to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()
    
    # To do if post
    if request.method == "POST":

        # Budget reset is clicked
        if request.form["btnover"] == "btn_budget": 

            # Update budget transaction and budget transaction total to 0
            cur.execute("UPDATE overview SET budget_trans = 0, budget_trans_total = 0 WHERE uname = ?", [uname])
            con.commit()

            # Display flash
            flash("Reset success!", "success")

        # Savings reset is clicked
        elif request.form["btnover"] == "btn_savings":

            # Update savings trasaction and savings transaction total to 0
            cur.execute("UPDATE overview SET savings_trans = 0, savings_trans_total = 0 WHERE uname = ?", [uname])
            con.commit()

            # Display flash
            flash("Reset success!", "success")

    # Get data in overview
    data = cur.execute("SELECT * FROM overview WHERE uname = ?", [uname])

    # Store data in variables
    for row in data:
        bt_num = int(row[1])
        bd_num = float(row[2])
        bud_mon = float(row[3])
        ft_num = int(row[4])
        fa_num = float(row[5])
        fut_mon = float(row[6])
    
    # Close cursor and database
    cur.close()
    con.close()
    
    # Render overview page
    return render_template("overview.html", uname=uname, bt_num=bt_num, bd_num=bd_num, ft_num=ft_num, fa_num=fa_num, fut_mon=fut_mon, bud_mon=bud_mon)  

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Go to budget page
@app.route("/budget")
@login_required
def budget():

    # Get username and table name
    uname = session["user_id"]
    tbl_name = "budget_" + uname

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Get current budget
    cur.execute("SELECT budget_money FROM overview WHERE uname = ?", [uname])
    budget_money = float(cur.fetchone()[0]) 

    # Get all data from budget table
    data = cur.execute('SELECT * FROM "{}"'.format(tbl_name))   

    # Render budget page
    return render_template("budget.html", data=data, budget_money=budget_money)
 
# Add activity in budget
@app.route("/budget_activity", methods=["POST"])
@login_required
def budget_activity():

    # To do if post
    if request.method == "POST":

        # Get username and table name
        uname = session["user_id"]
        tbl_name = "budget_" + uname

        # Connect to database
        con = sqlite3.connect("moneytracker.db")
        cur = con.cursor()

        # Get current budget
        cur.execute("SELECT budget_money FROM overview WHERE uname = ?", [uname])
        budget_money = float(cur.fetchone()[0])

        # Get selected activity
        act = str(request.form.get("activities"))

        # Generate id
        charSource = string.ascii_lowercase + string.ascii_uppercase + string.digits
        id = str(( ''.join(random.choice(charSource) for ctr in range(12))))
        
        # Get typed details and amount
        details = str(request.form["details"])
        amountstr = str(request.form["amount"]) 

        # Strip input
        details = details.strip(' ')
        amountstr = amountstr.strip(' ')
        
        # Check if amount is a float
        try:
            float(amountstr)
            inv = 0
        except ValueError:
            inv = 1

        # Check if details is safe from injection
        chk = 0
        for a in details:
            b = ord(a)

            if b == 34 or b == 39:
                chk = 1

        # Check if details and amount are valid
        if len(details) == 0:
            flash("Details cannot be blank!", "danger")
        elif len(amountstr) == 0:
            flash("Amount cannot be blank!", "danger")
        elif inv == 1:
            flash("Amount should be numeric!", "danger")
        elif float(amountstr) < 0:
            flash("Negative amount not allowed!", "danger")
        elif chk == 1:
            flash("Error!", "danger")     

        # Details and amount are valid           
        else:
            
            # Get amount in float
            amount = float(amountstr)

            # Add budget
            if act == "add":
                
                # Create type
                type = "Added budget"

                # Call functions
                AddList(tbl_name, id, type, details, amount)
                AddBudgetMoney(uname, amount)
                flash("Budget added!", "success")
            
            # Log expense
            elif act == "log":

                # Create type
                type = "Logged expense"
     
                # Check if budget is enough
                if budget_money >= amount:
                    
                    # Call functions
                    AddList(tbl_name, id, type, details, amount)
                    DeductBudgetMoney(uname, amount)
                    TransactionBudget(uname, amount)
                    flash("Expense logged!", "success")
                
                # Budget not enough
                else:

                    # Display flash
                    flash("Budget not enough!", "danger")

            # Transfer to savings
            elif act == "transfer":

                # Create type
                type = "Transferred to savings"


                # Check if budget is enough
                if budget_money >= amount:

                    # Call functions
                    AddList(tbl_name, id, type, details, amount)
                    DeductBudgetMoney(uname, amount)
                    AddSavingsMoney(uname, amount)
                    TransactionBudget(uname, amount)
                    TransactionSavings(uname, amount)
                    flash("Budget transferred!", "success")

                    # Add in savings history
                    tbl_name = "savings_" + uname
                    type = "Transferred from budget"
                    AddList(tbl_name, id, type, details, amount)
                    
                # Budget not enough
                else:

                    # Display flash       
                    flash("Budget not enough!", "danger")

            # Delete budget
            elif act == "delete":
                
                # Create type
                type = "Deleted budget"
               
                # Check if budget is enough
                if budget_money >= amount:
                    
                    # Call functions
                    AddList(tbl_name, id, type, details, amount)
                    DeductBudgetMoney(uname, amount)
                    TransactionBudget(uname, amount)
                    flash("Budget deleted!", "success")

                # Budget not enough
                else:

                    # Display flash
                    flash("Budget not enough!", "danger")

    # Close cursor and connection
    cur.close()
    con.close()
    
    # Redirect to budget page
    return redirect(url_for("budget"))
 
# Delete history in budget
@app.route("/budget_delete/<string:id>", methods=["GET", "POST"])
@login_required
def budget_delete(id):

    # Get username and table name
    uname = session["user_id"]
    tbl_name = "budget_" + uname

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Delete clicked row
    cur.execute('DELETE FROM "{}" WHERE id = ?'.format(tbl_name), ([id]))
    con.commit()

    # Display flash
    flash("History deleted!", "success")

    # Close cursor and connection
    cur.close()
    con.close()

    # Redirect to budget page
    return redirect(url_for("budget"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Go to savings page
@app.route("/savings")
@login_required
def savings():

    # Get username and table name
    uname = session["user_id"]
    tbl_name = "savings_" + uname

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()
    
    # Get current savings
    cur.execute("SELECT savings_money FROM overview WHERE uname = ?", [uname])
    savings_money = float(cur.fetchone()[0])

    # Get all data from savings table
    data = cur.execute('SELECT * FROM "{}"'.format(tbl_name))

    # Render savings page
    return render_template("savings.html", data=data, savings_money=savings_money)
 
# Add activity in savings
@app.route("/savings_activity", methods=["POST"])
@login_required
def savings_activity():

    # To do if post
    if request.method == "POST":

        # Get username and table name
        uname = session["user_id"]
        tbl_name = "savings_" + uname

        # Connect to database
        con = sqlite3.connect("moneytracker.db")
        cur = con.cursor()

        # Get current savings
        cur.execute("SELECT savings_money FROM overview WHERE uname = ?", [uname])
        savings_money = float(cur.fetchone()[0])

        # Get selected activity
        act = str(request.form.get("activities"))

        # Generate id
        charSource = string.ascii_lowercase + string.ascii_uppercase + string.digits
        id = str(( ''.join(random.choice(charSource) for ctr in range(12))))

        # Get typed details and amount
        details = str(request.form["details"])
        amountstr = str(request.form["amount"])

        # Strip input
        details = details.strip(' ')
        amountstr = amountstr.strip(' ')
        
        # Check if amount is a float
        try:
            float(amountstr)
            inv = 0
        except ValueError:
            inv = 1

        # Check if details is safe from injection
        chk = 0
        for a in details:
            b = ord(a)

            if b == 34 or b == 39:
                chk = 1

        # Check if details and amount are valid
        if len(details) == 0:
            flash("Details cannot be blank!", "danger")
        elif len(amountstr) == 0:
            flash("Amount cannot be blank!", "danger")
        elif inv == 1:
            flash("Amount should be numeric!", "danger")
        elif float(amountstr) < 0:
            flash("Negative amount not allowed!", "danger")
        elif chk == 1:
            flash("Error!", "danger")

        # Details and amount are valid
        else:          
            
            # Get amount in float
            amount = float(amountstr)

            # Add savings
            if act == "add":
                
                # Create type
                type = "Added to savings"

                # Call functions
                AddList(tbl_name, id, type, details, amount)
                AddSavingsMoney(uname, amount)
                TransactionSavings(uname, amount)
                flash("Savings added!", "success")

            # Transfer to budget
            elif act == "transfer":

                # Create type
                type = "Transferred to budget"

                # Check if savings is enough
                if savings_money >= amount:

                    # Call functions
                    AddList(tbl_name, id, type, details, amount)
                    DeductSavingsMoney(uname, amount)
                    AddBudgetMoney(uname, amount)
                    flash("Savings transferred!", "success")

                    # Add in budget history
                    tbl_name = "budget_" + uname
                    type = "Transferred from savings"
                    AddList(tbl_name, id, type, details, amount)
                    
                # Savings not enough
                else:

                    # Display flash
                    flash("Savings not enough!", "danger")

            # Delete savings
            elif act == "delete":
                
                # Create type
                type = "Deleted savings"

                # Check if savings is enough
                if savings_money >= amount:
                    
                    # Call functions
                    AddList(tbl_name, id, type, details, amount)
                    DeductSavingsMoney(uname, amount)
                    flash("Savings deleted!", "success")
                
                # Savings not enough
                else:

                    # Display flash
                    flash("Savings not enough!", "danger")

    # Close cursor and connection
    cur.close()
    con.close()

    # Redirect to savings page
    return redirect(url_for("savings"))

# Delete history in savings
@app.route("/savings_delete/<string:id>", methods=["GET", "POST"])
@login_required
def savings_delete(id):

    # Get username and table name
    uname = session["user_id"]
    tbl_name = "savings_" + uname

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Delete clicked row
    cur.execute('DELETE FROM "{}" WHERE id = ?'.format(tbl_name), ([id]))
    con.commit()

    # Display flash
    flash("History deleted!", "success")

    # Close cursor and connection
    cur.close()
    con.close()

    # Redirect to savings page
    return redirect(url_for("savings"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Go to account page
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    # Get username
    uname = session["user_id"]        
    
    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()
   
    # To do if post
    if request.method == "POST":  

        # Get all user info
        info = cur.execute("SELECT * FROM users WHERE uname = ?", [uname])

        # Store all user info
        for row in info: 
            fname = str(row[3])
            lname = str(row[4])
            email = str(row[2])
            uname = str(row[0])
            pword = str(row[1])

        # Update info is clicked
        if request.form["btnacc"] == "upd_info":

            # Store all input in variable
            ffname = str(request.form.get("fname"))
            flname = str(request.form.get("lname"))
            femail = str(request.form.get("email"))
            funame = str(request.form.get("uname"))

            # Strip all input
            ffname = ffname.strip(' ')
            flname = flname.strip(' ')
            femail = femail.strip(' ')
            funame = funame.strip(' ')

            # Check if all inputs are valid
            if ffname == fname and flname == lname and femail == email and funame == uname:
                flash("No changes made!", "danger")
            elif len(ffname) == 0 or len(flname) == 0 or len(femail) == 0 or len(funame) == 0:
                flash("Complete details!", "danger")
            elif len(ffname) < 3 or len(flname) < 3:
                flash("First name and last name should contain atleast 3 characters!", "danger")
            elif len(femail) < 11:
                flash("Invalid email!", "danger")
            elif len(funame) < 8:
                flash("Username should contain atleast 8 characters!", "danger")                  
            elif not all(a.isalpha() or a.isspace() for a in ffname) or not all(b.isalpha() or b.isspace() for b in flname):
                flash("First name and last name can only contain letters and spaces!", "danger")
            elif not(re.fullmatch(regex, femail)):
                flash("Invalid email!", "danger")
            elif not funame.isalnum():
                flash("Username can only contain letters and numbers!", "danger")

            # Inputs are valid
            else:

                # Create a checker variable
                check = 0

                # Get all email from database
                emails = cur.execute("SELECT email FROM users")
                
                # Check if email is already used by another account
                for result in emails:
                    
                    # Store email to a variable
                    a = str(result[0])

                    # Check if email is already in database
                    if a != email and a == femail:

                        # Change check to 1
                        check = 1
                       
                # Email is already used
                if check == 1:
                    
                    # Display flash
                    flash("Email is already used by another account!", "danger")

                # Email is not used
                else:
                                
                    # Get all username from database
                    unames = cur.execute("SELECT uname FROM users")
                    
                    # Check if username is already used by another account
                    for result in unames:
                        
                        # Store username to a variable
                        a = str(result[0])

                        # Check if username is already in database
                        if a != uname and a == funame:
                            
                            # Change check to 1
                            check = 1
                    
                    # Username is already used
                    if check == 1:

                        # Display flash
                        flash("Username is already used by another account!", "danger")
                                     
                    # Username is not used
                    else:

                        # First name is changed
                        if ffname != fname:

                            # Update first name
                            cur.execute("UPDATE users SET fname = ? WHERE uname = ?", (ffname, uname))
                            con.commit()              

                        # Last name is changed
                        if flname != lname:

                            # Update last name
                            cur.execute("UPDATE users SET lname = ? WHERE uname = ?", (flname, uname))
                            con.commit()

                        # Email is changed
                        if femail != email:

                            # Update email
                            cur.execute("UPDATE users SET email = ? WHERE uname = ?", (femail, uname))
                            con.commit()

                        # Username is changed
                        if funame != uname:

                            # Update budget table name
                            old = "budget_" + uname
                            new = "budget_" + funame
                            cur.execute('ALTER TABLE "{}" RENAME TO "{}"'.format(old, new))
                            con.commit()

                            # Update savings table name
                            old = "savings_" + uname
                            new = "savings_" + funame
                            cur.execute('ALTER TABLE "{}" RENAME TO "{}"'.format(old, new))
                            con.commit()

                            # Update username in overview
                            cur.execute("UPDATE overview SET uname = ? WHERE uname = ?", (funame, uname))
                            con.commit()

                            # Update username in users
                            cur.execute("UPDATE users SET uname = ? WHERE uname = ?", (funame, uname))
                            con.commit()

                            # Change user id in session
                            uname = funame
                            session["user_id"] = uname
                            
                        # Display flash
                        flash("Update success!", "success")

        # Update password is clicked
        elif request.form["btnacc"] == "upd_pword":

            # Store all input in variable
            curp = str(request.form.get("cur_pword"))
            newp = str(request.form.get("new_pword"))

            # Strip all input
            curp = curp.strip(' ')
            newp = newp.strip(' ')

            # Check if all inputs are valid
            if len(curp) == 0 or len(newp) == 0:
                flash("Complete details!", "danger")
            elif len(curp) < 8 or len(newp) < 8:
                flash("Passwords is atleast 8 characters!", "danger")
            elif curp == newp:
                flash("Passwords are just the same!", "danger")
            elif not curp.isalnum() or not newp.isalnum():
                flash("Passwords can only contain letters and numbers!", "danger")
            elif not (check_password_hash(pword, curp)):
                flash("Current password is incorrect!", "danger")

            # Inputs are valid
            else:

                # Encrypt password
                newp = generate_password_hash(newp)

                # Update password
                cur.execute("UPDATE users SET pword = ? WHERE uname = ?", (newp, uname))
                con.commit()
                flash("Password changed successfully!", "success")

        # Logout is clicked
        elif request.form["btnacc"] == "logout":

            # Clear session and redirect to login
            session.clear()
            return redirect(url_for("login"))

    # Get all user info
    info = cur.execute("SELECT * FROM users WHERE uname = ?", [uname])

    # Store all user info
    for row in info:
        fname = str(row[3])
        lname = str(row[4])
        email = str(row[2])
        uname = str(row[0])

    # Close cursor and connection
    cur.close()
    con.close()

    # Render account page
    return render_template("account.html", fname=fname, lname=lname, email=email, uname=uname)  

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Error page
@app.route("/error")
@login_required
def error():

    # Render error page
    return render_template("error.html")

# Admin page
@app.route("/admin")
@login_required
def admin():
    
    # Get username
    uname = session["user_id"]

    # Check if admin
    if uname != "1mt1admin1":
        return redirect("/error")

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Get all user info
    data = cur.execute("SELECT * FROM users WHERE uname != '1mt1admin1'")

    # Render admin page
    return render_template("admin.html", data=data)

# Admin activity
@app.route("/admin_activity", methods=["POST"])
@login_required
def admin_activity():
    
    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Button generate is clicked
    if request.form["btnadd"] == "generate":

        # Get typed username and email
        uuname = str(request.form.get("uname"))
        uemail = str(request.form.get("email"))
        
        # Strip username and email
        uuname = uuname.strip(' ')
        uemail = uemail.strip(' ')

        # Generate random password
        charSource = string.ascii_lowercase + string.ascii_uppercase + string.digits
        newPass = ( ''.join(random.choice(charSource) for ctr in range(10)))

        # Get info of sender
        sender = priv_info.acc_mail
        senPass = priv_info.acc_pword

        # Create contents of message
        subject = "NEW PASSWORD | MONEYTRACKER"
        body = "Log in to your account with this new password: " + newPass

        # Setup message to send
        emailMessage = EmailMessage()
        emailMessage["From"] = sender
        emailMessage["To"] = uemail
        emailMessage["Subject"] = subject
        emailMessage.set_content(body)

        # Send new password to user
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:

            # Login sender and send message
            smtp.login(sender, senPass)
            smtp.sendmail(sender, uemail, emailMessage.as_string())

        # Encrypt password
        newPass = generate_password_hash(newPass)

        # Update new password
        cur.execute("UPDATE users set pword = ? WHERE uname = ?", (newPass, uuname))
        con.commit()

        # Display flash
        flash("New password sent!", "success")

    # Button change is clicked
    elif request.form["btnadd"] == "change":
        
        # Get typed password
        pword = str(request.form.get("pword"))

        # Strip password
        pword = pword.strip(' ')
        
        # Encrypt password
        pword = generate_password_hash(pword)

        # Update password
        cur.execute("UPDATE users set pword = ? WHERE uname = '1mt1admin1'", [pword])
        con.commit()

        # Display flash
        flash("Password changed!", "success")
    
    # Button logout is clicked
    elif request.form["btnadd"] == "logout":

        # Clear session and redirect to login
        session.clear()
        return redirect(url_for("login"))
    
    # Close connection and cursor
    cur.close()
    con.close()

    # Redirect to admin page
    return redirect(url_for("admin"))

# Delete account
@app.route("/admin_delete/<string:id>", methods=["GET", "POST"])
@login_required
def admin_deleted(id):

    # Get username
    uname = session["user_id"]

    # Check if admin
    if uname != "1mt1admin1":
        return redirect("/error")

    # Connect to database
    con = sqlite3.connect("moneytracker.db")
    cur = con.cursor()

    # Delete user in users
    cur.execute("DELETE FROM users WHERE uname = ?", ([id]))
    con.commit()

    # Delete user in overview
    cur.execute("DELETE FROM overview WHERE uname = ?", ([id]))
    con.commit()

    # Delete budget table of user
    tblname = "budget_" + id
    cur.execute('DROP TABLE "{}"'.format(tblname))
    con.commit()

    # Delete savings table of user
    tblname = "savings_" + id
    cur.execute('DROP TABLE "{}"'.format(tblname))

    # Display flash
    flash("Account deleted!", "success")

    # Close cursor and connection
    cur.close()
    con.close()

    # Redirect to admin page
    return redirect(url_for("admin"))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#