from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, flash
import shelve
import sys, os
from datetime import datetime
# current_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = os.path.dirname(current_dir)
# sys.path.append(main_dir)
# Importing Objects
from markupsafe import Markup
from flask_wtf import FlaskForm,RecaptchaField
from Objects.transaction.Product import Product  # it does work
from Objects.transaction.Order import Order
from Objects.transaction.Review import Review
from Objects.transaction.code import Code
from Objects.transaction.cart import Cart, CartItem
from Forms import *
import flash
from dataclasses import dataclass, field
# sys.path.remove(main_dir)
import Customer
import Admin
import requests
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
from flask_wtf.recaptcha import RecaptchaField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SENDGRID_API_KEY'] = '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'
app.secret_key = 'your_secret_key_here'  # Replace with your own secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcmcpEnAAAAAHxJ65HrhNMxZyew7i11rbhtOcpp'  # Add this line
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcmcpEnAAAAAJMyWO81WUlszsiT2dVifAvP9YWq'
app.config['RECAPTCHA_VERIFY_URL'] = 'https://www.google.com/recaptcha/api/siteverify'
SITE_KEY = "6LfarpAnAAAAAARa-mm-fxaT-ELv4SOygA8tX687"
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
SECRET_KEY = '6LfarpAnAAAAAPnX52zucGBcrqBXduANOx9gEFbc'


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

def generate_time_for_timeseries():
    return str(datetime.now().replace(minute=0, second= 0, microsecond=0))

def send_verification_email(email):
    sg = sendgrid.SendGridAPIClient(api_key=app.config['SENDGRID_API_KEY'])
    verification_link = f"http://127.0.0.1:5000/verify_email?email={email}"
    message = Mail(
        from_email=From('sam.bryant29@gmail.com'),
        to_emails=To(email),
        subject='Email Verification',
        html_content=f'Thank you for registering for our FashionHub membership.<br>If this was not done by you, please ignore this email.<br><br>Please click this to <a href="{verification_link}">verify</a> your account.<br><br>Best Regards,<br> FashionHub Accounts Department<br><img src="https://thumbs.dreamstime.com/z/sustainable-fashion-logo-eco-friendly-production-label-icon-badge-clothes-hanger-green-leaves-natural-recycling-215122758.jpg" width="120" height="120"></img>'
    )
    try:
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


@app.route('/verify_email', methods=['GET'])
def verify_email():
    email = request.args.get('email')
    # Add code to verify the email address and update userVerified column accordingly in your database.
    # For simplicity, we'll just set userVerified to 1 here.
    db = shelve.open('shelvefile.db', 'w')
    users_dict = db.get('users', {})

    for user in users_dict.values():
        if user.get_userEmail() == email:
            userVerified = 1
            user.set_userVerified(userVerified)
            db['users'] = users_dict
            db.close()
            return render_template('/User/verifiedEmailThankYou.html')

    db.close()
    return "Email verification failed. User not found."

@dataclass
class User:
    user_id: str
    userName: str
    userEmail: str
    userPassword: str
    userCfmPassword: str

def generate_time_for_timeseries():
    return str(datetime.now().replace(minute=0, second= 0, microsecond=0))

# Home
@app.route('/')
def home():
    return render_template('/User/homepage.html')

@app.route('/Logout', methods=['GET','POST'])
def Logout():
    session.clear()
    return render_template('/User/homepage.html')
