import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, send_file
import shelve
import sys
import os
from datetime import datetime
import time
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


    # Fetch the product details from the database
    db_path = 'Objects/transaction/product.db'
    db = shelve.open(db_path, 'r')
    product = db.get(product_id)
    default_quantity = 1
    default_color = product.color_options[0]
    default_size = product.size_options[0]
    db.close()

    quantity = int(request.form.get('quantity', default_quantity))
    size = request.form.get('size', default_size)
    color = request.form.get('color', default_color)

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

@app.route('/updateshippingforexpcheckout', methods=['POST'])
def updateshippingforexpcheckout():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    try:
        data = request.get_json()
        if data is None:
            # Handle error here, e.g. return a response with a 400 status code
            return "Bad Request", 400
        shipping = data.get('shipping')
        if shipping is None:
            # Handle error here, e.g. return a response with a 400 status code
            return "Bad Request", 400
        session["shipping"] = shipping
        payment_intent_id = session["payment_intent_id"]
        new_total_cost = int(float(calculate_total_cost(cartobj.cart_items, shipping)) * 100)
        shipping_cost = 5 if shipping == "Standard Delivery" else 10
        print(shipping_cost)
        intent = stripe.PaymentIntent.modify(
            payment_intent_id,
            amount=new_total_cost
        )
        return jsonify({
            'clientSecret': intent['client_secret'],
            'amount' : new_total_cost,
            'shipping_cost' : shipping_cost
        })
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 400

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
    cartobj.cart_items = list(combined_items.values())

    # Convert the dictionary of combined items back to a list
    combined_cart_items = list(combined_items.values())

    cart_total = cartobj.get_cart_total()

    session_cart_items = []
    for item in cart_items:
        session_cart_items.append(item.to_dict())

    session['intent_metadata'] = session_cart_items
    session['code_dict'] = {}
    session['shipping'] = 5

    return render_template('Customer/transaction/Cart.html', cart_items=combined_cart_items, cart_total=cart_total, num_items_in_cart=num_items_in_cart)

@app.route('/payment', methods=['GET'])
def display_payment():
    cart_items = cartobj.get_cart_items()
    line_items = []
    db_file = 'Objects/transaction/promo.db'
    allow_promo = os.path.isfile(db_file)
    for item in cart_items:
        line_item = {
            'price': find_product(item.name, item.color, item.size)["default_price"],
            'quantity': item.quantity,
            'adjustable_quantity': {"enabled": True, "minimum": 1, "maximum": 99},
            }
        
        line_items.append(line_item)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=Domain + 'thankyou',
            cancel_url=Domain + 'product',
            automatic_tax={'enabled': True},
            allow_promotion_codes=allow_promo,
            shipping_address_collection={
                'allowed_countries': ['SG'],
            },
            shipping_options=[{
                'shipping_rate_data': {
                    'display_name': 'Standard Delivery',
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 500,
                        'currency': 'sgd',
                    },
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'day',
                            'value': 1
                        },
                        'maximum': {
                            'unit': 'day',
                            'value': 3
                        },
                    },
                },
            },
            {
                'shipping_rate_data': {
                    'display_name': 'Express Delivery',
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 1000,
                        'currency': 'sgd',
                    },
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'hour',
                            'value': 6
                        },
                        'maximum': {
                            'unit': 'day',
                            'value': 1
                        },
                    },
                },
            }],
        )
        session['checkout_session_id'] = checkout_session.id
        code_dict = {}
        for code in stripe.PromotionCode.list()["data"]:
            code_data={}
            code_data["code_id"] = code["id"]
            code_data["times_redeemed"] = code["times_redeemed"]
            code_dict[code["id"]] = code_data
        session["code_dict"] = code_dict
        if code_data["times_redeemed"] < 2:
            print(f"promo code 20OFF has {code_data['times_redeemed']} times redeemed")

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

Domain = "https://confunius-sturdy-space-guide-9pwww99p7vqfxrqw-5000.app.github.dev/"

@app.route('/totalcostcalculator')
def calculate_total_cost(cart_items, delivery_option):
    subtotal = 0
    for item in cart_items:
        subtotal += item.price * item.quantity
    shipping_costs = 5 if delivery_option == 'Standard Delivery' else 10

    total_cost = subtotal + shipping_costs
    return total_cost

