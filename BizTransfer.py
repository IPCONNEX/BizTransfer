#! Python
#  BizTransfer Web Application for Business exchanges

from flask import render_template, request, Flask, flash, redirect, url_for, session, logging, jsonify
from flask_moment import Moment
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
from flask_mail import Message, Mail
from random import randint
from functools import wraps
from passlib.hash import sha256_crypt
from lib.AppDB import AppDB
from datetime import datetime
from lib.ToolBox import int_all
import os

DB = AppDB()
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()
serializer = URLSafeTimedSerializer('Sec3ret_key!')
#  TODO load all languages initially, send the right language based on the session
#  TODO change the language to en <> english to be pushed in pages
#  TODO can be used to show dates flask_moment

# THE APP
app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])

moment = Moment(app)
mail = Mail(app)


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


def define_language(private_request):
    if session['statics']:
        return session['statics']
    else:
        language = private_request.environ.get('werkzeug.request').accept_languages[0][0][:2]
        return DB.GetLanguageStatics(language)


@app.route("/lang/<string:lang>/", methods=['GET'])
def language(lang):
    origin_url = request.environ['werkzeug.request'].referrer
    if lang[:2] == 'fr':
        session['statics'] = DB.GetLanguageStatics('fr')
    elif lang[:2] == 'en':
        session['statics'] = DB.GetLanguageStatics('en')
    if not origin_url:
        origin_url = '/'
    return redirect(origin_url)


@app.route("/", methods=["GET"])
def index():
    # print("MAIL_SERVER = " + os.environ.get('MAIL_SERVER'))
    if session.get('statics') is not None:
        session['statics'] = define_language(request)
    return render_template('index.html')


@app.route("/listings/", methods=["GET"])
def listings():
    return render_template('listings.html', enterprisesDB=enterprisesDB.find({'valid': True}))


@app.route("/ent/<string:id>/", methods=["GET"])
@is_logged_in
def ent(id):
    profile = enterprisesDB.find_one({"id": id}, {'_id': False})
    enterprisesDB.update_one({'id': id}, {'$inc': {'visits': 1}}, upsert=True)
    #  TODO include flask_moment to track the time when the post created and updated from Flask Web Dev ch3 UTC based
    return render_template('profile.html', profile=profile)


@app.route("/newpost/<string:newId>/<int:step>/", methods=["GET", "POST"])
#  TODO inspect the option for url_for(newpost, id=, page= ...) /newpost/3424?page=2...
#  TODO store element of enterprisePost per page on the session
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
                                                              'modified': datetime.utcnow(),
                                                              'visites': 0, 'reason': request.form['reason'],
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
                                                              'valid': False,
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
                                                              'valid': False,
                                                              'tax': int_all(request.form.get('tax'))}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=4))
        elif step == 4:
            enterprisesDB.update_one({'id': newId}, {"$set": {'scian1': request.form['scian1'],
                                                              'scian2': request.form['scian2'],
                                                              'fulltime': int_all(request.form['fulltime']),
                                                              'parttime': int_all(request.form['parttime']),
                                                              'sell_involve': (request.form['sell_involve']),
                                                              'patent': request.form['patent'],
                                                              'valid': False,
                                                              'market_business': request.form.get('market_business'),
                                                              'market_individuals': request.form.get('market_individuals'),
                                                              'market_online': request.form.get('market_online')}},
                                     upsert=True)
            return redirect(url_for('newpost', newId=newId, step=5))
        elif step == 5:
            enterprisesDB.update_one({'id': newId}, {"$set": {'user_agreement': request.form['user_agreement'],
                                                              'submit_date': datetime.utcnow(),
                                                              'submitted': True, 'valid': False,
                                                              'market_online': request.form.get('market_online')}},
                                     upsert=True)
            flash("You successfully sent your enterprise for review", "success")
            return redirect(url_for('dashboard'))

    if request.method == 'GET':
        return render_template('newpost.html', step=step, current_profile=current_profile)


@app.route("/dashboard/", methods=['GET'])
@is_logged_in
def dashboard():
    enterprises = enterprisesDB.find({'owner': session['email']}, {'_id': False})
    return render_template('dashboard.html', enterprises=enterprises)


@app.route("/login/", methods=['POST', 'GET'])
def login():
    #  TODO  find language using: request.environ
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if usersDB.find_one({'email': email}):
            #  TODO verify that the account is verified
            hashPass = usersDB.find_one({'email': email})['password']
            if sha256_crypt.verify(password, hashPass):
                session['logged'] = True
                session['username'] = usersDB.find_one({'email': email})['firstname']
                session['email'] = email
                #  TODO update last login data on the DB
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
        usersDB.insert({'firstname': request.form['firstname'], 'lastname': request.form['lastname'],
                        'email': request.form['email'],'phone': request.form['phone'], 'password': hashPassword})
        token = serializer.dumps(request.form['email'], salt='confirm-email')
        msg = Message('Confirm email', sender='oelmohri@gmail.com', recipients=[request.form['email']])
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = '<h3>Your confirmation link is: ' + link
        mail.send(msg)
        flash("Your account has been created, Please check your email to validate your account", "warning")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/signup/confirm_email/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='confirm-email')
        usersDB.update_one({'email': email}, {"$set": {'account.email_confirmed': True}}, upsert=True)
        #  TODO update the account creation date
        flash("Your email is successfully validated, you can login now", "success")
    except BadTimeSignature:
        flash("A wrong confirmation link has been provided, please click again on the confirmation link", "error")
    return redirect(url_for('login'))


@app.route("/signout/", methods=['GET'])
def logout():
    session['logged'] = False
    #  TODO update the last signout date
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


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001)
