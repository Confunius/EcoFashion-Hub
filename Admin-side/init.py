from flask import Flask, render_template, request, redirect, url_for
import shelve

app = Flask(__name__)

# Login
@app.route('/')
def home():
    return render_template('login.html')
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
@app.route('/transaction/order')
def order():
    order_dict = {}
    db = shelve.open('../Objects/order.db', 'r')
    order_dict = db['Order']
    db.close()

    order_list = []
    for key in order_dict:
        order = order_dict.get(key)
        order_list.append(order)
    return render_template('/transaction/order.html', order_list=order_list, count=len(order_list))
@app.route('/transaction/product')
def product():
    return render_template('/transaction/product.html')
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
    app.run()
