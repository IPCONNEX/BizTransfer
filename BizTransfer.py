#! Python
#  BizTransfer Web Application for Business exchanges

from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from random import randint
from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, validators
from functools import wraps
from passlib.hash import sha256_crypt
from lib.AppDB import AppDB
import time


DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()
STATICS = DB.GetLanguageStatics('english')


class EnterpriseForm(Form):
    ent_name = StringField('', [validators.length(min=5, max= 50)])
    neq = DecimalField('NEQ')
    contact = StringField('Contact name', [validators.length(min=5, max= 50)])
    email = StringField('Email', [validators.length(min=6, max= 50)])
    phone = DecimalField('Phone')
    ebitda = DecimalField('EBITDA')


class UserForm(Form):
    username = StringField('Username')
    name = StringField('Full name')
    email = StringField('Email')
    phone = StringField('Phone')
    password = StringField('Password')


# THE APP

app = Flask(__name__)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged' in session:
            return f(*args, **kwargs)
        else:
            flash ("You are not authorized, Please login", 'error')
            return redirect(url_for('login'))
    return wrap


@app.route("/", methods=["GET"])
def index():
    enterprisesDB.find()
    #  session['lang'] = mongo.db.statics.find_one({"language": "english"})
    #  print((session['lang']))
    return render_template('index.html', enterprisesDB=enterprisesDB.find(), STATICS=STATICS)


@app.route("/listings/", methods=["GET"])
def listings():
    return render_template('listings.html', enterprisesDB=enterprisesDB.find({'valide':True}),STATICS=STATICS)


@app.route("/ent/<string:id>/", methods=["GET"])
@is_logged_in
def ent(id):
    profile = enterprisesDB.find_one({"id":id})
    enterprisesDB.update_one({'id':id}, {'$inc':{'visits': 1}})
    return render_template('profile.html', profile=profile, STATICS=STATICS)


@app.route("/newpost/", methods=["GET", "POST"])
@is_logged_in
def newpost():

    #  get a random non-existing ID for the entry
    while True:
        newId = str(randint(1, 999999)).rjust(6, '0')
        if not enterprisesDB.find({"id":newId}).count():
            break

    if request.method == 'POST':
        if enterprisesDB.find({'neq' : request.form['neq']}).count() > 0:
            flash("This company already exists", "error")
            return render_template('newpost.html', newId=newId, STATICS=STATICS)
        enterprisesDB.insert({'id':newId, 'entr_name': request.form['business_name'], 'neq': request.form['neq'],
            'contact': request.form['contact_name'], 'email': request.form['contact_email'], 'phone': request.form['contact_phone'],
            'ask_price': request.form['ask_price'], 'valide': False, 'created':time.time(), 'owner':session['email']})
        flash("You successfully entered your enterprise", "success")
        return redirect(url_for('index', id=newId))

    return render_template('newpost.html', newID=newId, STATICS=STATICS)


@app.route("/login/", methods=['POST', 'GET'])
def login():
    #TODO  find language using: request.environ
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashPass = usersDB.find_one({'email':email})['password']
        if usersDB.find_one({'email': email}):
            if sha256_crypt.verify(password, hashPass):
                session['logged'] = True
                session['username'] = usersDB.find_one({'email': email})['name']
                session['email'] = email
                flash("Login successful", "success")
                return redirect(url_for('index'))
        else:
            flash("Wrong combination username/password", "error")

    return render_template('login.html', STATICS=STATICS)


@app.route("/signup/", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if usersDB.find({'email': request.form['email']}).count() > 0:
            flash("Email already used by another account", "error")
            return render_template('signup.html', STATICS=STATICS)

        hashPassword = sha256_crypt.encrypt(request.form['password']).encode()
        usersDB.insert({'name': request.form['name'], 'email': request.form['email'], 'phone': request.form['phone'],
                        'password': hashPassword})
        flash("Your account has been created successfully", "success")
        return redirect(url_for('login'))

    return render_template('signup.html', STATICS=STATICS)


@app.route("/signout/", methods=['GET'])
def logout():
    session.clear()
    flash('Successfully logged out of your session', "info")
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.secret_key = "secr3tkey"
    app.run(debug=True)
