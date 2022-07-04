from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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