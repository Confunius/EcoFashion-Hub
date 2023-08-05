import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import shelve
import sys
import os
from datetime import datetime
import stripe
# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from Objects.transaction.Product import Product  # it does work
from Objects.transaction.Order import Order
from Objects.transaction.Review import Review
from Objects.transaction.code import Code
from Objects.transaction.cart import Cart, CartItem
from Objects.account.Customer import User, userPayment
from Objects.CustomerService.Record import Record
# sys.path.remove(main_dir)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your own secret key

stripe.api_key = 'sk_test_51NbJAUL0EO5j7e8js0jOonkCjFkHksaoITSyuD8YR34JLHMBkX3Uy4SwejTVr6XAvL8amqm4kMjmXtedg2I1oNTI00wnaqFYJJ'  # Replace with your own secret key


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
            product_reviews = [review for review in review_db.values(
            ) if review.product_id == product.product_id]
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

    # Create a list of unique categories from the product_list
    categories = list(set(product.category for product in product_list))

    return render_template('/Customer/transaction/Product.html', product_list=product_list, count=len(product_list), categories=categories)


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

    # Create a list of unique colors from the productobj object.
    color_options = ', '.join(productobj.color_options)

    # Create a list of unique sizes from the productobj object.
    size_options = ', '.join(productobj.size_options)

    return render_template('/Customer/transaction/ProductInfo.html', productobj=productobj, review_list=review_list, count=len(review_list), rounded_rating=rounded_rating, size_options=size_options, color_options=color_options)


