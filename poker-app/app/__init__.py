#Andrew Tsai, Ricky Lin, Yu Lu, Mustafa Abdullah
#Snorelacks

# Imports
from flask import Flask, render_template, request, flash, url_for, redirect, session
import sqlite3   #enable control of an sqlite database
import csv       #facilitate CSV I/O
import json
from urllib.request import Request, urlopen
import pprint
import os
import re
import db
# Initialize databases

app = Flask(__name__)
app.secret_key = "83ut83ojreoikdlshg3958u4wjtse09gol.hi"

@app.context_processor
def user_context(): # persistent info made avalible for all html templates
    return {
        "logged_in": ('username' in session), # eventually change requirement to userid after db is done
        "current_user": session.get('username')
    }

@app.route("/", methods=['GET', 'POST'])
def homepage():
    if "username" in session:
        currency = db.get_balance(session['username'])
        return render_template("home.html", currency = currency)
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username'].strip()
        pswd = request.form['password'].strip()

        if(not user or not pswd):
            flash("WARNING: One of the fields cannot be empty!")
            return redirect(url_for('register'))

        # add database registration here
        if db.add_user(user, pswd):
            flash(f"Registration Successful! Welcome, {user}. Please log in.")
            return redirect(url_for('login'))
        else:
            flash("Username already exists. Please choose another.")
            return redirect(url_for('register'))
        return redirect(url_for('login'))
    return render_template('create_account.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip()
        pswd = request.form['password'].strip()
        if(not user or not pswd):
            flash("WARNING: Username and Password cannot be empty!")
            return redirect(url_for('login'))

        # add database authentication here
        db_user = db.get_user(user)
        if (db_user is None or not db.check_password(user,pswd)):
            flash("Username or password is not correct!")
            return redirect(url_for('login'))
        flash(f"Login Successful! Welcome back, {user}.")
        session['username'] = user
        print(session['username'])
        return redirect(url_for('homepage'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('homepage'))

@app.route("/setup", methods=['GET', 'POST'])
def setup():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('setup.html')

@app.route("/game", methods=['GET', 'POST'])
def game():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    currency = db.get_balance(session['username'])
    if request.method == 'POST':
        starting_balance = request.form['starting_balance'].strip()
        min_bet = request.form['min_bet'].strip()
        return render_template('game.html', starting_balance = starting_balance, min_bet = min_bet, currency = currency)
    return render_template('game.html', starting_balance = 5000, min_bet = 50, currency = currency)

@app.route("/update_currency", methods = ["GET", "POST"])
def update_currency():
    if 'username' not in session:
        return redirect(url_for('login'))

    if("currency" in request.form):
        balance_change = int(request.form["currency"])
        db.alter_balance(session["username"], balance_change)
        print(f"altered balance by {balance_change}")
    return redirect("/")

@app.route("/update_currency_bailout", methods = ["GET", "POST"])
def update_currency_bailout():
    if 'username' not in session:
        return redirect(url_for('login'))

    if("currency" in request.form):
        balance_change = int(request.form["currency"]) - db.get_balance(session['username'])
        if balance_change < 0: 
            balance_change = 0
        db.alter_balance(session["username"], balance_change)
        print(f"altered balance by {balance_change}")
    return redirect("/")

@app.route("/login.html")
def loginhtml():
    if 'username' in session:
        return redirect("/")
    return render_template("login.html")


@app.route("/register.html")
def registerhtml():
    if 'username' in session:
        return redirect("/")
    return render_template("register.html")

@app.route("/setup.html")
def setuphtml():
    return render_template("setup.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
