#! Python
#  BizTransfer Web Application for Business exchanges

from flask import render_template, request, Flask, flash, redirect, url_for, session, logging, jsonify
from flask_moment import Moment
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
from flask_mail import Message, Mail
from random import randint
from functools import wraps
from passlib.hash import sha256_crypt
from config import AppDB
from datetime import datetime
from lib.ToolBox import int_all
import os

#  TODO load all languages initially, send the right language based on the session
#  TODO change the language to en <> english to be pushed in pages

# THE APP
app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
moment = Moment(app)
mail = Mail(app)
DB = AppDB(app.config['DB_URI'], app.config['DB_USER'], app.config['DB_PWD'])
usersDB = DB.GetUsersDB()
enterprisesDB = DB.GetEnterprisesDB()
serializer = URLSafeTimedSerializer('Sec3ret_key!')


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
    return render_template('profile.html', profile=profile)


@app.route("/newpost/<string:newId>/<int:step>/", methods=["GET", "POST"])
#  TODO inspect the option for url_for(newpost, id=, page= ...) /newpost/3424?page=2...
#  TODO review the step + the content to enter
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
        if step == 1:
            enterprisesDB.update_one({'id': newId}, {"$set":
                                                         {'id': newId,
                                                          'general.contact': request.form['contact'],
                                                          'general.person_position': request.form['person_position'],
                                                          'general.email': request.form['email'],
                                                          'general.phone': request.form['phone'],
                                                          'general.address.street': request.form['address'],
                                                          'general.address.city': request.form['city'],
                                                          'general.address.province': request.form['province'],
                                                          'general.address.postcode': request.form['postcode'],
                                                          'valid': False, 'modified': datetime.utcnow(),
                                                          'owner': session['email']}},
                                     upsert=True)
            return redirect(url_for('newpost', newId=newId, step=2))
        elif step == 2:
            enterprisesDB.update_one({'id': newId},
                                     {"$set": {'profile.title': request.form['title'],
                                               'profile.description': request.form['description'],
                                               'profile.asking_price': int_all(request.form['asking_price']),
                                               'profile.franchise': request.form['franchise'],
                                               'valid': False}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=3))
        elif step == 3:
            enterprisesDB.update_one({'id': newId},
                                     {"$set": {'financial.gross_revenue': int_all(request.form['gross_revenue']),
                                               'financial.gross_profit': int_all(request.form['gross_profit']),
                                               'financial.ebitda': int_all(request.form['ebitda']),
                                               'financial.inventory': int_all(request.form['inventory']),
                                               'financial.office_furniture': int_all(request.form['office_furniture']),
                                               'valid': False}}, upsert=True)
            return redirect(url_for('newpost', newId=newId, step=4))
        elif step == 4:
            enterprisesDB.update_one({'id': newId},
                                     {"$set": {'non_financial.foundation_year': request.form['foundation_year'],
                                               'non_financial.reason': request.form['reason'],
                                               'non_financial.target': request.form['target'],
                                               'non_financial.dev_stage': request.form['dev_stage'],
                                               'non_financial.finance': request.form['finance'],
                                               'non_financial.after_sale': request.form['after_sale'],
                                               'non_financial.patent': request.form['patent'],
                                               'non_financial.fulltime': int_all(request.form['fulltime']),
                                               'non_financial.parttime': int_all(request.form['parttime']),
                                               'non_financial.rent': request.form['rent'],
                                               'non_financial.end_date': request.form['end_date'], 'valid': False}},
                                     upsert=True)
            return redirect(url_for('newpost', newId=newId, step=5))
        elif step == 5:
            enterprisesDB.update_one({'id': newId},
                                     {"$set": {'advanced.scian1': request.form['scian1'],
                                               'advanced.scian2': request.form['scian2'],
                                               'advanced.tax': int_all(request.form['tax']),
                                               'advanced.average_revenue': int_all(request.form['average_revenue']),
                                               'advanced.average_profit': int_all(request.form['average_profit']),
                                               'advanced.average_interest': int_all(request.form['average_interest']),
                                               'advanced.average_debt': int_all(request.form['average_debt']),
                                               'advanced.cca': int_all(request.form['cca']),
                                               'advanced.ucc': int_all(request.form['ucc']),
                                               'advanced.rdtoh': int_all(request.form['rdtoh']),
                                               'advanced.de_ratio': request.form['de_ratio'], 'valid': False}},
                                     upsert=True)
            return redirect(url_for('newpost', newId=newId, step=6))
        elif step == 6:
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
        account = {}
        email = request.form['email']
        password = request.form['password']
        account = usersDB.find_one({'email': email}, {'_id': False})
        if account is not None:
            hashPass = account['password']
            if sha256_crypt.verify(password, hashPass) and account['account']['email_confirmed']:
                session['logged'] = True
                session["name"] = ' '.join([account.get('firstname'), account.get('lastname')])
                session['email'] = email
                session['phone'] = account.get('phone')
                #  TODO update last login data on the DB
                usersDB.update_one({'email': email}, {"$set": {'account.last_login': datetime.utcnow()}})
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
    usersDB.update_one({'email': session.get('email')}, {"$set": {'account.logout': datetime.utcnow()}})
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
