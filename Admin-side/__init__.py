from flask import Flask, render_template, request, redirect, url_for
import shelve
import sys, os
# print("Current working directory:", os.getcwd())
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product
sys.path.remove(main_dir)

app = Flask(__name__)
# Login
# @app.route('/')
# def home():
#     return render_template('login.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


# Account
# @app.route('/account/?')
# def unnamedfunction():
#     return render_template('/account/?.html')


# Transaction
# @app.route('/transaction/order')
@app.route('/')
def order():
    order_list = []
    order_dict = {}
    db_path = 'Objects/order.db'
    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
        db.close()

    db = shelve.open(db_path, 'r')
    order_dict = db.get('Order', {})
    db.close()
    for key in order_dict:
        order = order_dict.get(key)
        order_list.append(order)
    return render_template('/transaction/order.html', order_list=order_list, count=len(order_list))
@app.route('/transaction/product')
def product():
    product_list = []
    product_dict = {}
    db_path = 'Objects/product.db'
    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
        db.close()
    
    db = shelve.open(db_path, 'r')
    product_dict = db.get('Product', {})
    db.close()
    for key in product_dict:
        product = product_dict.get(key)
        product_list.append(product)
    return render_template('/transaction/product.html', product_list=product_list, count=len(product_list))

@app.route('/transaction/review')
def review():
    return render_template('/transaction/review.html')
@app.route('/transaction/promocode')
def promocode():
    return render_template('/transaction/promocode.html')


# Customer Service
# @app.route('/custservice/?')
# def unnamedfunction():
#     return render_template('/custservice/?.html')

if __name__ == '__main__':
    app.run(debug=True)
