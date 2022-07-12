from os import path
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from models.db_models import *
import datetime

##
## THE APP
##

# This is the application.
app = Flask(__name__)

##
## CONFIGURATION
##

# Session secret key.
app.config['SECRET_KEY'] = b"B!\x1d\xc6\xb8'\xd6\x97\xe9\xa0\xed\xb1\xe3\x00\xa0\xa1"

# Database configuration.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##
## DATABASE SETUP
##

# Initialize database manager.
db.init_app(app)
 
##
## LOGIN SETUP
##

# Initialize login managers.
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dictionary containing the users currently logged in.
current_users = {}


# Declare the user loader callback for flask_login. Returns the user data for 
# the given user_id. Returns None if no user with this user_id is logged in.
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

##
## ROUTES
##

    
# Deliver the start page of the application.
@app.route('/')
@login_required
def index():
    return redirect(url_for('.generate_invoice_1'))


# Deliver the application icon.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'images/apl.png', mimetype='image/x-icon')

# Authenticate the given user at the configured LDAP server and then
# login the user at this application.
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('username')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    if request.method == 'POST':
        if user:
            flash(f'Welcome {email}', 'success')
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Logout the current user.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/generate_invoice')
@login_required
def generate_invoice():
    customers = Customers.query.all()
    products = Products.query.all()
    return render_template("e-invoicegenerator.html",customers = customers, products = products)

@app.route('/generate_invoice_1')
@login_required
def generate_invoice_1():
    customers = Customers.query.all()
    products = Products.query.all()
    date_time = datetime.datetime.today().strftime('%d-%m-%Y')
    return render_template("invoice_example.html",customers = customers, products = products,date_time=date_time)

@app.route('/manage_customers', methods=['GET'])
@login_required
def manage_customers():
    customers = Customers.query.all()
    return render_template("customers.html", customers = customers)

@app.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('customer-name')
    address = request.form.get('customer-address')
    email = request.form.get('customer-email')
    phone_number = request.form.get('customer-phone')
    new_customer = Customers(name=name, address=address, email=email, phone_number=phone_number)
    try:
        db.session.add(new_customer)
        db.session.commit()
        flash("New customer successfully added", 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash("Some customer details entered are not proper", 'danger')
    return redirect(url_for('manage_customers'))

@app.route('/manage_invoice_items', methods=['GET'])
@login_required
def manage_invoice_items():
    products = Products.query.all()
    return render_template("invoice_items.html", products = products)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    name = request.form.get('item-name')
    price = request.form.get('item-price')
    new_product = Products(name=name, price=price)
    try:
        db.session.add(new_product)
        db.session.commit()
        flash("New item successfully added", 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash("Item could not be added", 'danger')
    return redirect(url_for('manage_invoice_items'))

@app.route('/get_customer_details', methods=['GET'])
@login_required
def get_customer_details():
    customer_id = request.args.get('customer_id')
    customer = Customers.query.filter_by(id=int(customer_id)).first()
    if not customer:
        return {"ERROR":"FAILED"}

    return {
            "name": customer.name,
            "email": customer.email,
            "address": customer.address,
            "phone_number": customer.phone_number
            }

##
## MAIN
##

# Run the application.
if __name__ == "__main__":
    app.run()
