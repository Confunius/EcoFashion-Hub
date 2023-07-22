from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import shelve
import sys, os
# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product  # it does work
from Objects.transaction.Order import Order
# sys.path.remove(main_dir)

app = Flask(__name__)

# FAQ data
faqs = [
    {
        "section": "Order Issues",
        "questions": ["How to check my order status?", "Why didn't I get an email about my order being shipped?",
"How long will shipping take for my order?"],
        "answers": ["You will receive the shipping inform email within 1 business day after the order is shipped",
"Answer 2", "Answer 3"]
    },
    {
        "section": "Promotions",
        "questions": ["Question 4", "Question 5"],
        "answers": ["Answer 4", "Answer 5"]
    },
{
        "section": "Account",
        "questions": ["Question 6", "Question 7"],
        "answers": ["Answer 6", "Answer 7"]
    },
{
        "section": "Delivery",
        "questions": ["Question 8", "Question 9"],
        "answers": ["Answer 8", "Answer 9"]
    },
{
        "section": "Refund",
        "questions": ["Question 10", "Question 11"],
        "answers": ["Answer 10", "Answer 11"]
    },
    
]

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
    return render_template('/Customer/custservice/FAQ.html', faqs=faqs)

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
@app.route('/view_order/<order_id>')
def view_order(order_id):
    # Retrieve the order details from the database based on order_id
    db = shelve.open('Objects/transaction/order.db', 'r')
    order = db.get(order_id)
    db.close()

    # Render the view modal with the order details
    return render_template('view_order.html', order=order)

@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order(order_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/order.db', 'w')

    # Check if the order_id exists in the database
    if order_id in db:
        # Delete the order from the database
        del db[order_id]
        db.close()

    # Redirect back to the order page
    return redirect(url_for('order'))

@app.route('/admin/order')
def order():
    order_list = []
    db_path = 'Objects/transaction/order.db'
    if not os.path.exists(db_path):
        placeholder_data = [
            {
                "order_id": "O1",
                "user_id": "U1",
                "product_id": "P1",
                "order_date": "2023-07-21",
                "ship_to": "John Doe",
                "promo_code": "N/A"
            },
            {
                "order_id": "O2",
                "user_id": "U2",
                "product_id": "P2",
                "order_date": "2023-07-22",
                "ship_to": "Jane Smith",
                "promo_code": "N/A"
            }
        ]
        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            order = Order(
                data["order_id"],
                data["user_id"],
                data["product_id"],
                data["order_date"],
                data["ship_to"],
                data["promo_code"],
            )
            db[order.order_id] = order
        db.close()

    db = shelve.open(db_path, 'r')
    for key in db:
        order = db.get(key)
        order_list.append(order)
    db.close()
    return render_template('/Admin/transaction/order.html', order_list=order_list, count=len(order_list))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    # Retrieve the form data
    name = request.form['name']
    color = request.form['color']
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = int(request.form['stock'])
    description = request.form['description']
    image = request.form['image']
    category = request.form['category']

    # Update the product_dict with the new product
    db = shelve.open('Objects/transaction/product.db', 'w')
    max_id = 0
    # Find the maximum existing ID in the database
    for key in db:
        product_id = int(key[1:])
        if product_id > max_id:
            max_id = product_id

    new_product_id = "P" + str(max_id + 1)  # Assign a new ID based on the maximum ID + 1
    new_product = Product(new_product_id, name, color, cost_price, list_price, stock, description, image, category)
    db[new_product_id] = new_product
    db.close()

    # Redirect back to the product page
    return redirect(url_for('product'))

@app.route('/update_product/<product_id>', methods=['POST'])
def update_product(product_id):
    # Retrieve the form data
    name = request.form['name']
    color = request.form['color']
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = int(request.form['stock'])
    description = request.form['description']
    image = request.form['image']
    category = request.form['category']

    # Update the product in the database
    db = shelve.open('Objects/transaction/product.db', 'w')

    if product_id in db:
        productobj = db[product_id]
        productobj.name = name
        productobj.color = color
        productobj.cost_price = cost_price
        productobj.list_price = list_price
        productobj.stock = stock
        productobj.description = description
        productobj.image = image
        productobj.category = category
        db[product_id] = productobj
    db.close()

    # Redirect back to the product page
    return redirect(url_for('product'))

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/product.db', 'w')

    # Check if the product_id exists in the database
    if product_id in db:
        # Delete the product from the database
        del db[product_id]
        db.close()

    # Redirect back to the product page
    return redirect(url_for('product'))

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
        # key is product ID
        product = db[key]
        product_dict[key] = product
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
