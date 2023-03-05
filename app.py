import flask
from flask import Flask, redirect, url_for, jsonify
from flask import request, flash
from flask import abort, render_template
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import json
# from sqlalchemy import text
import ssl
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import smtplib
import os

app = Flask(__name__)
app.secret_key = 'shhh'

with app.app_context():
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    # Instantiate the database.
    db = SQLAlchemy(app)
    
    #Sets up login manager

    login_manager = LoginManager()
    login_manager.login_view = 'logIn'
    login_manager.init_app(app)

    class Customer(db.Model):
        c_custKey         = db.Column(db.Integer, primary_key = True)
        c_custName        = db.Column(db.String, unique = False, nullable = False)
        c_custEmail       = db.Column(db.String, unique = False, nullable = True)
        c_custPhoneNumber = db.Column(db.String, unique = False, nullable = True)
        c_custComment = db.Column(db.String, unique = False, nullable = True)

        # Adds a new user to database
        def addCustomer(c_custName, c_custEmail, c_custPhoneNumber, c_custComment):
            db.session.add(Customer(c_custName = c_custName, c_custEmail = c_custEmail, c_custPhoneNumber = c_custPhoneNumber, c_custComment = c_custComment))
            db.session.commit()
        #For the login we need get_id
        def get_id(self):
           return (self.c_custKey)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))

    class Posts(db.Model):
        p_postKey = db.Column(db.Integer, primary_key = True)
        p_custName     = db.Column(db.String, unique = False, nullable = False)
        p_postEmoji     = db.Column(db.BLOB, unique = False, nullable = False)
        p_postComment   = db.Column(db.String, unique = False, nullable = False)


    db.create_all()

@app.route('/')
def home():
    return render_template('mainmenu.html')

@app.route('/', methods=['POST'])
def login_post():
    #Get login information from the form
    username = request.form.get('uname')
    password = request.form.get('password')
    
    #get user information
    user = Customer.query.filter_by(c_custUser=username).first()


    #check if user exists
    #print(user.c_custKey)
    print(user.c_custUser)
    
    if not user.c_custUser:
        flash('Please check your login details and try again.')
        return redirect(url_for('logIn'))
    if bcrypt.checkpw(password.encode('utf-8'), user.c_custPass):
        login_user(user)
        return redirect(url_for('home_menu'))
    else: 
        return "Can not log in"

@app.route('/logout')
@login_required
def logOut():
    logout_user()
    return redirect(url_for('logIn'))

@app.route('/home')
@login_required
def home_menu():
    user = Customer.query.filter_by(c_custKey=current_user.c_custKey).first()
    return render_template('home.html', person = user)


# Sign Up Method
@app.route('/signup')
def signUp():
    return render_template('signup.html')

@app.route('/signup', methods =['GET','POST'])
def signup_post():
    username = request.form['uname']
    password = request.form['upassword']
    name     = request.form['name']
    email    = request.form['uemail']

    if username and password and name and email:
        # Checks if user already exists, if so, don't allow them to register with same name
        if Customer.query.filter_by(c_custUser = username).first():
            flash('Username already being used: login or use a different name')
            return render_template('signup.html')
        
        # Checks if email in use, if so, use a different one of login
        if Customer.query.filter_by(c_custEmail = email).first():
            flash('Email already being used: login or use a different email')
            return render_template('signup.html')

    else:
        flash('Fill in the form')
        return render_template('signup.html')
    
    # Checks if all fields are filled, if so, add to database, if not, fill in form
    if username and password and name and email:
        password_hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Admin status defaults to 0
        db.session.add(Customer(c_custUser = username, c_custPass = password_hashed, c_custCity = city, c_custNation = nation, c_custEmail = email, c_custPhoneNumber = phone, c_custAdminStatus = False))
        db.session.commit()
        flash('Successfully Signed Up!')
        return redirect(url_for('home_menu'))
    else:
        flash('Fill in the form')
        return render_template('signup.html')
