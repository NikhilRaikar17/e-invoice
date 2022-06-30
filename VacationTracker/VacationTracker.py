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
class User(UserMixin):
    def __init__(self, dn, username, data):
        self.dn = dn
        self.username = username
        self.data = data

    def __repr__(self):
        return self.dn
    
    def get_id(self):
        return self.dn
    
    def get_mail(self):
        #return self.data['mail'][0] if 'mail' in self.data else None
        return "pvtest@gmail.com"
    
    def get_name(self):
        #return self.data['cn'][0] if 'cn' in self.data else self.username
        return "pvtest"

    def is_admin(self):
        return "pvtest"

# Declare the user loader callback for flask_login. Returns the user data for 
# the given user_id. Returns None if no user with this user_id is logged in.
@login_manager.user_loader
def load_user(user_id):
    if user_id in current_users:
        return current_users[user_id]
    return None

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
    form = LDAPLoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form = form)

# Logout the current user.
@app.route('/logout')

def logout():
    logout_user()
    return redirect(url_for('login'))

# Show the vacation dates of the current user.
@app.route('/vacation/<scope>')

def vacation(scope):
    if scope == 'all':
        vacations = Vacation.query;
    else:
        vacations = Vacation.query.filter_by(Mail = "pvtest@gmail.com")
    vacations = vacations.order_by(desc('StartDate'))
    return render_template("vacation.html", vacations = vacations, scope = scope)


# Add a new vacation date to the vacation database. The vacation start and
# end dates are given.
@app.route('/vacation_add/<scope>', methods = ['POST'])

def vacation_add(scope):
    startdate = datetime.strptime(request.form['add-start-date'], "%Y-%m-%d").date()
    enddate = datetime.strptime(request.form['add-end-date'], "%Y-%m-%d").date()
    if scope == 'all' and current_user.is_admin():
        email = request.form['add-email']
        if not ldap_manager.get_object(ldap_manager.full_user_search_dn, '(mail=' + email + ')', None):
            flash('Unknown email address.')
            # print('Unknown email address')
            return redirect(url_for('vacation', scope = scope))
    else:
        email = current_user.get_mail()
    vacation = Vacation(Mail = email, StartDate = startdate, EndDate = enddate)
    db.session.add(vacation)
    db.session.commit()
    return redirect(url_for('vacation', scope = scope))

# Update a vacation date. The vacation database entry id and the new vacation
# start and end dates are given. 
@app.route('/vacation_update/<scope>', methods = ['POST'])

def vacation_update(scope):
    if scope == 'all' and current_user.is_admin():
        email = request.form['edit-email']
        vacation = Vacation.query.filter_by(id = request.form['edit-vacation-id']).first()
    else:
        email = current_user.get_mail()
        vacation = Vacation.query.filter_by(id = request.form['edit-vacation-id'], Mail = email).first()
    if vacation != None:
        vacation.Mail = email
        vacation.StartDate = datetime.strptime(request.form['edit-start-date'], "%Y-%m-%d").date()
        vacation.EndDate = datetime.strptime(request.form['edit-end-date'], "%Y-%m-%d").date()
        db.session.commit()
    return redirect(url_for('vacation', scope = scope))

# Delete a vacation date. The vacation database entry id is given. 
@app.route('/vacation_delete/<scope>', methods = ['POST'])

def vacation_delete(scope):
    if scope == 'all' and current_user.is_admin():
        vacation = Vacation.query.filter_by(id = request.form['delete-vacation-id']).first()
    else:
        email = current_user.get_mail()
        vacation = Vacation.query.filter_by(id = request.form['delete-vacation-id'], Mail = email).first()
    if vacation != None:
        db.session.delete(vacation)
        db.session.commit()
    return redirect(url_for('vacation', scope = scope))

# Delete all vacation dates checked in the vacation dates table. The vacation
# database entry ids are given.
@app.route('/vacations_delete/<scope>', methods = ['POST'])

def vacations_delete(scope):
    for id in request.form['delete-vacation-ids'].split(','):
        if scope == 'all' and current_user.is_admin():
            vacation = Vacation.query.filter_by(id = id).first()
        else:
            vacation = Vacation.query.filter_by(id = id, Mail = current_user.get_mail()).first()
        if vacation != None:
            db.session.delete(vacation)
    db.session.commit()
    return redirect(url_for('vacation', scope = scope))

@app.route('/generate_invoice')

def generate_invoice():
    vacations = Vacation.query.all()
    return render_template("e-invoicegenerator.html", vacations = vacations, scope = "my")

##
## MAIN
##

# Run the application.
if __name__ == "__main__":
    app.run()