# User side
@app.route('/Login', methods=['GET','POST'])
def Login():
    create_user_form = userLogin(request.form)
    if request.method == "POST" and create_user_form.validate():
        db = shelve.open('shelvefile.db', 'r')
        users_dict = db.get('users', {})  # Use a default empty dict if 'users' doesn't exist yet

        email = create_user_form.userEmail.data
        password = create_user_form.userPassword.data

        for key, user_data in users_dict.items():
            if user_data.get_userEmail() == email and user_data.get_userPassword() == password:
                if user_data.get_userVerified() == 1:
                    session['id'] = key
                    session['userfullname'] = user_data.get_userFullName()
                    session['username'] = user_data.get_userName()
                    session['useremail'] = user_data.get_userEmail()
                    session['useraddress'] = user_data.get_userAddress()
                    session['userpostalcode'] = user_data.get_userPostalCode()
                    session['user_logged_in'] = True
                    db.close()
                    return redirect(url_for('CustomerHomepage'))
                else:
                    #flash("Please verify/create your account.", category="danger")
                    return render_template('/User/account/LoginPage.html', form=create_user_form)

        admin_dict = db.get('admins', {})
        # Handle admin login here (similar to user login)
        admin_email = create_user_form.userEmail.data #It doesn't matter as it is borrowing the fields not the
                                                    #corresponding assigned "variable" in forms.py Programming essential
        admin_password = create_user_form.userPassword.data

        # Check if the admin credentials are valid (you can implement your admin login logic here)
        for key, admin_data in admin_dict.items():
            if admin_data.get_adminEmail() == admin_email and admin_data.get_adminPassword() == admin_password:
                if admin_data.get_adminVerified() == 'deactivated':
                    #flask.flash("Your account has been deactivated. Please contact an administrator to reactivate your account.", category="danger")
                    return render_template('/User/account/LoginPage.html', form=create_user_form)
                else:
                    session['id'] = key
                    session['adminfname'] = admin_data.get_adminFirstName()
                    session['adminlname'] = admin_data.get_adminLastName()
                    session['adminusername'] = admin_data.get_adminUserName()
                    session['adminemail'] = admin_data.get_adminEmail()
                    session['phonenumber'] = admin_data.get_adminPhoneNumber()
                    session['admin_logged_in'] = True
                    db.close()
                    return redirect(url_for('ahome'))
    return render_template('/User/account/LoginPage.html', form=create_user_form)


    # create_user_form = userLogin(request.form)
    # create_admin_form = adminLogin(request.form)
    # if request.method == "POST" and create_user_form.validate():
    #
    #     db = shelve.open('shelvefile.db', 'r')
    #     users_dict = {}
    #     try:
    #         users_dict = db['users'] #user_dict = {1:UserObject, 2:UserObject} #take everything out
    #     except:
    #         db["users"] = users_dict
    #         print("Error in retrieving Users from shelvefile.db")
    #
    #     email = create_user_form.userEmail.data
    #     password = create_user_form.userPassword.data
    #
    #     for key in users_dict:
    #         userschecklist = users_dict[key]
    #         if userschecklist.get_userEmail() == email and  userschecklist.get_userPassword() == password:
    #             #tempKey = key #Used for /userProfile
    #             session['id'] = userschecklist.get_user_id()
    #             session['username'] = userschecklist.get_userName()
    #             session['useremail'] = userschecklist.get_userEmail()
    #             session['useraddress'] = userschecklist.get_userAddress()
    #             session['userpostalcode'] = userschecklist.get_userPostalCode()
    #             return redirect(url_for('CustomerHomepage')) #Looks for function in the python routing
    #     return render_template('/User/account/LoginPage.html', form=create_user_form)
    # return render_template('/User/account/LoginPage.html', form=create_user_form)


@app.route('/CustomerHomepage')
def CustomerHomepage():
    return render_template('/User/LoggedInHomepage.html')

#@app.route('/CustomerLogin', methods=['GET','POST'])
#def CustomerLogin():


@app.route('/UserRegistrationPage', methods=['GET', 'POST'])
def UserRegistrationPage():
    create_user_form = createUser(request.form)
    if request.method == "POST":
        # if not request.form.get("user_id")\
        #     or not request.form.get("userName")\
        #     or not request.form.get("userEmail")\
        #     or not request.form.get("userPassword")\
        #     or not request.form.get("userCfmPassword"):
        #         flash("All fields are required to sign up")
        db = shelve.open('shelvefile.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users'] #user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from shelvefile.db")

        userPassword = create_user_form.userPassword.data
        userCfmPassword = create_user_form.userCfmPassword.data
        if not userPassword == userCfmPassword:
            flash("Passwords Don't match", category="danger")
            return redirect("/CustomerRegistration")

        user = Customer.User(create_user_form.userFullName.data, create_user_form.userName.data, create_user_form.userPassword.data,
                             create_user_form.userEmail.data, create_user_form.userCfmPassword.data,
                             create_user_form.userAddress.data, create_user_form.userPostalCode.data)

        users_dict[user.get_user_id()] = user #users_dict[3] = user // user_dict = {1:user, 3:user}
        db['users'] = users_dict #put everything back
        #users = shelf["users"].values()
        #if userName in list(map(lambda x: x.username, users)):
        #    flash(Markup('Username already exists., <a href="/user_login">Login?</a>',),category="danger")

        #new_user = User(user_id, userName, userEmail, userPassword, userCfmPassword)
        #shelf["users"][user_id] = user
        #shelf["account_creation_history"][generate_time_for_timeseries()] += 1
        #flash("Account created successfully",category="success")
        #shelf.sync()
        db.close()
        send_verification_email(create_user_form.userEmail.data)
        recaptcha_response = request.form.get('g-recaptcha-response')
        verify_payload = {
            'secret': SECRET_KEY,
            'response': recaptcha_response
        }
        verify_response = requests.post(url=VERIFY_URL, data=verify_payload).json()
        #flash('A verification email has been sent. Please check your inbox.', category='success')
        return redirect("/Login")
    return render_template('/User/account/CustomerRegistration.html', form=create_user_form, site_key=SITE_KEY)



