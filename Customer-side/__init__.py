from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import shelve
import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product
sys.path.remove(main_dir)

app = Flask(__name__)

# Home
@app.route('/')
def home():
    return render_template('homepage.html')

# Account

# Transaction
@app.route('/products')
def products():
    return render_template('transaction/Product.html')

# Customer Service
@app.route('/FAQ')
def FAQ():
    return render_template('custservice/FAQ.html')

@app.route('/CustomerService')
def CustomerService():
    return render_template('custservice/CustomerService.html')

@app.route('/ServiceRecord')
def ServiceRecord():
    return render_template('custservice/ServiceRecord.html')

if __name__ == '__main__':
    app.run()
