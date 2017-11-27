from datetime import datetime
from passlib.hash import sha256_crypt
from flask import render_template, session, redirect, url_for, request, flash
from . import main
from ..models import AppDB


DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()


@main.route('/', methods=['GET'])
def index():
    #  defineLanguage(request)
    return render_template('index.html')


@main.route("/dashboard/", methods=['GET'])
#@is_logged_in
def dashboard():
    #  TODO add a button to post enterprise if empty (or not)
    enterprises = enterprisesDB.find({'owner': session['email']}, {'_id': False})
    return render_template('dashboard.html', enterprises=enterprises)


@main.route("/login/", methods=['POST', 'GET'])
#  TODO link to forget my password
#  TODO add social media login/validation
def login():
    #  TODO  find language using: request.environ
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if usersDB.find_one({'email': email}):
            hashPass = usersDB.find_one({'email': email})['password']
            if sha256_crypt.verify(password, hashPass):
                usersDB.update_one({'email': email}, {"$set": {'account.last_login': datetime.utcnow()}}, upsert=True)
                session['logged'] = True
                session['username'] = usersDB.find_one({'email': email})['firstname']
                session['email'] = email
                flash("Login successful", "success")
                try:
                    origin_url = session['origin_url']
                    del session['origin_url']
                    return redirect(origin_url)
                except:
                    return redirect(url_for('.dashboard'))
        else:
            flash("Wrong combination username/password", "error")

    return render_template('login.html')