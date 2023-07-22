from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import shelve
import sys, os
# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product  # it does work
# sys.path.remove(main_dir)

app = Flask(__name__)

# Home
@app.route('/')
def home():
    return render_template('/Customer/homepage.html')
# Customer side

# Account
@app.route('/CustomerDelete')
def CustomerDelete():
    return render_template('/Customer/account/CustomerDelete.html')

@app.route('/CustomerInfo')
def CustomerInfo():
    return render_template('/Customer/account/CustomerInfo.html')

@app.route('/CustomerUpdate')
def CustomerUpdate():
    return render_template('/Customer/account/CustomerUpdate.html')

@app.route('/CustomerAccounts')
def CustomerAccounts():
    return render_template('/Customer/account/CustomerAccounts.html')

@app.route('/Profile')
def Profile():
    return render_template('/Customer/account/Profile.html')

@app.route('/EditProfile')
def EditProfile():
    return render_template('/Customer/account/EditProfile.html')

# Transaction
@app.route('/products')
def products():
    return render_template('/Customer/transaction/Product.html')

@app.route('/cart')
def cart():
    return render_template('/Customer/transaction/Cart.html')

# Customer Service
@app.route('/FAQ')
def FAQ():
    return render_template('/Customer/custservice/FAQ.html')

@app.route('/CustomerService')
def CustomerService():
    return render_template('/Customer/custservice/CustomerService.html')

@app.route('/ServiceRecord')
def ServiceRecord():
    return render_template('/Customer/custservice/ServiceRecord.html')




# Admin side

@app.route('/admin')
def ahome():
    return render_template('/Admin/login.html')
@app.route('/admin/homepage')
def ahomepage():
    return render_template('/Admin/homepage.html')


# Account
@app.route('/admin/AdminAccounts')
def AdminAccounts():
    return render_template('/Admin/account/AdminAccounts.html')

@app.route('/admin/AdminDelete')
def AdminDelete():
    return render_template('/Admin/account/AdminDelete.html')

@app.route('/admin/AdminFrom')
def AdminFrom():
    return render_template('/Admin/account/AdminFrom.html')

@app.route('/admin/AdminInfo')
def AdminInfo():
    return render_template('/Admin/account/AdminInfo.html')

@app.route('/admin/AdminPasswordForm')
def AdminPasswordForm():
    return render_template('/Admin/account/AdminPasswordForm.html')

@app.route('/admin/AdminUpdate')
def AdminUpdate():
    return render_template('/Admin/account/AdminUpdate.html')

@app.route('/admin/Navbar')
def Navbar():
    return render_template('/Navbar.html')

@app.route('/admin/Sidebar')
def Sidebar():
    return render_template('/Sidebar.html')


# Transaction
@app.route('/admin/order')
def order():
    order_list = []
    order_dict = {}
    db_path = 'Objects/transaction/order.db'
    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
        db.close()

    db = shelve.open(db_path, 'r')
    order_dict = db.get('Order', {})
    db.close()
    for key in order_dict:
        order = order_dict.get(key)
        order_list.append(order)
    return render_template('/Admin/transaction/order.html', order_list=order_list, count=len(order_list))

@app.route('/admin/product')
def product():
    product_list = []
    product_dict = {}
    db_path = 'Objects/transaction/product.db'
    if not os.path.exists(db_path):
        placeholder_data = [
            {
                "product_id": "P1",
                "name": "Men 100% Cotton Linen Long Sleeve Shirt",
                "color": "White",
                "cost_price": 8,
                "list_price": 16,
                "stock": 3,
                "description": "Introducing the \"Men 100% Cotton Linen Long Sleeve Shirt\"...",
                "image": "https://m.media-amazon.com/images/I/615Cby-DciL._AC_SX679_.jpg",
                "category": "Men's Casual"
            },
            {
                "product_id": "P2",
                "name": "Women Organic Dye Casual Jacket",
                "color": "White",
                "cost_price": 14,
                "list_price": 18,
                "stock": 5,
                "description": "Women Organic Dye Casual Jacket...",
                "image": "https://m.media-amazon.com/images/I/81mrNU4gF3L._AC_SX569_.jpg",
                "category": "Women's Casual"
            },
            {
                "product_id": "P3",
                "name": "Women Tank Top 100% Recycled Fibers",
                "color": "White",
                "cost_price": 6,
                "list_price": 12,
                "stock": 2,
                "description": "Women Tank Top 100% Recycled Fibers...",
                "image": "https://m.media-amazon.com/images/I/61a9kY47XPL._AC_SX679_.jpg",
                "category": "Women's Sportswear"
            },
        ]

        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            product = Product(
                data["product_id"],
                data["name"],
                data["color"],
                data["cost_price"],
                data["list_price"],
                data["stock"],
                data["description"],
                data["image"],
                data["category"],
            )
            db[product.product_id] = product
        db.close()
    
    db = shelve.open(db_path, 'r')
    # open the db and retrieve the dictionary
    for key in db:
        product = db[key]
        product_dict[product.product_id] = product
    db.close()
    for key in product_dict:
        product = product_dict.get(key)
        product_list.append(product)
    return render_template('/Admin/transaction/product.html', product_list=product_list, count=len(product_list))

@app.route('/admin/review')
def review():
    return render_template('/Admin/transaction/review.html')
@app.route('/admin/promocode')
def promocode():
    return render_template('/Admin/transaction/promocode.html')



if __name__ == '__main__':
    app.run()