@app.route('/create_intent', methods=['POST'])
def create_intent():
    cart = session['intent_metadata']
    cart_json = json.dumps(cart)

    session.pop('intent_metadata', None)
    amount = int(float(calculate_total_cost(cartobj.cart_items, 'Standard Delivery')) * 100)
    intent = stripe.PaymentIntent.create(
        amount = amount,  # Stripe expects the amount in cents
        currency='sgd',
        automatic_payment_methods={
            'enabled': True,
        },
        metadata={
            'cart': cart_json,
        }
    )

    session['payment_intent_id'] = intent['id']
    return jsonify({
        'clientSecret': intent['client_secret'],
        'amount' : amount
    })

@app.route('/thankyou')
def thankyou():

    # Retrieve cart items and promo code discount (if applicable) from the cart object
    product_db_path = 'Objects/transaction/product.db'
    order_db_path = 'Objects/transaction/order.db'
    checkout_info = stripe.checkout.Session.retrieve(session['checkout_session_id'])
    print(checkout_info)
    # checkout_line_items = stripe.checkout.Session.list_line_items(checkout_info['id'])
    subtotal = float(checkout_info['amount_subtotal']/100)
    total_cost = float(checkout_info['amount_total']/100)
    order_id = checkout_info['payment_intent']
    # payment_intent = stripe.PaymentIntent.retrieve(order_id)
    shipping_costs = float(checkout_info['shipping_cost']['amount_total']/100)
    shipping_rate_id = checkout_info['shipping_cost']['shipping_rate']
    delivery_option = stripe.ShippingRate.retrieve(shipping_rate_id)['display_name']
    shipping_details_dict = checkout_info['shipping_details']
    shipping_address = f"{shipping_details_dict['address']['line1']}, {shipping_details_dict['address']['line2']}, {shipping_details_dict['address']['country']}"
    
    # Create new code_dict after purchase
    code_dict = {}
    for code in stripe.PromotionCode.list()["data"]:
        code_data={}
        code_data["code_id"] = code["id"]
        code_data["code"] = code["code"]
        code_data["times_redeemed"] = code["times_redeemed"]
        code_data["percent_off"] = code["coupon"]["percent_off"]
        code_dict[code["id"]] = code_data

    # retrieve times_redeemed before purchase
    old_code_dict = session["code_dict"]
    promo_code_discount_pct = 0
    promo_code = ""
    
    for old_code_id, old_code_data in old_code_dict.items():
        old_times_redeemed = old_code_data["times_redeemed"]
        # check times_redeemed after purchase to see if there are any increases
        for code_id, code_data in code_dict.items():
            if code_id == old_code_id:
                new_times_redeemed = code_data["times_redeemed"]
                if new_times_redeemed > old_times_redeemed:
                    promo_code_discount_pct = code_data["percent_off"]/100
                    promo_code = code_data["code"]
                    print(f"promo_code chosen: {code_data['code']}'s new_times_redeemed {new_times_redeemed} > old_times_redeemed {old_times_redeemed} ")
                else:
                    promo_code_discount_pct = 0
    print(f"code_discount: {promo_code_discount_pct}, promo_code: {promo_code}")
    if promo_code_discount_pct == 0:
        promo_code_discount = 0
        promo_code = 'N/A'
        print("No promo code applied")
    else:
        promo_code_discount = promo_code_discount_pct * subtotal

    # Close sessions
    session.pop('checkout_session_id', None)
    session.pop('code_dict', None)
    cart_items = cartobj.cart_items
    cartobj.cart_items = []

    # Create product_dict and a list of product_ids
    product_dict = {}
    with shelve.open(product_db_path) as product_db:
        for key in product_db:
            product = product_db[key]
            product_dict[key] = product
    product_id_list = []
    size = []
    color = []
    quantity = []
    for item in cart_items:
        product_id_list.append(item.product_id)
        size.append(item.size)
        color.append(item.color)
        quantity.append(item.quantity)
    # Create new order object
    user_id = 0
    order_date = datetime.now().date()
    order_status = "processing"
    order = Order(order_id, user_id, product_id_list, size, color, quantity, order_date, delivery_option, promo_code, order_status)
    with shelve.open(order_db_path) as db:
        db[order_id] = order


    return render_template('Customer/transaction/Thankyou.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost, delivery_option=delivery_option,
                           shipping_address=shipping_address, product_dict=product_dict,
                             order_id=order_id)


