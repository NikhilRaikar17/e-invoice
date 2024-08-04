from __future__ import annotations

import datetime
from os import path

from application import db
from application import login_manager
from application.models.db_models import Customers
from application.models.db_models import Products
from application.models.db_models import Users
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user


invoice = Blueprint('invoice', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@invoice.route('/')
@login_required
def index():
    return redirect(url_for('.generate_invoice'))


@invoice.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(
            invoice.root_path,
            'static',
        ),
        'images/apl.png',
        mimetype='image/x-icon',
    )


@invoice.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('username')
    password = request.form.get('password')
    print(password)
    user = Users.query.filter_by(email=email).first()
    if request.method == 'POST':
        if user:
            flash(f'Welcome {email}', 'success')
            login_user(user)
            return redirect(url_for('.index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@invoice.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


@invoice.route('/generate_invoice')
@login_required
def generate_invoice():
    customers = Customers.query.all()
    products = Products.query.all()
    date_time = datetime.datetime.today().strftime('%d-%m-%Y')
    return render_template(
        'invoice_generator.html',
        customers=customers,
        products=products,
        date_time=date_time,
    )


@invoice.route('/manage_customers', methods=['GET'])
@login_required
def manage_customers():
    customers = Customers.query.all()
    return render_template('customers.html', customers=customers)


@invoice.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('customer-name')
    address = request.form.get('customer-address')
    email = request.form.get('customer-email')
    phone_number = request.form.get('customer-phone')
    new_customer = Customers(
        name=name, address=address,
        email=email, phone_number=phone_number,
    )
    try:
        db.session.add(new_customer)
        db.session.commit()
        flash('New customer successfully added', 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash('Some customer details entered are not proper', 'danger')
    return redirect(url_for('manage_customers'))


@invoice.route('/manage_invoice_items', methods=['GET'])
@login_required
def manage_invoice_items():
    products = Products.query.all()
    return render_template('add_products_for_invoice.html', products=products)


@invoice.route('/add_product', methods=['POST'])
@login_required
def add_product():
    name = request.form.get('item-name')
    price = request.form.get('item-price')
    new_product = Products(name=name, price=price)
    try:
        db.session.add(new_product)
        db.session.commit()
        flash('New item successfully added', 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash('Item could not be added', 'danger')
    return redirect(url_for('manage_invoice_items'))


@invoice.route('/get_customer_details', methods=['GET'])
@login_required
def get_customer_details():
    customer_id = request.args.get('customer_id')
    customer = Customers.query.filter_by(id=int(customer_id)).first()
    if not customer:
        return {'ERROR': 'FAILED'}

    return {
        'name': customer.name,
        'email': customer.email,
        'address': customer.address,
        'phone_number': customer.phone_number,
    }


@invoice.route('/edit_customer', methods=['GET', 'POST'])
@login_required
def edit_customer():
    try:
        customer_id = request.form.get('edited_customer_id')
        name = request.form.get('edited_customer_name')
        address = request.form.get('edited_customer_address')
        email = request.form.get('edited_customer_email')
        phone_number = request.form.get('edited_customer_phone')

        valid_customer = Customers.query.filter_by(id=int(customer_id)).first()
        if valid_customer:
            if valid_customer.name != name:
                valid_customer.name = name

            if valid_customer.address != address:
                valid_customer.address = address

            if valid_customer.email != email:
                valid_customer.email = email

            if valid_customer.phone_number != phone_number:
                valid_customer.phone_number = phone_number

            db.session.commit()
            flash('Successfully updated the customer details', 'success')
            return redirect(url_for('.manage_customers'))
        else:
            raise Exception('Invalid customer details')
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash('Customer could not be updated, please check the form', 'danger')
        return redirect(url_for('.manage_customers'))


@invoice.route('/login_2', methods=['GET'])
@login_required
def login_2():
    return render_template('login_2.html')


@invoice.route('/get_product_details', methods=['GET'])
@login_required
def get_product_details():
    """ Get all product details using product ID"""

    product_id = request.args.get('product_id')
    product = Products.query.filter_by(id=int(product_id)).first()
    if not product:
        return {'ERROR': 'FAILED'}

    return {
        'name': product.name,
        'price': product.price,
    }


@invoice.route('/edit_product', methods=['POST'])
@login_required
def edit_product():
    try:
        product_id = request.form.get('update_product_id')
        name = request.form.get('update_item_name')
        price = request.form.get('update_item_price')

        valid_product = Products.query.filter_by(id=int(product_id)).first()
        if valid_product:
            if valid_product.name != name:
                valid_product.name = name

            if valid_product.price != price:
                valid_product.price = price

            db.session.commit()
            flash('Successfully updated the product', 'success')
            return redirect(url_for('.manage_invoice_items'))

        else:
            raise Exception('Invalid product')

    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        flash('Product could not be updated, please check the form', 'danger')
        return redirect(url_for('.manage_invoice_items'))


@invoice.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@invoice.route('/dummy_data', methods=['GET', 'POST'])
@login_required
def dummy_data():
    if request.method == 'POST':
        if 'delete_all' in request.form:
            delete_all = request.form['delete_all']
        else:
            delete_all = None

        if delete_all:
            try:
                Customers.query.delete()
                Products.query.delete()
                db.session.commit()
                flash('Deleted all data of customers and products!', 'success')
            except Exception:
                db.session.rollback()
                db.session.flush()
                flash(
                    'Could not delete data of customers and products!',
                    'danger',
                )
            return render_template('dummy_data.html')

        customer_count = int(request.form['customer_count'])
        product_count = int(request.form['product_count'])
        try:
            if customer_count:
                for count in range(0, customer_count):
                    new_customer = Customers(
                        name=f'customer_{count}',
                        email=f'customer_{count}@gmail.com',
                        address='76890,KA Germany',
                        phone_number='908728738767',
                    )
                    db.session.add(new_customer)
                db.session.commit()

            if product_count:
                for count in range(0, product_count):
                    new_products = Products(
                        name=f'product_{count}', price=count+180,
                    )
                    db.session.add(new_products)
                db.session.commit()

        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.flush()

    return render_template('dummy_data.html')

# @invoice.route('/generate_customer_invoice', methods=['GET','POST'])
# @login_required
# def generate_customer_invoice():
#     today = datetime.today().strftime("%d/%m/%Y")
#     invoice_number = 123
#     from_addr = {
#         'company_name': 'Python Tip',
#         'addr1': '12345 Sunny Road',
#         'addr2': 'Sunnyville, CA 12345'
#     }
#     to_addr = {
#         'company_name': 'Acme Corp',
#         'person_name': 'John Dilly',
#         'person_email': 'john@example.com'
#     }
#     items = [
#         {
#             'title': 'website design',
#             'charge': 300.00
#         },{
#             'title': 'Hosting (3 months)',
#             'charge': 75.00
#         },{
#             'title': 'Domain name (1 year)',
#             'charge': 10.00
#         }
#     ]
#     duedate = "August 1, 2018"
#     total = sum([i['charge'] for i in items])
#     rendered = render_template('invoice.html',
#                             date = today,
#                             from_addr = from_addr,
#                             to_addr = to_addr,
#                             items = items,
#                             total = total,
#                             invoice_number = invoice_number,
#                             duedate = duedate)
#     html = HTML(string=rendered)
#     rendered_pdf = html.write_pdf()
#     return send_file(
#             io.BytesIO(rendered_pdf),
#             attachment_filename='invoice.pdf')