@app.route('/UserHomepage')
def UserHomepage():
    return render_template('/User/LoggedInHomepage.html')
# Account
@app.route('/UserProfile')
def UserProfile():
    return render_template('/User/account/usersettings.html')

@app.route('/OrderStatus')
def OrderStatus():
    return render_template('/User/account/orderstatus.html')

@app.route('/OrderHistory')
def OrderHistory():
    return render_template('/User/account/orderhistory.html')

@app.route('/Wishlist')
def Wishlist():
    return render_template('/User/account/wishlist.html')

@app.route('/CustomerAccountDelete')
def CustomerAccountDelete():
    return render_template('User/account/accountdelete.html')

@app.route('/EditCustomerAccount/<int:id>/', methods=['GET', 'POST']) #refer to usersettings "href"
def EditCustomerAccount(id):
    edit_user_form = userEditInfo(request.form)
    if request.method == 'POST' and edit_user_form.validate():
        db = shelve.open('shelvefile.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from shelvefile.db")

        tempUser = users_dict[id]
        tempUser.set_userFullName(edit_user_form.userFullName.data)
        tempUser.set_userName(edit_user_form.userName.data)
        tempUser.set_userEmail(edit_user_form.userEmail.data)
        tempUser.set_userAddress(edit_user_form.userAddress.data)
        tempUser.set_userPostalCode(edit_user_form.userPostalCode.data)

        session['userfullname'] = tempUser.get_userFullName()
        session['username'] = tempUser.get_userName()
        session['useremail'] = tempUser.get_userEmail()
        session['useraddress'] = tempUser.get_userAddress()
        session['userpostalcode'] = tempUser.get_userPostalCode()

        users_dict[id] = tempUser
        db['users'] = users_dict
        db.close()

        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('shelvefile.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(id)
        edit_user_form.userFullName.data = user.get_userFullName()
        edit_user_form.userName.data = user.get_userName()
        edit_user_form.userEmail.data = user.get_userEmail()
        edit_user_form.userAddress.data = user.get_userAddress()
        edit_user_form.userPostalCode.data = user.get_userPostalCode()
        return render_template('User/account/editinfo.html', form=edit_user_form)


    #if request.method == 'POST' and edit_user_form.validate():
        # Update user data in the shelve database
    #    db = shelve.open('shelvefile.db', 'c')
    #    users_dict = db.get('users', {})

        # Retrieve user data from the session
    #    email = session['email']

        # Update user data in the shelve database
    #    for key, user in users_dict.items():
    #        if user.get_userEmail() == email:
    #            user.set_userName(edit_user_form.userName.data)
    #            user.set_userEmail(edit_user_form.userEmail.data)
    #            user.set_userAddress(edit_user_form.userAddress.data)
    #            user.set_userPostalCode(edit_user_form.userPostalCode.data)
    #            break

    #    db['users'] = users_dict
    #    db.close()

        # Redirect to the user profile page or another appropriate page
    #    return redirect(url_for('CustomerHomepage'))
#    return render_template('User/account/editinfo.html', form=edit_user_form)

@app.route('/CustomerChangePassword/<int:id>/', methods=['GET', 'POST'])
def CustomerChangePassword(id):
    edit_user_form = userChangePassword(request.form)
    if request.method == 'POST' and edit_user_form.validate():
        db = shelve.open('shelvefile.db', 'c')
        users_dict = {}
        try:
            users_dict = db['users']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["users"] = users_dict
            print("Error in retrieving Users from shelvefile.db")

        tempUser = users_dict[id]
        tempUser.set_userPassword(edit_user_form.userPassword.data)
        tempUser.set_userCfmPassword(edit_user_form.userCfmPassword.data)

        users_dict[id] = tempUser
        db['users'] = users_dict
        db.close()

        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('shelvefile.db', 'r')
        users_dict = db['users']
        db.close()

        user = users_dict.get(id)
        edit_user_form.userPassword.data = user.get_userPassword()
        edit_user_form.userCfmPassword.data = user.get_userCfmPassword()
        return render_template('User/account/changepw.html', form=edit_user_form)

@app.route('/UserDeletion/<int:user_id>', methods=['POST'])
def user_deletion(user_id):
    db = shelve.open('shelvefile.db', 'w')
    users_dict = db.get('users', {})

    # Check if the user_id exists in the users_dict
    if user_id in users_dict:
        users_dict.pop(user_id)
        db['users'] = users_dict
        db.close()
        session.clear()
        return redirect(url_for('listCustomerAccounts'))
    else:
        db.close()
        return "User not found."

@app.route('/UserDeactivation/<int:user_id>', methods=['POST'])
def user_deactivation(user_id):
    db = shelve.open('shelvefile.db', 'w')
    users_dict = db.get('users', {})

    # Check if the user_id exists in the users_dict
    if user_id in users_dict:
        # Set the user status to 'deactivated' (or any other value to represent deactivation)
        user = users_dict[user_id]
        user.set_userVerified("deactivated")  # Update the status to "deactivated"
        db['users'] = users_dict
        db.close()
        session.clear()
        return render_template('/User/homepage.html')
    else:
        db.close()
        return "User not found."

@app.route('/AdminDeletion/<int:admin_id>', methods=['POST'])
def admin_deletion(admin_id):
    db = shelve.open('shelvefile.db', 'w')
    admins_dict = db.get('admins', {})

    # Check if the admin_id exists in the admins_dict
    if admin_id in admins_dict:
        admins_dict.pop(admin_id)
        db['admins'] = admins_dict
        db.close()
        session.clear()
        return redirect(url_for('listAdminAccounts'))
    else:
        db.close()
        return "Admin not found."

@app.route('/AdminDeactivation/<int:admin_id>', methods=['POST'])
def admin_deactivation(admin_id):
    db = shelve.open('shelvefile.db', 'w')
    admins_dict = db.get('admins', {})

    # Check if the admin_id exists in the admins_dict
    if admin_id in admins_dict:
        # Set the admin status to 'deactivated' (or any other value to represent deactivation)
        admin = admins_dict[admin_id]
        admin.set_adminVerified("deactivated")  # Update the status to "deactivated"
        db['admins'] = admins_dict
        db.close()
        session.clear()
        return redirect(url_for('listAdminAccounts'))
    else:
        db.close()
        return "Admin not found."

@app.route('/LoginPage' ,methods=['POST'])
def Customer_Login():
    return render_template('User/account/LoginPage.html')

@app.route('/CustomerDelete')
def CustomerDelete():
    return render_template('/User/account/CustomerDelete.html')

@app.route('/CustomerInfo')
def CustomerInfo():
    return render_template('/User/account/CustomerInfo.html')

# @app.route('/CustomerUpdate')
# def CustomerUpdate():
#     return render_template('/User/account/CustomerUpdate.html')

@app.route('/CustomerAccounts')
def CustomerAccounts():
    return render_template('/User/account/CustomerAccounts.html')

@app.route('/Profile')
def Profile():
    return render_template('/User/account/Profile.html')

@app.route('/EditProfile')
def EditProfile():
    return render_template('/User/account/EditProfile.html')

@app.route('/Payment/<int:id>',methods=['GET', 'POST'])
def Payment(id):
    create_user_payment = userPaymentMethod(request.form)
    if request.method == "POST" and create_user_payment.validate():
        db = shelve.open('shelvefile.db', 'c')
        users_payment = {}
        try:
            users_payment = db['usersPayment'] #user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["usersPayment"] = users_payment
            print("Error in retrieving Users from shelvefile.db")

        CardDetails = Customer.userPayment(create_user_payment.userFullName.data, create_user_payment.userEmail.data,
                                           create_user_payment.userCardName.data, create_user_payment.userCardType.data,
                                           create_user_payment.userCardNumber.data, create_user_payment.userCardExp.data,
                                           create_user_payment.userCardSec.data, create_user_payment.userAddress.data,
                                           create_user_payment.userPostalCode.data)

        payment_method_dict = users_payment[id] # payment_method_dict = {91:paymentMethodObj, 92:paymentMethodObj, 93:paymentMethodObj, 94: paymentMethodObj}}
        for key in payment_method_dict:
            if payment_method_dict[key] is not None:
                count += 1
            else:
                count = 1

        payment_method_dict[count] = CardDetails
        users_payment[id] = payment_method_dict
        db['userPayment'] = users_payment
        db.close()
        return redirect(url_for('UserProfile'))
    else:
        db = shelve.open('shelvefile.db', 'r')
        users_dict = db['users']
        db.close()

        tempUser = users_dict[id]
        putEmail = tempUser.get_userEmail()
        putAddress = tempUser.get_userAddress()
        putPostalCode = tempUser.get_userPostalCode()


        create_user_payment.userEmail.data = putEmail
        create_user_payment.userAddress.data = putAddress
        create_user_payment.userPostalCode.data = putPostalCode
        return render_template('/User/account/payment.html', form=create_user_payment)

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
    return render_template('/User/transaction/Product.html', product_list=product_list, count=len(product_list))


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
    
    return render_template('/User/transaction/ProductInfo.html', productobj=productobj, review_list=review_list, count=len(review_list), rounded_rating=rounded_rating, size_options=size_options, color_options=color_options)

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

    return render_template('User/transaction/Cart.html', cart_items=combined_cart_items, cart_total=cart_total, num_items_in_cart=num_items_in_cart, size_options=size_options, color_options=color_options)

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
    # promo_code = request.args.get('promo_code')  # Assuming the promo code is passed as a query parameter
    promo_code_discount = 0

    # Get the subtotal
    subtotal = cartobj.get_cart_total()

    # Calculate the total cost to display first
    shipping_costs = 5
    total_cost = subtotal - promo_code_discount + shipping_costs

    return render_template('/User/transaction/PaymentProcess.html', cart_items=cart_items, subtotal=subtotal,
                           promo_code_discount=promo_code_discount, shipping_costs=shipping_costs,
                           total_cost=total_cost)

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
    # email = request.form['email']
    # phone = request.form['phone']
    delivery_option = request.form['delivery_option']
    # address = request.form['address']
    # postal_code = request.form['postal_code']
    # card_number = request.form['card_number']
    # expiry_date = request.form['expiry_date']
    # cvc = request.form['cvc']
    # save_payment = True if 'save_payment' in request.form else False
    promo_code = request.form['promo_code']

    # Process the form data and place the order (Implement your logic here)

    # Redirect to the order confirmation page (replace 'order_confirmation' with the actual route)
    return redirect(url_for('order_confirmation'))


@app.route('/order_confirmation')
def order_confirmation():
    # This route will show the order confirmation page after the payment is processed
    # Implement your logic to display the confirmation page here
    return render_template('User/transaction/OrderConfirmation.html')



# User Service
@app.route('/FAQ')
def FAQ():
    return render_template('/User/custservice/FAQ.html', faqs=faqs)

@app.route('/CustomerService')
def CustomerService():
    return render_template('/User/custservice/CustomerService.html')

@app.route('/ServiceRecord')
def ServiceRecord():
    return render_template('/User/custservice/ServiceRecord.html')




# Admin side

@app.route('/admin')
def ahome():
    if session['admin_logged_in'] == True:
        return render_template('/Admin/AdminLoggedInHomepage.html')
    else:
        return redirect(url_for('login'))
@app.route('/admin/homepage')
def ahomepage():
    return render_template('/Admin/LoginPage.html')


# Account
@app.route('/adminCreation', methods=['GET', 'POST'])
def AdminRegistrationPage():
    create_admin_form = createAdmin(request.form)
    if request.method == "POST" and create_admin_form.validate():
        # if not request.form.get("user_id")\
        #     or not request.form.get("userName")\
        #     or not request.form.get("userEmail")\
        #     or not request.form.get("userPassword")\
        #     or not request.form.get("userCfmPassword"):
        #         flash("All fields are required to sign up")
        db = shelve.open('shelvefile.db', 'c')
        admin_dict = {}
        try:
            admin_dict = db['admins'] #admin_dict = {1:AdminObject, 2:AdminObject} #take everything out
        except:
            db["admins"] = admin_dict
            print("Error in retrieving Users from shelvefile.db")

        adminPassword = create_admin_form.adminPassword.data
        adminCfmPassword = create_admin_form.adminCfmPassword.data
        if not adminPassword == adminCfmPassword:
            flash("Passwords Don't match", category="danger")
            return redirect("/CustomerRegistration")

        admin = Admin.Admin( create_admin_form.adminFirstName.data, create_admin_form.adminLastName.data,
                             create_admin_form.adminUserName.data, create_admin_form.adminPassword.data,
                             create_admin_form.adminEmail.data, create_admin_form.adminCfmPassword.data,
                             create_admin_form.adminPhoneNumber.data)

        admin_dict[admin.get_admin_id()] = admin
        db['admins'] = admin_dict #put everything back
        #users = shelf["users"].values()
        #if userName in list(map(lambda x: x.username, users)):
        #    flash(Markup('Username already exists., <a href="/user_login">Login?</a>',),category="danger")

        #new_user = User(user_id, userName, userEmail, userPassword, userCfmPassword)
        #shelf["users"][user_id] = user
        #shelf["account_creation_history"][generate_time_for_timeseries()] += 1
        #flash("Account created successfully",category="success")
        #shelf.sync()
        db.close()

        return redirect("/Login")
    return render_template('/Admin/account/AdminRegistration.html', form=create_admin_form)

@app.route('/AdminProfile')
def AdminProfile():
    return render_template('/Admin/account/adminProfile.html')

@app.route('/EditAdminAccount/<int:id>/', methods=['GET', 'POST']) #refer to usersettings "href"
def EditAdminAccount(id):
    edit_admin_form = editAdminAccount(request.form)
    if request.method == 'POST' and edit_admin_form.validate():
        db = shelve.open('shelvefile.db', 'c')
        admin_dict = {}
        try:
            admin_dict = db['admins']  # user_dict = {1:UserObject, 2:UserObject} #take everything out
        except:
            db["admins"] = admin_dict
            print("Error in retrieving Users from shelvefile.db")

        tempAdmin = admin_dict[id]
        tempAdmin.set_adminFirstName(edit_admin_form.adminFirstName.data)
        tempAdmin.set_adminLastName(edit_admin_form.adminLastName.data)
        tempAdmin.set_adminEmail(edit_admin_form.adminEmail.data)
        tempAdmin.set_adminPhoneNumber(edit_admin_form.adminPhoneNumber.data)

        session['adminfname'] = tempAdmin.get_adminFirstName()
        session['adminlname'] = tempAdmin.get_adminLastName()
        session['adminemail'] = tempAdmin.get_adminEmail()
        session['phonenumber'] = tempAdmin.get_adminPhoneNumber()

        admin_dict[id] = tempAdmin
        db['admins'] = admin_dict
        db.close()

        return redirect(url_for('AdminProfile'))
    else:
        db = shelve.open('shelvefile.db', 'r')
        admin_dict = db['admins']
        db.close()

        admin = admin_dict.get(id)
        edit_admin_form.adminFirstName.data = admin.get_adminFirstName()
        edit_admin_form.adminLastName.data = admin.get_adminLastName()
        edit_admin_form.adminEmail.data = admin.get_adminEmail()
        edit_admin_form.adminPhoneNumber.data = admin.get_adminPhoneNumber()
        return render_template('Admin/account/editAdminProfile.html', form=edit_admin_form)

@app.route('/listCustomerAccounts')
def listCustomerAccounts():
    users_dict = {}
    db = shelve.open('shelvefile.db', 'r')
    users_dict = db['users']
    db.close()
    users_list = []
    for key in users_dict:
        user = users_dict[key]
        users_list.append(user)
    return render_template('/Admin/account/ListCustomerAccount.html', count=len(users_list), usersList=users_list)

@app.route('/listAdminAccounts')
def listAdminAccounts():
    admins_dict = {}
    db = shelve.open('shelvefile.db', 'r')
    admins_dict = db['admins']
    db.close()
    admins_list = []
    for key in admins_dict:
        admin = admins_dict[key]
        admins_list.append(admin)
    return render_template('/Admin/account/ListAdminAccount.html', count=len(admins_list), adminsList=admins_list)


@app.route('/admin/AdminAccounts')
def AdminAccounts():
    return render_template('/Admin/account/AdminAccounts.html')

# @app.route('/admin/AdminDelete')
# def AdminDelete():
#     return render_template('/Admin/account/AdminDelete.html')

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
                "ship_to": "Singapore",
                "promo_code": "N/A"
            },
            {
                "order_id": "O2",
                "user_id": "U2",
                "product_id": "P2",
                "order_date": "2023-07-22",
                "ship_to": "Singapore",
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

@app.route('/CustomerUpdate', methods=['POST', 'GET'])
def CustomerUpdate():

    return render_template('CustomerUpdate.html')


if __name__ == '__main__':
    app.run(debug=True)
