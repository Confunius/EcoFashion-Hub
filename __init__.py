from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import shelve
import sys, os
from datetime import datetime
# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product  # it does work
from Objects.transaction.Order import Order
from Objects.transaction.Review import Review
from Objects.transaction.code import Code
from Objects.transaction.cart import Cart, CartItem
# sys.path.remove(main_dir)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your own secret key


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
@app.route('/product')
def products():
    product_list = []
    db_path = 'Objects/transaction/product.db'
    review_db_path = 'Objects/transaction/review.db'
    try:
        db = shelve.open(db_path, 'r')
        review_db = shelve.open(review_db_path, 'r')

        # Get the filter options from request parameters
        category_filter = request.args.get('category')
        rating_filter = request.args.get('rating')

        for key in db:
            product = db[key]
            product_reviews = [review for review in review_db.values() if review.product_id == product.product_id]
            num_reviews = len(product_reviews)
            if num_reviews > 0:
                total_rating = sum(review.rating for review in product_reviews)
                average_rating = total_rating / num_reviews
            else:
                average_rating = 0

            # Round the average_rating to display in stars
            rounded_rating = round(average_rating)

            # Add the average_rating and num_reviews to the product object
            product.average_rating = rounded_rating
            product.num_reviews = num_reviews

            # Apply filters if they are selected
            if category_filter and category_filter not in product.category:
                continue

            if rating_filter and int(rating_filter) > rounded_rating:
                continue

            product_list.append(product)

        db.close()
        review_db.close()
    except:
        product_list = []
    return render_template('/Customer/transaction/Product.html', product_list=product_list, count=len(product_list))


