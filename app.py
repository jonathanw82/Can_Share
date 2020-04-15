import os
from numpy import arange
from functools import wraps
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from passlib.hash import pbkdf2_sha256
from os import path
if path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'CanShare'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = "B,t=u0W};gBf{DnBClV8/BwiW[1k~7EEzoiv(1Ng'*1k!^R,4sd\
                 |4-[:8:_t4c8"
mongo = PyMongo(app)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Log In setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_logged_in(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged-in' in session:
            return(func(*args, **kwargs))
        else:
            return render_template('beerceller.html')
    return wrapped_function


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html',
                               background='background_image_nonlogedin\
                               _landing')
    elif request.method == "POST":
        email = request.form['email']
        existing_user = mongo.db.users.find_one({'email': email})
        username = request.form['username']
        password = request.form['password']
        user_type = 'user'

        if existing_user is None:
            _hash = pbkdf2_sha256.hash(password)
            mongo.db.users.insert_one({
                'username': username,
                'email': email,
                'password': _hash,
                'type': user_type})
            return redirect(url_for('login'))
        else:
            return redirect(url_for('loginalready'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('beerceller.html')
    elif request.method == "POST":
        """ Check to see if the Email & password are correct """
        email = request.form['email']
        user = mongo.db.users.find_one({'email': email})
        if user:
            user_password = user['password']
            form_password = request.form['password']
            if pbkdf2_sha256.verify(form_password, user_password):
                session['logged-in'] = True
                session['username'] = user['username']
                session['email'] = email
                session['usertype'] = user['type']
                return redirect(url_for('homeLoggedIn'))
            else:
                return redirect(url_for('loginerror'))
        else:
            return redirect(url_for('loginerror'))


@app.route('/loginerror')
def loginerror():
    return render_template('loginerror.html',
                           background='background_image_nonlogedin_landing')


@app.route('/loginalready')
def loginalready():
    return render_template('loginalready.html',
                           background='background_image_nonlogedin_landing')


@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged-in', None)
    session.pop('email', None)
    session.pop('usertype', None)
    return redirect(url_for('home'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Page Routes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# finds the can ratings and populates them on page start
def calculate(can_id):
    findrating = mongo.db.ratings.find({'canId': str(can_id)})
    total = 0
    for res in findrating:
        total += res['rating']
    if total == 0:
        return 0
    else:
        return total


@app.route('/vote/<direction>/<element>', methods=['GET'])
def vote(direction, element):
    rating = 1 if direction == 'up' else 0
    results = mongo.db.ratings.find_one({'canId': element,
                                         'userId': session['email']})
    # if results none the user has not rated before return the direction
    if results is None:
        mongo.db.ratings.insert_one({
            'userId': session['email'],
            'canId': element,
            'rating': rating
        })
        return direction
    else:
        prev_rating = results['rating']
        if prev_rating == rating:
            mongo.db.ratings.remove({'_id': ObjectId(results['_id'])})
            return 'None'
        else:
            mongo.db.ratings.update({'_id': ObjectId(results['_id'])},
                                    {
                                    'userId': session['email'],
                                    'canId': element,
                                    'rating': rating
                                    })
            return direction


@app.route('/')
@app.route('/home')
def home():
    return render_template("beerceller.html",
                           title='Can share',
                           background='background_image_nonlogedin_landing')


@app.route('/homeLoggedIn')
@check_logged_in
def homeLoggedIn():
    if session['usertype'] == 'admin':
        # if session['usertype']: return admin panel,
        results = list(mongo.db.cansAndBottleInfo.find())
        ratings = list(mongo.db.ratings.find({'userId': session['email']}))
        for res in results:
            beer_type = mongo.db.type.find_one({'_id': ObjectId(res[
                                                'beer_type'])})
            res['beer_name'] = beer_type['type']
            res['rating'] = 'None'
            res['average'] = calculate(res['_id'])

            for r in ratings:
                if str(res['_id']) == str(r['canId']):
                    res['rating'] = r['rating']

        return render_template("beerceller_loggedin_admin.html",
                               caninfo=results,
                               username=session['username'],
                               usertype=session['usertype'],
                               background='background_image_landing',
                               title='Can Share Admin')
    else:
        results = list(mongo.db.cansAndBottleInfo.find())
        ratings = list(mongo.db.ratings.find({'userId': session['email']}))
        for res in results:
            beer_type = mongo.db.type.find_one({'_id': ObjectId(res
                                                                ['beer_type'])}
                                               )
            res['beer_name'] = beer_type['type']
            res['rating'] = 'None'
            res['average'] = calculate(res['_id'])

            for r in ratings:
                if str(res['_id']) == str(r['canId']):
                    res['rating'] = r['rating']

        return render_template("beerceller_loggedin.html",
                               caninfo=results,
                               background='background_image_landing',
                               username=session['username'],
                               title='Can Share')


@app.route('/can_info/<can_id>')
@check_logged_in
def can_info(can_id):
    results = mongo.db.cansAndBottleInfo.find_one({'_id': ObjectId(can_id)})
    _beer_type = mongo.db.type.find_one({'_id': ObjectId(results
                                                         ['beer_type'])})
    """
    average = calculate(results['_id'])for each results call the calulate function and pass in the can_id
    res['average'] = average
    """
    return render_template('caninfo.html', caninfo=results,
                           beer_type=_beer_type,
                           title='Can Info')


@app.route('/help')
def help():
    return render_template('help.html', title='Help')


@app.route('/about')
def about():
    return render_template('about.html', title='About',
                           background='background_image_about')


@app.route('/topshelf')
def topshelf():
    return render_template('topshelf.html', title='Top Shelf',
                           background='background_image_topshelf')


@app.route('/friends')
def friends():
    return render_template('friends.html', title='Friends',
                           background='background_image_friends')


# CREATE
@app.route("/add_beer", methods=["GET", "POST"])
@check_logged_in
def add_beer():
    if request.method == 'GET':
        return render_template('addnewbeer.html',
                               typesofbeer=mongo.db.type.find(),
                               abvnumber=arange(0, 200, 1),
                               price=arange(0, 200, 1),
                               background='background_image_create',
                               title='Add Beer')
    if request.method == 'POST':
        print(request.form.to_dict())
        # GET THE DATA FROM MY FORM (COMING FROM THE CLIENT)
        cans = mongo.db.cansAndBottleInfo
        form = request.form.to_dict()
        form['beer_type'] = ObjectId(form['beer_type'])
        form['creator'] = session['email']
        cans.insert_one(form)
        return redirect(url_for('homeLoggedIn'))


# UPDATE
@app.route("/edit_beer/<can_id>", methods=['GET', 'POST'])
@check_logged_in
def edit_beer(can_id):
    if request.method == 'GET':
        _the_can = mongo.db.cansAndBottleInfo.find_one({'_id':
                                                        ObjectId(can_id)})
        variety_of_beer = mongo.db.type.find()
        variety_of_beer_list = [beerlist for beerlist in variety_of_beer]
        return render_template('editbeer.html', the_can=_the_can,
                               abvnumber=arange(0, 200, 1),
                               varietyofbeer=variety_of_beer_list,
                               price=arange(0, 200, 1),
                               title='Edit Beer')
    if request.method == 'POST':
        print(request.form.to_dict())
        cans = mongo.db.cansAndBottleInfo
        cans.update({'_id': ObjectId(can_id)},
                    {
                    'name': request.form['name'],
                    'brand': request.form['brand'],
                    'beer_type': ObjectId(request.form['beer_type']),
                    'abv': request.form['abv'],
                    'vegan': request.form.get('vegan', 'off'),
                    'hop_type': request.form['hop_type'],
                    'malts': request.form['malts'],
                    'average_price': request.form['average_price'],
                    'where_bought': request.form['where_bought'],
                    'image_url': request.form['image_url'],
                    'review': request.form['review'],
                    })
        return redirect(url_for('homeLoggedIn'))


@app.route('/delete_can/<can_id>')
def delete_can(can_id):
    mongo.db.cansAndBottleInfo.remove({'_id': ObjectId(can_id)})
    return redirect(url_for('homeLoggedIn'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
