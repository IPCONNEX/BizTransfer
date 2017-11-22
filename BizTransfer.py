#! Python
#  BizTransfer Web Application for Business exchanges

from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from random import randint
#  from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, validators
from functools import wraps
from passlib.hash import sha256_crypt
from lib.AppDB import AppDB
import time
import json


DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()
#  TODO load all languages initially, send the right language based on the session
#  TODO change the language to en <> english to be pushed in pages
#  TODO can be used to show dates flask_moment
#  STATICS = DB.GetLanguageStatics('en')

# THE APP

app = Flask(__name__)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        #  TODO include the cookies checking, if present and session is saved, load session variables
        origine_url = request.environ['werkzeug.request'].path
        session['origin_url'] = origine_url
        if session.get('logged'):
            return f(*args, **kwargs)
        else:
            flash("You are not authorized, Please login", 'error')
            return redirect(url_for('login'))
    return wrap


def defineLanguage(private_request):
    language = private_request.environ.get('werkzeug.request').accept_languages[0][0][:2]
    return DB.GetLanguageStatics(language)


@app.route("/lang/<string:lang>/", methods=['GET'])
def language(lang):
    if lang[:2] == 'fr':
        session['statics'] = DB.GetLanguageStatics('fr')
    elif lang[:2] == 'en':
        session['statics'] = DB.GetLanguageStatics('en')
    return redirect(url_for('dashboard'))


@app.route("/", methods=["GET"])
def index():
    defineLanguage(request)
    return render_template('index.html')


@app.route("/listings/", methods=["GET"])
def listings():
    return render_template('listings.html', enterprisesDB=enterprisesDB.find({'valide':True}))


@app.route("/ent/<string:id>/", methods=["GET"])
@is_logged_in
def ent(id):
    profile = enterprisesDB.find_one({"id":id})
    enterprisesDB.update_one({'id':id}, {'$inc':{'visits': 1}})
    #  TODO include flask_moment to track the time when the post created and updated from Flask Web Dev ch3 UTC based
    return render_template('profile.html', profile=profile)


@app.route("/newpost/", methods=["GET", "POST"])
#  TODO inspect the option for url_for(newpost, id=, page= ...) /newpost/3424?page=2...
#  TODO test the WTform with Semantic UI
#  TODO store element of enterprisePost per page on the session
#  TODO use session.get('key') to avoid raising an exception !!!
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
            return render_template('newpost.html', newId=newId)
        enterprisesDB.insert({'id':newId, 'entr_name': request.form['business_name'], 'neq': request.form['neq'],
                                'contact': request.form['contact_name'], 'email': request.form['contact_email'],
                              'phone': request.form['contact_phone'],'ask_price': request.form['ask_price'],
                              'valide': False, 'created':time.time(), 'owner':session['email']})
        flash("You successfully entered your enterprise", "success")
        return redirect(url_for('index', id=newId))

    return render_template('newpost.html', newId=newId)


@app.route("/dashboard/", methods=['GET'])
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route("/login/", methods=['POST', 'GET'])
def login():
    #  TODO  find language using: request.environ
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if usersDB.find_one({'email': email}):
            hashPass = usersDB.find_one({'email': email})['password']
            if sha256_crypt.verify(password, hashPass):
                session['logged'] = True
                session['username'] = usersDB.find_one({'email': email})['name']
                session['email'] = email
                flash("Login successful", "success")
                try:
                    origin_url = session['origin_url']
                    del session['origin_url']
                    return redirect(origin_url)
                except:
                    return redirect(url_for('dashboard'))
        else:
            flash("Wrong combination username/password", "error")

    return render_template('login.html')


@app.route("/signup/", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if usersDB.find({'email': request.form['email']}).count() > 0:
            flash("Email already used by another account", "error")
            return render_template('signup.html')

        hashPassword = sha256_crypt.encrypt(request.form['password']).encode()
        usersDB.insert({'name': request.form['name'], 'email': request.form['email'], 'phone': request.form['phone'],
                        'password': hashPassword})
        flash("Your account has been created successfully", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/signout/", methods=['GET'])
def logout():
    session['logged'] = False
    flash('Successfully logged out of your session', "info")
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    #  TODO setup an personalized page for 404 error return page+message error
    return "<h1 style='text-align: center'>PAGE NOT FOUND</h1>"


@app.errorhandler(500)
def page_not_found(e):
    #  TODO setup an personalized page for 500 error
    return "<h1 style='text-align: center'>APPLICATION ERROR</h1>"


#  TODO attach the key and the BD key into a local environment file instead of hardcoded
app.secret_key = "secr3tkey"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
