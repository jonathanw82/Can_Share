import os
from numpy import arange
from functools import wraps
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
#from passlib.hash import pbkdf2_sha256
from os import path
if path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'CanShare'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = "B,t=u0W};gBf{DnBClV8/BwiW[1k~7EEzoiv(1Ng'*1k!^R,4sd\
                 |4-[:8:_t4c8"
mongo = PyMongo(app)

"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Log In setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_logged_in(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged-in' in session:
            return(func(*args, **kwargs))
        else:
            return render_template('nologin.html')
    return wrapped_function


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        username = request.form['userid']
        password = request.form['password']
        user_type = request.form['type']
        _hash = pbkdf2_sha256.hash(password)
        mongo.db.users.insert_one({
            'username': username,
            'password': _hash,
            'type': user_type
        })
        return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['userid']
        user = mongo.db.users.find_one({'username': username})
        user_password = user['password']
        form_password = request.form['password']
        if pbkdf2_sha256.verify(form_password, user_password):
            session['logged-in'] = True
            session['user-id'] = username
            session['usertype'] = user['type']
        else:
            return "login error"
        return render_template('login.html')


@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged-in', None)
    session.pop('user-id', None)
    session.pop('usertype', None)
    return redirect(url_for('home'))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Page Routes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


@app.route('/')
@app.route('/home')
def home():
    return render_template("beerceller_loggedin.html",
                           caninfo=mongo.db.cansAndBottleInfo.find())


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/topshelf')
def topshelf():
    return render_template('topshelf.html')


@app.route('/friends')
def friends():
    return render_template('friends.html')


# CREATE
@app.route("/add_beer", methods=["GET", "POST"])
def add_beer():
    if request.method == 'GET':
        return render_template('addnewbeer.html',
                               typesofbeer=mongo.db.type.find(),
                               abvnumber=arange(0, 20, 0.1))
    if request.method == 'POST':
        # GET THE DATA FROM MY FORM (COMING FROM THE CLIENT)
        cans = mongo.db.cansAndBottleInfo
        cans.insert_one(request.form.to_dict())
        return redirect(url_for('home'))


# UPDATE
@app.route("/edit_beer/<can_id>")
def edit_beer(can_id):
    _the_can = mongo.db.cansAndBottleinfo.find_one({'_id': ObjectId(can_id)})
    typesof_beer = mongo.db.type.find()
    typesof_beer_list = [typesBeer for typesBeer in typesof_beer]
    return render_template('editbeer.html', the_can=_the_can, types_of_beer=typesof_beer_list,
                           abvnumber=arange(0, 20, 0.1))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
