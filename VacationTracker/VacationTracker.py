from os import path
from datetime import datetime
from sqlalchemy import desc
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from flask_ldap3_login import LDAP3LoginManager
from flask_ldap3_login.forms import LDAPLoginForm
from flask_sqlalchemy import SQLAlchemy

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

# LDAP configuration.
app.config['LDAP_HOST'] = 'ldaps://ldap.ps-office.local:636'
app.config['LDAP_USER_DN'] = 'ou=People'
app.config['LDAP_BASE_DN'] = 'dc=ps-office,dc=com'
app.config['LDAP_USER_RDN_ATTR'] = 'uid'
app.config['LDAP_USER_LOGIN_ATTR'] = 'uid'
app.config['LDAP_SEARCH_FOR_GROUPS'] = None
app.config['LDAP_BIND_USER_DN'] = None
app.config['LDAP_BIND_USER_PASSWORD'] = None

# Database configuration.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(path.abspath(path.dirname(__file__)), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##
## DATABASE SETUP
##

# Initialize database manager.
db = SQLAlchemy(app)

# Declare vacation database table.
class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Mail = db.Column(db.Text)
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), nullable=False) 
    email = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float(100), nullable=False)
class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))
    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"), nullable=False)

class InvoiceMaps(db.Model):
    __tablename__ = 'invoicemaps'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"), nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey("products.id"), nullable=False)


    
##
## LOGIN SETUP
##

# Initialize login managers.
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
ldap_manager = LDAP3LoginManager(app)
ldap_manager.init_app(app)

# Dictionary containing the users currently logged in.
current_users = {}

# Set containing the admin users.
admin_users = {'danilo', 'holger', 'steffi', 'pvtest'}

# Declare a flask_login compatible user data holder.


# Declare the user loader callback for flask_login. Returns the user data for 
# the given user_id. Returns None if no user with this user_id is logged in.
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Declare the user saver callback for flask_ldap3_login. This method is called 
# whenever a LDAPLoginForm successfully validates. Saves the user, and returns 
# it so it can be used in the login controller.
@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn = dn, username = username, data = data)
    current_users[dn] = user
    return user

##
## ROUTES
##

# Deliver the start page of the application.
@app.route('/')
def index():
    return redirect(url_for('vacation', scope = 'my'))

# Deliver the application icon.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'images/favicon.ico', mimetype='image/x-icon')

# Authenticate the given user at the configured LDAP server and then
# login the user at this application.
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('username')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    if request.method == 'POST':
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
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
    return render_template("e-invoicegenerator.html",customers = customers)

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

    return {"name": customer.name,
            "email": customer.email,
            "address": customer.address,
            "phone_number": customer.phone_number}

##
## MAIN
##

# Run the application.
if __name__ == "__main__":
    app.run(debug=True)