def generate_csrf():
    if 'csrf_token' not in session:
        session['csrf_token'] = 'some_random_string_or_use_uuid_module_to_generate_one'
    return session['csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf

@app.route('/product/<product_id>')
def product_info(product_id):
    review_list = []
    pdb_path = 'Objects/transaction/product.db'
    db_path = 'Objects/transaction/review.db'
    size_options = ['Small', 'Medium', 'Large']
    color_options = ['White', 'Black', 'Blue', 'Red', 'Green', 'Yellow', 'Orange', 'Purple', 'Pink', 'Grey']
    
    try:
        pdb = shelve.open(pdb_path, 'r')
        if product_id in pdb.keys():
            productobj = pdb[product_id]
        pdb.close()
    except:
        productobj = None
    
    try:
        db = shelve.open(db_path, 'r')
        for key in db:
            review = db[key]
            if review.product_id == product_id:
                review_list.append(review)
        db.close()
    except:
        review_list = []

    # Calculate average rating
    total_rating = sum(review.rating for review in review_list)
    total_reviews = len(review_list)
    average_rating = total_rating / total_reviews if total_reviews > 0 else 0
    
    # Round the average rating up to the nearest whole number
    rounded_rating = round(average_rating)
    
    return render_template('/Customer/transaction/ProductInfo.html', productobj=productobj, review_list=review_list, count=len(review_list), rounded_rating=rounded_rating, size_options=size_options, color_options=color_options)

@app.route('/review/<product_id>', methods=['POST'])
def add_review(product_id):
    db_path = 'Objects/transaction/review.db'

    # Retrieve the form data
    customer_name = request.form['customer_name']
    rating = int(request.form['rating'])
    review_comment = request.form['review_comment']

    db = shelve.open(db_path, 'w')  # Open the review.db in read-write mode

    # Generate a new review_id by finding the highest review_id and incrementing it by 1
    max_review_id = 0
    if db:
        # Check if the db is not empty before calculating the max_review_id
        max_review_id = max((int(review_id[1:]) for review_id in db.keys() if review_id.startswith('R')), default=0)

    new_review_id = "R" + str(max_review_id + 1)

    # Create a new Review object
    review = Review(new_review_id, product_id, "I need a User ID Ching Yi ", customer_name, rating, review_comment)

    # Save the review to the review_db
    db[new_review_id] = review
    db.close()

    return redirect(url_for('product_info', product_id=product_id))

cartobj = Cart()

@app.context_processor
def cart_items_processor():
    num_items_in_cart = sum(item.quantity for item in cartobj.get_cart_items())
    return {'num_items_in_cart': num_items_in_cart}

@app.route('/product', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    size = request.form['size']
    color = request.form['color']

    # Fetch the product details from the database
    db_path = 'Objects/transaction/product.db'
    db = shelve.open(db_path, 'r')
    product = db.get(product_id)
    db.close()

    if product is None:
        return redirect(url_for('products'))

    # Create an item object with the product details and the selected quantity
    item = CartItem(product_id=product.product_id, name=product.name, price=product.list_price, quantity=quantity, size=size, color=color)

    # Add the item to the cart
    cartobj.add_to_cart(item)

    return redirect(url_for('cart'))

@app.route('/update_cart_item/<cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    action = request.form.get('action')
    new_size = request.form.get('size')  # Get the selected size from the form
    new_color = request.form.get('color')

    cart_items = cartobj.get_cart_items()

    # Find the cart item with matching product_id
    for cart_item in cart_items:
        if cart_item.product_id == cart_item_id:
            if action == 'increment':
                cart_item.quantity += 1
            elif action == 'decrement' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.size = new_size  # Update the size for the cart item
            cart_item.color = new_color


    return redirect(url_for('cart'))


@app.route('/delete_cart_item/<cart_item_id>', methods=['POST'])
def delete_cart_item(cart_item_id):
    cart_items = cartobj.get_cart_items()

    # Find the cart item with matching product_id
    for cart_item in cart_items:
        if cart_item.product_id == cart_item_id:
            cart_items.remove(cart_item)

    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart_items = cartobj.get_cart_items()
    num_items_in_cart = sum(item.quantity for item in cart_items)
    size_options = ['Small', 'Medium', 'Large']
    color_options = ['White', 'Black', 'Blue', 'Red', 'Green', 'Yellow', 'Orange', 'Purple', 'Pink', 'Grey']


    # Combine rows with the same item name, price, quantity, and size
    combined_items = {}
    for item in cart_items:
        key = (item.name, item.price, item.size, item.color)
        existing_item = combined_items.get(key)
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            combined_items[key] = CartItem(
                product_id=item.product_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                size=item.size,
                color=item.color
            )

    # Convert the dictionary of combined items back to a list
    combined_cart_items = list(combined_items.values())

    cart_total = cartobj.get_cart_total()

    return render_template('Customer/transaction/Cart.html', cart_items=combined_cart_items, cart_total=cart_total, num_items_in_cart=num_items_in_cart, size_options=size_options, color_options=color_options)

@app.route('/update_shipping_cost', methods=['POST'])
def update_shipping_cost():
    delivery_option = request.form['delivery_option']

    # Calculate the new shipping costs based on the selected delivery option
    shipping_costs = 0 if delivery_option == 'collect_on_store' else 5

    # Redirect back to the payment processing page with the updated shipping costs
    return redirect(url_for('display_payment', shipping_costs=shipping_costs))



@app.route('/payment', methods=['GET'])
def display_payment():
    # Retrieve cart items from the cart object
    cart_items = cartobj.get_cart_items()
    db_path = 'Objects/transaction/product.db'
    product_dict = {}
    try:
        db = shelve.open(db_path, 'r')
        product_dict = dict(db)
        db.close()
    except:
        product_dict = {}    
    promo_code_discount = 0

    # Get the subtotal
    subtotal = cartobj.get_cart_total()

    # Calculate the total cost to display first
    shipping_costs = 5
    total_cost = subtotal - promo_code_discount + shipping_costs

    return render_template('/Customer/transaction/PaymentProcess.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, product_dict=product_dict)

@app.route('/validate_promo_code', methods=['POST'])
def validate_promo_code():
    promo_code = request.form.get('promo_code')

    if not promo_code:
        return jsonify({'error': 'Promo code is missing.'}), 400

    code_db_path = 'Objects/transaction/promo.db'

    with shelve.open(code_db_path) as code_db:
        if promo_code in code_db:
            promo = code_db[promo_code]
            end_date_str = promo.end_date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()  # Convert to datetime.date
            today = datetime.now().date()

            if end_date >= today:
                promo_discount = promo.discount
                return jsonify({'valid': True, 'discount': promo_discount})
            else:
                return jsonify({'valid': False, 'error': 'Promo code has expired.'}), 400
        else:
            return jsonify({'valid': False, 'error': 'Invalid promo code.'}), 400



@app.route('/processpayment', methods=['POST'])
def process_payment():
    # Retrieve form data

    delivery = request.form['delivery_option']
    
    # address = request.form['address']
    # postal_code = request.form['postal_code']
    # card_number = request.form['card_number']
    # expiry_date = request.form['expiry_date']
    # cvc = request.form['cvc']
    # save_payment = True if 'save_payment' in request.form else False
    promo_code = request.form['promo_code']
    user_id = 0
    order_date = datetime.now().strftime('%Y-%m-%d')
    max_id = 0
    db = shelve.open('Objects/transaction/order.db', 'w')
    # Find the maximum existing ID in the database
    for key in db:
        order_id = int(key[1:])
        if order_id > max_id:
            max_id = order_id
    order_id = "O" + str(order_id + 1)  # Assign a new ID based on the maximum ID + 1

    order = Order(order_id, user_id, cartobj, order_date, delivery, promo_code)
    db[order_id] = order
    db.close()
    
    return redirect(url_for('thankyou', order_id=order_id))


@app.route('/thankyou/<order_id>')
def thankyou(order_id):
    # Retrieve cart items and promo code discount (if applicable) from the cart object
    code_db_path = 'Objects/transaction/promo.db'
    order_db_path = 'Objects/transaction/order.db'
    product_db_path = 'Objects/transaction/product.db'
    cart_items = cartobj.get_cart_items()
    promo_code = request.args.get('promo_code')  # Assuming the promo code is passed as a query parameter

    # Calculate the subtotal
    subtotal =  cartobj.get_cart_total()

    # Get the delivery option
    db = shelve.open(order_db_path, 'r')
    order = db.get(order_id)
    delivery_option = order.delivery
    db.close()

    # Get the product dictionary
    db = shelve.open(product_db_path, 'r')
    product_dict = dict(db)
    db.close()

    # Check if the promo code is valid
    promo_valid = False
    promo_discount = 0
    if promo_code:
        with shelve.open(code_db_path) as code_db:
            if promo_code in code_db:
                promo = code_db[promo_code]
                end_date = datetime.strptime(promo['end_date'], '%Y-%m-%d')
                today = datetime.now().date()
                if end_date >= today:
                    promo_valid = True
                    promo_discount = promo['discount']

    # Calculate the promo code discount (if applicable)
    promo_code_discount = 0
    if promo_valid:
        promo_code_discount = subtotal * (promo_discount / 100)

    # Calculate the total cost
    shipping_costs = 5
    total_cost = subtotal - promo_code_discount + shipping_costs

    # Determine delivery option and relevant information
    # db = shelve.open('user_db_path', 'r')
    # shipping_address = db.get(order.user_id).address  
    shipping_address = "123 Main Street, City, Country"  # Replace this with the actual shipping address
    pickup_location = "EcoFashion Store, Location"  # Replace this with the actual pickup location

    return render_template('Customer/transaction/Thankyou.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, delivery_option=delivery_option,
                           shipping_address=shipping_address, product_dict=product_dict, pickup_location=pickup_location)



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
                "delivery": "Standard Delivery",
                "promo_code": "N/A"
            },
            {
                "order_id": "O2",
                "user_id": "U2",
                "product_id": "P2",
                "order_date": "2023-07-22",
                "ship_to": "Collect on Store",
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
                "description": "Introducing the \"Men 100% Cotton Linen Long Sleeve Shirt\"! Crafted with the finest blend of cotton and linen, this classic white shirt boasts both style and comfort. Perfect for casual outings or semi-formal occasions, its long sleeves add an air of sophistication to any ensemble. The breathable fabric ensures you stay cool and relaxed all day long. Embrace a timeless, versatile look with this essential wardrobe piece that pairs effortlessly with jeans, chinos, or tailored trousers. Designed to exude elegance and confidence, this shirt is a must-have for every fashion-forward gentleman. Get ready to make a lasting impression.",
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
                "description": "Women Organic Dye Casual Jacket! Elevate your style with this eco-friendly \"Women Organic Dye Casual Jacket.\" Crafted with organic dyes and sustainably sourced materials, this jacket embodies a perfect blend of fashion and environmental consciousness. The soft and breathable fabric ensures comfort without compromising on style. Its pristine white color complements any outfit, making it a versatile addition to your wardrobe. Embrace the essence of modern femininity as you step out in this chic jacket, designed to make a statement at casual gatherings or outings with friends. Embrace sustainability with flair and inspire others to do the same.",
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
                "description": "Women Tank Top 100% Recycled Fibers! Embrace a greener lifestyle with our \"Women Tank Top 100% Recycled Fibers.\" Made from environmentally friendly materials, this white tank top not only enhances your workout performance but also reduces your carbon footprint. The soft and stretchable fabric provides a comfortable and supportive fit, making it ideal for any active lifestyle. Whether you're hitting the gym, going for a run, or practicing yoga, this tank top ensures you stay cool and dry throughout your workout. Embrace sustainability without compromising on style, and let this tank top be a reflection of your commitment to a healthier planet.",
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

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    db_path = 'Objects/transaction/review.db'
    db = shelve.open(db_path, 'w')
    try:
        del db[str(review_id)]
    except KeyError:
        pass
    db.close()
    return redirect(url_for('review'))

@app.route('/admin/review')
def review():
    review_list = []
    db_path = 'Objects/transaction/review.db'
    if not os.path.exists(db_path):
        placeholder_reviews = [
            {
                "review_id": "R1",
                "product_id": "P1",
                "user_id": 1,
                "author": "John Doe",
                "rating": 4,
                "description": "Great product! Love it.",
            },
            {
                "review_id": "R2",
                "product_id": "P1",
                "user_id": 2,
                "author": "Jane Smith",
                "rating": 5,
                "description": "Excellent quality and fast delivery.",
            },
            {
                "review_id": "R3",
                "product_id": "P2",
                "user_id": 3,
                "author": "Mike Johnson",
                "rating": 3,
                "description": "Decent product, but could be better.",
            },
            {
                "review_id": "R4",
                "product_id": "P2",
                "user_id": 4,
                "author": "Sarah Lee",
                "rating": 5,
                "description": "Absolutely amazing! Highly recommended.",
            },
            {
                "review_id": "R5",
                "product_id": "P3",
                "user_id": 5,
                "author": "Chris Williams",
                "rating": 4,
                "description": "Nice product for the price.",
            },
        ]

        # Save the placeholder reviews to the review.db database
        db_path = 'Objects/transaction/review.db'
        db = shelve.open(db_path, 'c')
        for data in placeholder_reviews:
            review = Review(
                data["review_id"],
                data["product_id"],
                data["user_id"],
                data["author"],
                data["rating"],
                data["description"],
            )
            db[str(review.review_id)] = review
        db.close()

    db = shelve.open(db_path, 'r')
    review_list = list(db.values())  # Assuming reviews are stored in the 'review' shelve
    db.close()

    return render_template('Admin/transaction/review.html', review_list=review_list, count=len(review_list))

@app.route('/admin/code')
def promocode():
    code_list = []
    db_path = 'Objects/transaction/promo.db'
    
    if not os.path.exists(db_path):
        placeholder_data = [
            {
                "code": "CODE1",
                "discount": 10.0,
                "end_date": "2023-12-31",
            },
            {
                "code": "CODE2",
                "discount": 20.0,
                "end_date": "2023-11-30",
            },
            {
                "code": "CODE3",
                "discount": 15.0,
                "end_date": "2023-10-31",
            },
        ]

        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            promo = Code(
                data["code"],
                data["discount"],
                data["end_date"],
            )
            db[promo.code] = promo
        db.close()

    db = shelve.open(db_path, 'r')
    for key in db:
        code = db[key]
        code_list.append(code)
    db.close()
    return render_template('/Admin/transaction/promocode.html', code_list=code_list, count=len(code_list))

@app.route('/admin/add_promo', methods=['POST'])
def add_promo():
    if request.method == 'POST':
        code = request.form['code']
        discount = float(request.form['discount'])
        end_date = request.form['end_date']
        promo = Code(code, discount, end_date)
        db = shelve.open('Objects/transaction/promo.db', 'c')
        db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))

@app.route('/update_code/<code>', methods=['POST'])
def update_code(code):
    if request.method == 'POST':
        discount = float(request.form['discount'])
        end_date = request.form['end_date']
        promo = Code(code, discount, end_date)
        db = shelve.open('Objects/transaction/promo.db', 'w')
        db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))

@app.route('/delete_code/<code>', methods=['POST'])
def delete_code(code):
    db = shelve.open('Objects/transaction/promo.db', 'w')
    if code in db:
        del db[code]
    db.close()
    return redirect(url_for('promocode'))



if __name__ == '__main__':
    app.run()