@app.route('/cancel_and_refund/<order_id>', methods=['GET'])
def cancel_and_refund(order_id):
    # Fetch the order_id from the session or some other mechanism
    db_path = 'Objects/transaction/order.db'

    if order_id:
        # Open the shelve database
        db = shelve.open(db_path, 'w')
        # Delete the order from the database
        orderobj = db[order_id]
        orderobj.order_status = "cancelled"
        try:
            stripe.Refund.create(
                payment_intent=order_id,
            )
            orderobj.order_status = "refunded"
        except:
            print("Refund failed")

        db[order_id] = orderobj
        # Close the shelve database
        db.close()

    return render_template('Customer/transaction/CancelRefund.html')

# Customer Service
with shelve.open("custservice_deleted_records.db") as custservice_deleted_records_db:
    deleted_record_ids = custservice_deleted_records_db.get('deleted_record_ids', set())

with shelve.open("custservice_deleted_records_admin.db") as custservice_deleted_records_admin_db:
    deleted_record_admin_ids = custservice_deleted_records_admin_db.get('deleted_record_ids', set())

# Add any other methods or attributes required for your Record class
def get_total_record_count():
    with shelve.open("service_records.db") as service_records_db:
        # Get the count of current records
        current_count = len(service_records_db)

    with shelve.open("custservice_deleted_records.db") as custservice_deleted_records_db:
        # Get the count of deleted records
        deleted_count = len(custservice_deleted_records_db.get('deleted_record_ids', set()))

    # Calculate the total count by adding current and deleted records
    total_count = current_count + deleted_count
    return total_count
    
@app.route('/FAQ')
def FAQ():
    with shelve.open("faqs.db") as db:
        faqs = db.get("faqs", [])
    return render_template('/Customer/custservice/FAQ.html', faqs=faqs)

@app.route('/get_csv')
def get_csv():
    csv_file_path = r'C:\Users\ethan\Downloads\profanity_en.csv'
    return send_file(csv_file_path, as_attachment=True)
    
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
        user = record.user_id

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
                               subject=subject, date=date, status=status, auto=auto, user_id=user)
   

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
                auto=data['auto'],
                user_id="Real"
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
                    auto=data['auto'],
                    user_id=["Real"]
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
            with shelve.open("custservicedeleted_records.db") as custservice_deleted_records_db:
                custservice_deleted_records_db['deleted_record_ids'] = deleted_record_ids
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
    max_id = 0
    for key in db:
        if int(key) > max_id:
            max_id = int(key)
    product_id = "P" + int(max_id + 1)

    product = Product(product_id, name, color_options, size_options, cost_price,
                          list_price, stock, description, image, category)
        # stripe payment
    for color in product["color_options"]:
        for size in product["size_options"]:
            try:
                stripe_details = stripe.Product.create(
                    name=f"{product['name']} | {color} | {size}",
                    default_price_data={
                        "unit_amount": int(float(list_price) * 100),
                        "currency": "sgd",
                    },
                    images=[product["image"]],
                )
                stripe.Product.modify(
                    stripe_details["id"],
                    url=Domain+"/product/"+product["id"],
                )
            except Exception as e:
                print(f"Failed to create product {product['product_id']}: {str(e)}")
    product_id = product["id"]
    db[product_id] = product
    db.close()



    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/admin/update_product/<product_id>', methods=['POST'])
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

    # Find the base product
    base_product = find_product(name)

    base_product = base_product[0]  # Assuming find_product returns a list

    # Save the old default price ID
    old_default_price_id = base_product['default_price']

    # Create a new price for the base product
    default_price = stripe.Price.create(
        product=base_product['id'],
        unit_amount=int(float(list_price) * 100),
        currency="sgd",
    )

    stripe.Product.modify(base_product['id'], default_price = default_price['id'])
    # Now you should be able to archive the old default price
    stripe.Price.modify(old_default_price_id, active=False)

    # Now handle the product variants
    for color in color_options:
        for size in size_options:
            variant_name = f"{name} | {color} | {size}"

            # Check if the variant already exists
            variant_product = find_product(variant_name)

            if variant_product is None:
                # If the variant doesn't exist, create it
                variant_product = stripe.Product.create(name=variant_name)

            variant_product = variant_product[0]  # Assuming find_product returns a list

            # Create a new price for the variant
            variant_price = stripe.Price.create(
                product=variant_product['id'],
                unit_amount=int(float(list_price) * 100),
                currency="sgd",
            )

            # Save the old default price ID for the variant
            old_default_price_id = variant_product['default_price']

            stripe.Product.modify(variant_product['id'], default_price = variant_price['id'])

            # Now you should be able to archive the old default price for the variant
            stripe.Price.modify(old_default_price_id, active=False)

    db.close()

    # Redirect back to the product page
    return redirect(url_for('product_admin'))