@app.route('/review/<product_id>', methods=['POST'])
def add_review(product_id):
    db_path = 'Objects/transaction/review.db'

    # Retrieve the form data
    customer_name = request.form['customer_name']
    rating = int(request.form['rating'])
    review_comment = request.form['review_comment']
    try:
        db = shelve.open(db_path, 'w')  # Open the review.db in read-write mode
    except:
        db = shelve.open(db_path, 'c')

    # Generate a new review_id by finding the highest review_id and incrementing it by 1
    max_review_id = 0
    if db:
        # Check if the db is not empty before calculating the max_review_id
        max_review_id = max((int(review_id[1:]) for review_id in db.keys(
        ) if review_id.startswith('R')), default=0)

    new_review_id = "R" + str(max_review_id + 1)

    # Create a new Review object
    review = Review(new_review_id, product_id, "I need a User ID Ching Yi ",
                    customer_name, rating, review_comment)

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
    item = CartItem(product_id=product.product_id, name=product.name,
                    price=product.list_price, quantity=quantity, size=size, color=color)

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
    db_path = 'Objects/transaction/product.db'
    db = shelve.open(db_path, 'r')
    num_items_in_cart = sum(item.quantity for item in cart_items)

    # Combine rows with the same item name, price, quantity, and size
    combined_items = {}
    for item in cart_items:
        product = db.get(item.product_id)
        size_options = product.size_options
        color_options = product.color_options
        key = (item.name, item.price, item.size, item.color, tuple(size_options), tuple(color_options))
        existing_item = combined_items.get(key)
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            item.size_options = size_options
            item.color_options = color_options
            combined_items[key] = item

    # update the cart_obj with the combined items
    print(list(combined_items.values()))
    cartobj.cart_items = list(combined_items.values())

    # Convert the dictionary of combined items back to a list
    combined_cart_items = list(combined_items.values())

    cart_total = cartobj.get_cart_total()

    return render_template('Customer/transaction/Cart.html', cart_items=combined_cart_items, cart_total=cart_total, num_items_in_cart=num_items_in_cart)

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

    max_id = 0
    try:
        db = shelve.open('Objects/transaction/order.db', 'w')
        # Find the maximum existing ID in the database
        for key in db:
            order_id = int(key[1:])
            if order_id > max_id:
                max_id = order_id
        # Assign a new ID based on the maximum ID + 1
        order_id = "O" + str(max_id + 1)
        db.close()
    except:
        db = shelve.open('Objects/transaction/order.db', 'c')
        order_id = "O1"
    
    session_cart_items = []
    for item in cart_items:
        session_cart_items.append(item.to_dict())

    session['intent_metadata'] = {'order_id': order_id, 'cart': session_cart_items}
    
    return render_template('/Customer/transaction/PaymentProcess.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, product_dict=product_dict)

@app.route('/update_shipping_cost', methods=['POST'])
def update_shipping_cost():
    delivery_option = request.form['delivery_option']

    # Calculate the new shipping costs based on the selected delivery option
    shipping_costs = 0 if delivery_option == 'collect_on_store' else 5

    # Redirect back to the payment processing page with the updated shipping costs
    return redirect(url_for('display_payment', shipping_costs=shipping_costs))

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
            # Convert to datetime.date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()

            if end_date >= today:
                promo_discount = promo.discount
                return jsonify({'valid': True, 'discount': promo_discount})
            else:
                return jsonify({'valid': False, 'error': 'Promo code has expired.'}), 400
        else:
            return jsonify({'valid': False, 'error': 'Invalid promo code.'}), 400

Domain = "https://confunius-sturdy-space-guide-9pwww99p7vqfxrqw-5000.app.github.dev/"

@app.route('/processpayment', methods=['GET', 'POST'])
def process_payment():
    intent_id = request.args.get("payment_intent")
    intent = stripe.PaymentIntent.retrieve(intent_id)
    order_id = intent['metadata']['order_id']
    cart_json = intent['metadata']['cart']
    cart = json.loads(cart_json)
    product_ids = [item['product_id'] for item in cart]
    for i, product_id in enumerate(product_ids):
        ele_product_id = product_id
        ele_size = cart[i]['size']
        ele_color = cart[i]['color']
        ele_quantity = cart[i]['quantity']
        promocode ="N/A"
        delivery = "N/A"
        user_id = 0
        order_date = datetime.now().strftime("%Y-%m-%d")

        db = shelve.open('Objects/transaction/order.db', 'w')
        order = Order(order_id, user_id, ele_product_id, ele_size, ele_color, ele_quantity, order_date, delivery, promocode)
        db[order_id] = order


    print(intent)
    # Retrieve form data
    # delivery = request.form['delivery_option']
    # address = request.form['address']
    # postal_code = request.form['postal_code']
    # card_number = request.form['card_number']
    # expiry_date = request.form['expiry_date']
    # cvc = request.form['cvc']
    # save_payment = True if 'save_payment' in request.form else False
    # size = request.form.getlist('size')
    # color = request.form.getlist('color')
    # quantity = request.form.getlist('quantity')
    # product_id = request.form.getlist('product_id')



    # max_id = 0
    # try:
    #     db = shelve.open('Objects/transaction/order.db', 'w')
    #     # Find the maximum existing ID in the database
    #     for key in db:
    #         order_id = int(key[1:])
    #         if order_id > max_id:
    #             max_id = order_id
    #     # Assign a new ID based on the maximum ID + 1
    #     order_id = "O" + str(max_id + 1)
    #     db.close()
    # except:
    #     db = shelve.open('Objects/transaction/order.db', 'c')
    #     order_id = "O1"
    

    # for i, product_id in enumerate(product_id):
    #     ele_product_id = product_id
    #     ele_size = size[i]
    #     ele_quantity = int(quantity[i])
    #     ele_color = color[i]
    #     promo_code = request.form['promo_code']
    #     user_id = 0
    #     order_date = datetime.now().strftime('%Y-%m-%d')

    #     # Save each order in the database
    #     db = shelve.open('Objects/transaction/order.db', 'w')
    #     order = Order(order_id, user_id, ele_product_id, ele_size, ele_color, ele_quantity,
    #                 order_date, delivery, promo_code)
    #     db[order_id] = order
    #     db.close()

    # # Store payment info in a dictionary
    # payment_info = {
    #     'delivery': delivery,
    #     'order_id': order_id,
    #     'subtotal': request.form['subtotal'],
    #     'promo_code_discount': request.form['promo_code_discount'],
    #     'shipping_costs': request.form['shipping_costs'],
    #     'total_cost': request.form['total_cost'],
    # }
    # session['payment_info'] = payment_info
    # session['cart_item'] = [item.to_dict() for item in cartobj.cart_items]
    
    # # Remove all items from the cart
    # cartobj.cart_items = []
    
    return redirect(url_for('thankyou'))

@app.route('/totalcostcalculator')
def calculate_total_cost(cart_items, delivery_option, promo_code):
    subtotal = 0
    for item in cart_items:
        subtotal += item.price * item.quantity
    shipping_costs = 0 if delivery_option == 'collect_on_store' else 5
    code_db_path = 'Objects/transaction/promo.db'

    with shelve.open(code_db_path) as code_db:
        if promo_code in code_db:
            promo = code_db[promo_code]
            end_date_str = promo.end_date
            # Convert to datetime.date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()

            if end_date >= today:
                promo_discount = promo.discount
        else:
            promo_discount = 0
    total_cost = subtotal - promo_discount + shipping_costs
    return total_cost

@app.route('/create_intent', methods=['POST'])
def create_intent():
    intent_metadata = session['intent_metadata']
    order_id = intent_metadata['order_id']
    cart = intent_metadata['cart']
    cart_json = json.dumps(cart)

    session.pop('intent_metadata', None)
    amount = int(float(calculate_total_cost(cartobj.cart_items, 'standard_delivery', '')) * 100)
    intent = stripe.PaymentIntent.create(
        amount = amount,  # Stripe expects the amount in cents
        currency='sgd',
        automatic_payment_methods={
            'enabled': True,
        },
        metadata={
            'order_id': order_id,
            'cart': cart_json,
        }
    )
    return jsonify({
        'clientSecret': intent['client_secret'],
        'amount' : amount
    })

@app.route('/thankyou')
def thankyou():

    # Retrieve cart items and promo code discount (if applicable) from the cart object
    product_db_path = 'Objects/transaction/product.db'
    payment_info = session['payment_info']
    session.pop('payment_info', None)

    delivery_option = payment_info['delivery']
    order_id = payment_info['order_id']
    subtotal = payment_info['subtotal']
    promo_code_discount = payment_info['promo_code_discount']
    shipping_costs = payment_info['shipping_costs']
    total_cost = payment_info['total_cost']
    cart_items = session['cart_item']

    # Create product_dict
    product_dict = {}
    with shelve.open(product_db_path) as product_db:
        for key in product_db:
            product = product_db[key]
            product_dict[key] = product

    shipping_address = "123 Main Street, City, Country"
    pickup_location = "EcoFashion Store, Location"
    print("order: ", order_id)

    return render_template('Customer/transaction/Thankyou.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, delivery_option=delivery_option,
                           shipping_address=shipping_address, product_dict=product_dict,
                           pickup_location=pickup_location, order_id=order_id)


@app.route('/cancel_and_refund/<order_id>', methods=['GET'])
def cancel_and_refund(order_id):
    # Fetch the order_id from the session or some other mechanism
    db_path = 'Objects/transaction/order.db'

    if order_id:
        # Open the shelve database
        db = shelve.open(db_path, 'w')

        # Delete the order from the database
        del db[order_id]

        # Close the shelve database
        db.close()

    return render_template('transaction/CancelAndRefund.html')

# Customer Service
with shelve.open("deleted_records.db") as deleted_records_db:
    deleted_record_ids = deleted_records_db.get('deleted_record_ids', set())

with shelve.open("deleted_records_admin.db") as deleted_records_admin_db:
    deleted_record_admin_ids = deleted_records_admin_db.get('deleted_record_ids', set())

def get_total_record_count():
    with shelve.open("service_records.db") as service_records_db:
        # Get the count of current records
        current_count = len(service_records_db)

    with shelve.open("deleted_records.db") as deleted_records_db:
        # Get the count of deleted records
        deleted_count = len(deleted_records_db.get('deleted_record_ids', set()))

    # Calculate the total count by adding current and deleted records
    total_count = current_count + deleted_count
    return total_count
    
@app.route('/FAQ')
def FAQ():
    with shelve.open("faqs.db") as db:
        faqs = db.get("faqs", [])
    return render_template('/Customer/custservice/FAQ.html', faqs=faqs)


@app.route('/CustomerService')
def CustomerService():
    return render_template('/Customer/custservice/CustomerService.html')


@app.route('/ServiceRecord')
def ServiceRecord():
    with shelve.open("service_records.db", writeback=True) as service_records_db:
        return render_template('/Customer/custservice/ServiceRecord.html', service_records=service_records_db)
    
@app.route('/record_detail/<record_id>')
def record_detail(record_id):
    # Find the record with the given record_id
    with shelve.open("service_records.db", writeback=True) as service_records_db:
        record = service_records_db.get(record_id)
        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        subject = record.subject
        chat = record.chat
        date = record.date
        status = record.status
        auto = record.auto

        # Parse the string as a list of dictionaries
        chat_list = json.loads(chat)
        # Initialize lists to store senders and contents
        senders = []
        contents = []

        # Loop through the list of dictionaries to retrieve the sender and content
        for entry in chat_list:
            sender = entry['sender']
            content = entry['content']
            senders.append(sender)
            contents.append(content)

        return render_template('Customer/custservice/record_detail.html', record=record, senders=senders, contents=contents,
                               subject=subject, date=date, status=status, auto=auto)
    # Loop through the list of dictionaries to retrieve the sender and content
    for entry in chat_list:
        sender = entry['sender']
        content = entry['content']
        senders.append(sender)
        contents.append(content)

    return render_template('/Customer/custservice/record_detail.html', record=record, senders=senders, contents=contents,
                           subject=subject, date=date, status=status, auto=auto)

@app.route('/save_service_record', methods=['POST'])
def save_service_record():
    # Get the data from the request
    data = request.get_json()
    global deleted
    record_id = data.get('record_id')

    if not record_id and record_id not in deleted_record_ids:
        # If record_id is not provided, it means we are creating a new record
        total_records = get_total_record_count()
        record_id = f"record_{total_records + 1}"
        with shelve.open("service_records.db", writeback=True) as service_records_db:
            # Create a new Record object and add it to the service_records_db dictionary
            record = Record(
                record_id=record_id,
                date=data['dateInitiated'],
                chat=data['chatHistory'],
                subject=data['subject'],
                status=data['status'],
                auto=data['auto']
            )
            service_records_db[record_id] = record
    else:
        # If record_id is provided, it means we are updating an existing record
        with shelve.open("service_records.db", writeback=True) as service_records_db:
            # Check if the record_id exists in the service_records_db dictionary
            if record_id in service_records_db:
                # Update the existing record
                record = service_records_db[record_id]
                record.date = data['dateInitiated']
                record.chat = data['chatHistory']
                record.subject = data['subject']
                record.status = data['status']
                record.auto = data['auto']
            elif record_id not in service_records_db:
                return jsonify({'error': 'Record not found'}), 404

    # Print the updated chat information for regular service_records_db
    with shelve.open("service_records.db", writeback=True) as service_records_db:
        record = service_records_db.get(record_id)

    # If this is an admin record, save it to the admin database as well
    if record_id:
        with shelve.open("service_records_admin.db", writeback=True) as service_records_admin_db:
            # Check if the record_id already exists in the service_records_admin_db dictionary
            if record_id in service_records_admin_db:
                # Update the existing admin record
                record_admin = service_records_admin_db[record_id]
                record_admin.date = data['dateInitiated']
                record_admin.chat = data['chatHistory']
                record_admin.subject = data['subject']
                record_admin.status = data['status']
                record_admin.auto = data['auto']
            elif record_id not in service_records_admin_db and record_id not in deleted_record_admin_ids:
                # Create a new admin Record object and add it to the service_records_admin_db dictionary
                total_records = get_total_record_count()
                record_id = f"record_{total_records}"
                record_admin = Record(
                    record_id=record_id,
                    date=data['dateInitiated'],
                    chat=data['chatHistory'],
                    subject=data['subject'],
                    status=data['status'],
                    auto=data['auto']
                )
                service_records_admin_db[record_id] = record_admin

        # Print the updated chat information for admin service_records_admin_db
        with shelve.open("service_records_admin.db", writeback=True) as service_records_admin_db:
            record_admin = service_records_admin_db.get(record_id)
            print("Updated Chat for service_records_admin_db:", record_admin.chat)

    # Return a success response
    return jsonify({'message': 'Record saved successfully'})
    
@app.route('/delete_record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    # Check if the record_id exists in the service_records dictionary
    with shelve.open("service_records.db", writeback=True) as service_records_db:
        if record_id in service_records_db:
            # If the record exists, delete it from the dictionary
            deleted_record_ids.add(record_id)
            with shelve.open("deleted_records.db") as deleted_records_db:
                deleted_records_db['deleted_record_ids'] = deleted_record_ids
            del service_records_db[record_id]
            return jsonify({'message': 'Record deleted successfully'})
        else:
            # If the record_id does not exist, return an error message
            return jsonify({'error': 'Record not found'}), 404

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
        db = shelve.open(db_path, 'c')
        db.close()

    db = shelve.open(db_path, 'r')
    for key in db:
        order = db.get(key)
        order_list.append(order)
    db.close()
    return render_template('/Admin/transaction/order.html', order_list=order_list, count=len(order_list))


@app.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form['name'].strip().title()
    color_options = request.form.get('color_options').split(',')
    color_options = [option.strip() for option in color_options]  # Remove leading/trailing spaces
    size_options = request.form.get('size_options').split(',')
    size_options = [option.strip() for option in size_options]
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = max(int(request.form['stock']), 0)
    description = request.form['description'].strip()
    image = request.form['image'].strip()
    category = request.form['category'].strip()

    # Update the product_dict with the new product
    db = shelve.open('Objects/transaction/product.db', 'w')
    # Add stripe product
    product = stripe.Product.create(
        name=name,
        default_price_data={
            "unit_amount": int(list_price * 100),
            "currency": "sgd",
        },
        expand=["default_price"],
        )
    product_id = product["id"]

    new_product = Product(product_id, name, color_options, size_options, cost_price,
                          list_price, stock, description, image, category)
    db[product_id] = new_product
    db.close()



    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/update_product/<product_id>', methods=['POST'])
def update_product(product_id):
    # Retrieve the form data
    name = request.form['name'].strip().title()
    color_options = request.form.get('color_options').split(',')
    color_options = [option.strip() for option in color_options]
    size_options = request.form.get('size_options').split(',')
    size_options = [option.strip() for option in size_options]
    cost_price = float(request.form['cost_price'])
    list_price = float(request.form['list_price'])
    stock = max(int(request.form['stock']), 0)
    description = request.form['description'].strip()
    image = request.form['image'].strip()
    category = request.form['category'].strip()

    # Update the product in the database
    db = shelve.open('Objects/transaction/product.db', 'w')

    if product_id in db:
        productobj = db[product_id]
        productobj.name = name
        productobj.color_options = color_options
        productobj.size_options = size_options
        productobj.cost_price = cost_price
        productobj.list_price = list_price
        productobj.stock = stock
        productobj.description = description
        productobj.image = image
        productobj.category = category
        db[product_id] = productobj
    db.close()

    stripe.Product.modify(
        product_id,
        name=name,
        unit_amount=int(list_price * 100),
        )

    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/product.db', 'w')

    # Check if the product_id exists in the database
    if product_id in db:
        # Delete the product from the database
        del db[product_id]
        db.close()
    
    stripe.Product.delete(product_id)

    # Redirect back to the product page
    return redirect(url_for('product_admin'))

def join_and_filter(list_):
    """This function joins a list of strings with commas and spaces, but with 'and' before the last item. This would be used
    to display the color_options."""
    if len(list_) > 1:
        return ', '.join(list_[:-1]) + ' and ' + list_[-1]
    elif list_:
        return list_[0]
    else:
        return ''
app.jinja_env.filters['join_and'] = join_and_filter

@app.route('/admin/product')
def product_admin():
    product_list = []
    product_dict = {}
    db_path = 'Objects/transaction/product.db'
    if not os.path.exists(db_path):
        placeholder_data = [

            {
                "product_id": "",
                "name": "Men 100% Cotton Linen Long Sleeve Shirt",
                "color_options": ["White", "Blue", "Green"],
                "size_options": ["M", "L", "XL"],
                "cost_price": 8,
                "list_price": 16,
                "stock": 3,
                "description": "Introducing the \"Men 100% Cotton Linen Long Sleeve Shirt\"! Crafted with the finest blend of cotton and linen, this classic white shirt boasts both style and comfort. Perfect for casual outings or semi-formal occasions, its long sleeves add an air of sophistication to any ensemble. The breathable fabric ensures you stay cool and relaxed all day long. Embrace a timeless, versatile look with this essential wardrobe piece that pairs effortlessly with jeans, chinos, or tailored trousers. Designed to exude elegance and confidence, this shirt is a must-have for every fashion-forward gentleman. Get ready to make a lasting impression.",
                "image": "https://m.media-amazon.com/images/I/615Cby-DciL._AC_SX679_.jpg",
                "category": "Men's Casual"
            },
            {
                "product_id": "",
                "name": "Women Organic Dye Casual Jacket",
                "color_options": ["White", "Blue", "Green"],
                "size_options": ["S", "L", "XL"],
                "cost_price": 14,
                "list_price": 18,
                "stock": 5,
                "description": "Women Organic Dye Casual Jacket! Elevate your style with this eco-friendly \"Women Organic Dye Casual Jacket.\" Crafted with organic dyes and sustainably sourced materials, this jacket embodies a perfect blend of fashion and environmental consciousness. The soft and breathable fabric ensures comfort without compromising on style. Its pristine white color complements any outfit, making it a versatile addition to your wardrobe. Embrace the essence of modern femininity as you step out in this chic jacket, designed to make a statement at casual gatherings or outings with friends. Embrace sustainability with flair and inspire others to do the same.",
                "image": "https://m.media-amazon.com/images/I/81mrNU4gF3L._AC_SX569_.jpg",
                "category": "Women's Casual"
            },
            {
                "product_id": "",
                "name": "Women Tank Top 100% Recycled Fibers",
                "color_options": ["White", "Blue", "Green"],
                "size_options": ["S", "M", "XL"],
                "cost_price": 6,
                "list_price": 12,
                "stock": 2,
                "description": "Women Tank Top 100% Recycled Fibers! Embrace a greener lifestyle with our \"Women Tank Top 100% Recycled Fibers.\" Made from environmentally friendly materials, this white tank top not only enhances your workout performance but also reduces your carbon footprint. The soft and stretchable fabric provides a comfortable and supportive fit, making it ideal for any active lifestyle. Whether you're hitting the gym, going for a run, or practicing yoga, this tank top ensures you stay cool and dry throughout your workout. Embrace sustainability without compromising on style, and let this tank top be a reflection of your commitment to a healthier planet.",
                "image": "https://m.media-amazon.com/images/I/61a9kY47XPL._AC_SX679_.jpg",
                "category": "Women's Sportswear"
            },
        ]
        # stripe payment
        for product in placeholder_data:
            try:
                stripe_product = stripe.Product.create(
                    name=product["name"],
                    default_price_data={
                        "unit_amount": int(product["list_price"] * 100),
                        "currency": "sgd",
                    },
                    expand=["default_price"],
                )
                product["product_id"] = stripe_product['id']

            except Exception as e:
                print(f"Failed to create product {product['product_id']}: {str(e)}")

        db = shelve.open(db_path, 'c')
        for data in placeholder_data:
            product = Product(
                data["product_id"],
                data["name"],
                data["color_options"],
                data["size_options"],
                float(data["cost_price"]),
                float(data["list_price"]),
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




@app.route('/admin/delete_review/<review_id>', methods=['POST'])
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
    # Assuming reviews are stored in the 'review' shelve
    review_list = list(db.values())
    db.close()

    return render_template('Admin/transaction/review.html', review_list=review_list, count=len(review_list))


@app.route('/admin/code')
def promocode():
    code_list = []
    db_path = 'Objects/transaction/promo.db'

    if not os.path.exists(db_path):
        db = shelve.open(db_path, 'c')
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

#Customer Service
@app.route('/RecordDetailAdmin/<record_id>')
def RecordDetailAdmin(record_id):
    # Find the record with the given record_id
    with shelve.open("service_records_admin.db", writeback=True) as service_records_admin_db:
        record = service_records_admin_db.get(record_id)
        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        subject = record.subject
        chat = record.chat
        date = record.date
        status = record.status
        auto = record.auto

        # Parse the string as a list of dictionaries
        chat_list = json.loads(chat)
        # Initialize lists to store senders and contents
        senders = []
        contents = []

        # Loop through the list of dictionaries to retrieve the sender and content
        for entry in chat_list:
            sender = entry['sender']
            content = entry['content']
            senders.append(sender)
            contents.append(content)

        return render_template('/Admin/custservice/RecordDetailAdmin.html', record=record, senders=senders, contents=contents,
                               subject=subject, date=date, status=status, auto=auto)

@app.route('/ServiceRecordAdmin')
def ServiceRecordAdmin():
    with shelve.open("service_records_admin.db", writeback=True) as service_records_admin_db:
        return render_template('/Admin/custservice/ServiceRecordAdmin.html', service_records=service_records_admin_db)

@app.route('/delete_record_admin/<record_id>', methods=['DELETE'])
def delete_record_admin(record_id):
    # Check if the record_id exists in the service_records dictionary
    with shelve.open("service_records_admin.db", writeback=True) as service_records_admin_db:
        if record_id in service_records_admin_db:
            # If the record exists, delete it from the dictionary
            deleted_record_admin_ids.add(record_id)
            with shelve.open("deleted_records_admin.db") as deleted_records_admin_db:
                deleted_records_admin_db['deleted_record_admin_ids'] = deleted_record_admin_ids
            del service_records_admin_db[record_id]
            return jsonify({'message': 'Record deleted successfully'})
        else:
            # If the record_id does not exist, return an error message
            return jsonify({'error': 'Record not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
