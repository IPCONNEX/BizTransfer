#! Python
#  BizTransfer Web Application for Business exchanges

from config import config
from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from flask_moment import Moment
from flask_mail import Mail
from random import randint
from functools import wraps
from passlib.hash import sha256_crypt
#  from lib.AppDB import
from datetime import datetime
from lib.ToolBox import int_all
import json

from app.models import AppDB
import os
from app import create_app
#  from app.models
#  from flask_migrate import Migrate


DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#  migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(usersDB=usersDB, enterprisesDB=enterprisesDB)

"""
DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()
#  TODO load all languages initially, send the right language based on the session
#  TODO change the language to en <> english to be pushed in pages
#  TODO can be used to show dates flask_moment
#  STATICS = DB.GetLanguageStatics('en')


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
    acc_language = private_request.environ.get('werkzeug.request').accept_languages[0][0][:2]
    language(acc_language)
    return DB.GetLanguageStatics(acc_language)


@app.route("/lang/<string:lang>/", methods=['GET'])
def language(lang):
    origin_url = request.environ['werkzeug.request'].referrer
    if lang[:2] == 'fr':
        session['statics'] = DB.GetLanguageStatics('fr')
    elif lang[:2] == 'en':
        session['statics'] = DB.GetLanguageStatics('en')
    return redirect(origin_url)





@app.route("/listings/", methods=["GET"])
def listings():
    return render_template('listings.html', enterprisesDB=enterprisesDB.find({'valide': True}))


@app.route("/ent/<string:id>/", methods=["GET"])
@is_logged_in
def ent(id):
    profile = enterprisesDB.find_one({"id": id})
    enterprisesDB.update_one({'id': id}, {'$inc': {'visits': 1}})
    #  TODO include flask_moment to track the time when the post created and updated from Flask Web Dev ch3 UTC based
    return render_template('profile.html', profile=profile)


@app.route("/newpost/<string:newId>/<int:step>/", methods=["GET", "POST"])
@is_logged_in
def newpost(newId='0', step=1):
    current_profile = {}
    #  get a random non-existing ID for the entry
    if newId == '0':
        #  The case of new posting
        while True:
            newId = str(randint(1, 999999)).rjust(6, '0')
            if not enterprisesDB.find({"id": newId}).count():
                current_profile['id'] = newId
                break
    else:
        current_profile = enterprisesDB.find_one({'id': newId}, {'_id': False})
        pass

    if request.method == 'POST':
        #  if enterprisesDB.find({'neq': request.form['neq']}).count() > 0:
        #  flash("This company already exists", "error")
        #  return render_template('newpost.html', newId=newId)
        if step == 1:
            #  modify and insert new if there is no entry (upsert=True)
            enterprisesDB.update_one({'id': newId}, {"$set": {'id': newId,
                                                              'title': request.form['business_title'],
                                                              'description': request.form['description'],
                                                              'region': request.form['region'],
                                                              'ask_price': int_all(request.form['ask_price']),
                                                              'revenue': int_all(request.form['revenue']),
                                                              'valid': False,
                                                              'update_date': datetime.utcnow(),
                                                              'visits': 0, 'reason': request.form['reason'],
                                                              'owner': session['email']}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=2))
        elif step == 2:
            #  TODO correct the fields form the HTML
            enterprisesDB.update_one({'id': newId}, {"$set": {'franchise': request.form['franchise'],
                                                              'foundation_year': int_all(
                                                                  request.form['foundation_year']),
                                                              'gross_profit': int_all(request.form['gross_profit']),
                                                              'ebitda': int_all(request.form['ebitda']),
                                                              'inventory': int_all(request.form['inventory']),
                                                              'office_furniture': int_all(
                                                                  request.form['office_furniture']),
                                                              'dev_stage':request.form['dev_stage'],
                                                              'update_date': datetime.utcnow(),
                                                              'finance': request.form['finance']}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=3))
        elif step == 3:
            enterprisesDB.update_one({'id': newId}, {"$set": {'gross_revenue': int_all(request.form['gross_revenue']),
                                                              'gross_profit': int_all(request.form['gross_profit']),
                                                              'ebitda': int_all(request.form['ebitda']),
                                                              'inventory': int_all(request.form['inventory']),
                                                              'office_furniture': int_all(
                                                                  request.form['office_furniture']),
                                                              'dept': int_all(request.form['dept']),
                                                              'update_date': datetime.utcnow(),
                                                              'tax': int_all(request.form.get('tax'))}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=4))
        elif step == 4:
            enterprisesDB.update_one({'id': newId}, {"$set": {'scian1': request.form['scian1'],
                                                              'scian2': request.form['scian2'],
                                                              'fulltime': int_all(request.form['fulltime']),
                                                              'parttime': int_all(request.form['parttime']),
                                                              'sell_involve': (request.form['sell_involve']),
                                                              'patent': request.form['patent'],
                                                              'update_date': datetime.utcnow(),
                                                              'market_business': request.form.get('market_business'),
                                                              'market_individuals': request.form.get('market_individuals'),
                                                              'market_online': request.form.get('market_online')}},
                                     upsert=True)
            return redirect(url_for('newpost', newId=newId, step=5))
        elif step == 5:
            enterprisesDB.update_one({'id': newId}, {"$set": {'user_agreement': request.form['user_agreement'],
                                                              'submit_date': datetime.utcnow(),
                                                              'update_date': datetime.utcnow(),
                                                              'submitted':True,
                                                              'market_online': request.form.get('market_online')}},
                                     upsert=True)
            flash("You successfully sent your enterprise for review", "success")
            return redirect(url_for('dashboard', id=newId))

    if request.method == 'GET':
        return render_template('newpost.html', step=step, current_profile=current_profile)


@app.route("/dashboard/", methods=['GET'])
@is_logged_in
def dashboard():
    #  TODO add a button to post enterprise if empty (or not)
    enterprises = enterprisesDB.find({'owner': session['email']}, {'_id': False})
    return render_template('dashboard.html', enterprises=enterprises)


@app.route("/login/", methods=['POST', 'GET'])
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
                    return redirect(url_for('dashboard'))
        else:
            flash("Wrong combination username/password", "error")

    return render_template('login.html')


@app.route("/signup/", methods=['POST', 'GET'])
#  TODO send confirmation email after signup
def signup():
    if request.method == 'POST':
        if usersDB.find({'email': request.form['email']}).count() > 0:
            flash("Email already used by another account", "error")
            return render_template('signup.html')

        hashPassword = sha256_crypt.encrypt(request.form['password']).encode()
        usersDB.insert({'firstname': request.form['firstname'], 'lastname': request.form['lastname'],
                        'email': request.form['email'], 'phone': request.form['phone'], 'password': hashPassword,
                        'account.created': datetime.utcnow()})
        flash("Your account has been created successfully", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/signout/", methods=['GET'])
def logout():
    usersDB.update_one({'email': session.get('email')}, {"$set": {'account.last_logout': datetime.utcnow()}}, upsert=True)
    session['logged'] = False
    flash('Successfully logged out of your session', "info")
    return redirect(url_for('index'))





#  TODO attach the key and the BD key into a local environment file instead of hardcoded
app.secret_key = "secr3tkey"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
"""