@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Open the shelve database
    db = shelve.open('Objects/transaction/product.db', 'w')

    # Check if the product_id exists in the database
    if product_id in db:
        # Delete the product from the database
        product = db[product_id]
        product_name = product.name
        stripe_product_list = find_product(product_name)
        for item in stripe_product_list:
            stripe.Product.delete(item["id"])
        del db[product_id]
        db.close()
    
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
                "product_id": "P1",
                "name": "Men 100% Cotton Linen Long Sleeve Shirt",
                "color_options": ["White", "Green"],
                "size_options": ["M", "L"],
                "cost_price": 8,
                "list_price": 16,
                "stock": 3,
                "description": "Introducing the \"Men 100% Cotton Linen Long Sleeve Shirt\"! Crafted with the finest blend of cotton and linen, this classic white shirt boasts both style and comfort. Perfect for casual outings or semi-formal occasions, its long sleeves add an air of sophistication to any ensemble. The breathable fabric ensures you stay cool and relaxed all day long. Embrace a timeless, versatile look with this essential wardrobe piece that pairs effortlessly with jeans, chinos, or tailored trousers. Designed to exude elegance and confidence, this shirt is a must-have for every fashion-forward gentleman. Get ready to make a lasting impression.",
                "image": "https://m.media-amazon.com/images/I/615Cby-DciL._AC_SX679_.jpg",
                "category": "Men's Casual"
            }
            # {
            #     "product_id": "P2",
            #     "name": "Women Organic Dye Casual Jacket",
            #     "color_options": ["White", "Blue"],
            #     "size_options": ["S", "L"],
            #     "cost_price": 14,
            #     "list_price": 18,
            #     "stock": 5,
            #     "description": "Women Organic Dye Casual Jacket! Elevate your style with this eco-friendly \"Women Organic Dye Casual Jacket.\" Crafted with organic dyes and sustainably sourced materials, this jacket embodies a perfect blend of fashion and environmental consciousness. The soft and breathable fabric ensures comfort without compromising on style. Its pristine white color complements any outfit, making it a versatile addition to your wardrobe. Embrace the essence of modern femininity as you step out in this chic jacket, designed to make a statement at casual gatherings or outings with friends. Embrace sustainability with flair and inspire others to do the same.",
            #     "image": "https://m.media-amazon.com/images/I/81mrNU4gF3L._AC_SX569_.jpg",
            #     "category": "Women's Casual"
            # },
            # {
            #     "product_id": "P3",
            #     "name": "Women Tank Top 100% Recycled Fibers",
            #     "color_options": ["White", "Red"],
            #     "size_options": ["S", "M"],
            #     "cost_price": 6,
            #     "list_price": 12,
            #     "stock": 2,
            #     "description": "Women Tank Top 100% Recycled Fibers! Embrace a greener lifestyle with our \"Women Tank Top 100% Recycled Fibers.\" Made from environmentally friendly materials, this white tank top not only enhances your workout performance but also reduces your carbon footprint. The soft and stretchable fabric provides a comfortable and supportive fit, making it ideal for any active lifestyle. Whether you're hitting the gym, going for a run, or practicing yoga, this tank top ensures you stay cool and dry throughout your workout. Embrace sustainability without compromising on style, and let this tank top be a reflection of your commitment to a healthier planet.",
            #     "image": "https://m.media-amazon.com/images/I/61a9kY47XPL._AC_SX679_.jpg",
            #     "category": "Women's Sportswear"
            # },
        ]
        # stripe payment
        for product in placeholder_data:
            for color in product["color_options"]:
                for size in product["size_options"]:
                    try:
                        stripe_details = stripe.Product.create(
                            name=f"{product['name']} | {color} | {size}",
                            default_price_data={
                                "unit_amount": int(product["list_price"] * 100),
                                "currency": "sgd",
                            },
                            images=[product["image"]],
                        )
                        # stripe.Product.modify(
                        #     stripe_details["id"],
                        #     url=Domain+"/product/"+product["id"],
                        # )
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

def find_product(name, color=None, size=None):
    matching_products = []
    stripe_product_dict = stripe.Product.list()["data"]
    for product in stripe_product_dict:
        product_name = product["name"]
        if color and size:
            # if color and size are specified, check for exact match
            if product_name == f"{name} | {color} | {size}":
                return product
        else:
            # if color and size are not specified, check if the product name matches
            if name in product_name:
                matching_products.append(product)
    return matching_products if matching_products else None

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
        date = datetime.strptime(str(end_date), '%Y-%m-%d')
        db = shelve.open('Objects/transaction/promo.db', 'w')
        unix_timestamp = int(time.mktime(date.timetuple()))
        if code not in db:
            coupon = stripe.Coupon.create(
                percent_off = discount,
                duration = 'once',
                redeem_by = unix_timestamp,
            )
            promocode = stripe.PromotionCode.create(
                coupon = coupon['id'],
                code = code, 
            )
            promo = Code(code, discount, end_date, coupon['id'], promocode['id'])
            db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))


@app.route('/admin/update_code/<code>', methods=['POST'])
def update_code(code):
    if request.method == 'POST':
        discount = float(request.form['discount'])
        end_date = request.form['end_date']
        date = datetime.strptime(str(end_date), '%Y-%m-%d')
        unix_timestamp = int(time.mktime(date.timetuple()))
        db = shelve.open('Objects/transaction/promo.db', 'w')
        stripe.Coupon.delete(db[code].coupon_id)
        coupon = stripe.Coupon.create(
            percent_off = discount,
            duration = 'once',
            redeem_by = unix_timestamp,
        )
        promocode = stripe.PromotionCode.create(
            coupon = coupon['id'],
            code = code,
        )
        promo = Code(code, discount, end_date, coupon['id'], promocode['id'])
        db[promo.code] = promo
        db.close()
    return redirect(url_for('promocode'))


@app.route('/admin/delete_code/<code>', methods=['POST'])
def delete_code(code):
    db = shelve.open('Objects/transaction/promo.db', 'w')
    if code in db:
        stripe.Coupon.delete(db[code].coupon_id)
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
        user = record.user_id

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
                               subject=subject, date=date, status=status, auto=auto, user=user)

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
            with shelve.open("custservice_deleted_records_admin.db") as custservice_deleted_records_admin_db:
                custservice_deleted_records_admin_db['deleted_record_admin_ids'] = deleted_record_admin_ids
            del service_records_admin_db[record_id]
            return jsonify({'message': 'Record deleted successfully'})
        else:
            # If the record_id does not exist, return an error message
            return jsonify({'error': 'Record not found'}), 404
def get_faqs_from_shelve():
    with shelve.open("faqs.db") as db:
        return db.get("faqs", [])

def save_faqs_to_shelve(faqs):
    with shelve.open("faqs.db") as db:
        db["faqs"] = faqs

@app.route('/FAQAdmin', methods=['GET', 'POST'])
def FAQAdmin():
    if request.method == 'POST':
        # Get the new section, question, and answer from the form submitted
        new_section = request.form['new_section']
        new_question = request.form['new_question']
        new_answer = request.form['new_answer']

        # Retrieve the FAQs from the shelve database
        faqs = get_faqs_from_shelve()

        # Find the section in the existing FAQs or add a new one
        for section_data in faqs:
            if section_data['section'] == new_section:
                section_data['questions'].append(new_question)
                section_data['answers'].append(new_answer)
                break

        # Save the updated FAQs back into the shelve database
        save_faqs_to_shelve(faqs)

    # Retrieve the FAQs from the shelve database
    faqs = get_faqs_from_shelve()

    return render_template('FAQAdmin.html', faqs=faqs)

@app.route('/update_faq', methods=['POST'])
def update_faq():
    # Handle form submission for updating question and answer
    section_to_update = request.form['update_section']
    index = int(request.form['update_index'])
    updated_question = request.form['update_question']
    updated_answer = request.form['update_answer']
    faqs = get_faqs_from_shelve()
    # Update the question and answer in the list under the specified section
    for section in faqs:
        if section['section'] == section_to_update:
            section['questions'][index] = updated_question
            section['answers'][index] = updated_answer
    save_faqs_to_shelve(faqs)

    # Redirect back to the FAQAdmin page after updating the question and answer
    return redirect('/FAQAdmin')

@app.route('/delete_faq', methods=['POST'])
def delete_faq():
    section = request.form['section']
    index = int(request.form['index'])
    # Retrieve the FAQs from the shelve database
    faqs = get_faqs_from_shelve()

    # Delete the question and answer from the FAQs list using the section and index
    for section_data in faqs:
        if section_data['section'] == section:
            del section_data['questions'][index]
            del section_data['answers'][index]
            break
    save_faqs_to_shelve(faqs)

    return redirect('/FAQAdmin')

if __name__ == '__main__':
    app.run(debug=True)
