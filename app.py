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

""" app.config instucts the app on where to find the Database
    and what its called.
"""
app.config["MONGO_DBNAME"] = 'CanShare'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = "B,t=u0W};gBf{DnBClV8/BwiW[1k~7EEzoiv(1Ng'*1k!^R,4sd\
                 |4-[:8:_t4c8"
mongo = PyMongo(app)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Log In setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# This fuction checks if the user is logged in
def check_logged_in(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged-in' in session:
            return(func(*args, **kwargs))
        else:
            return render_template('beerceller.html')
    return wrapped_function


""" when the user clicks on register the fuction gives a form so the
user can signup. When the user enters there new credentials the email and user
name get put into the database, before the password is entered the pasword is
encrypted using passlib"""
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html',
                               background='background_image_nonlogedin_land',
                               title="SignUp")
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


""" This function directs the usert to a log in box interigates the
database and and sees if a user is registered and if the password
and email are correct if not a warning message is displayed. """
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('beerceller.html',
                               background='background_image_nonlogedin_land')
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


# Tells the user if there credentials are wrong.
@app.route('/loginerror')
def loginerror():
    return render_template('loginerror.html',
                           background='background_image_nonlogedin_land',
                           title='Login Error')


# Tells the user if they are already signed up.
@app.route('/loginalready')
def loginalready():
    return render_template('loginalready.html',
                           background='background_image_nonlogedin_land',
                           title='Already Signedup')


@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged-in', None)
    session.pop('email', None)
    session.pop('usertype', None)
    return redirect(url_for('home'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Page Routes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

""" finds the can ratings and populates them on page start """


def calculate(can_id):
    findrating = mongo.db.ratings.find({'canId': str(can_id)})
    total = 0
    for res in findrating:
        total += res['rating']
    if total == 0:
        return 0
    else:
        return total


""" recieves the direction and can id from javascript, searches the database if
the user has voted before, by using the session email and seeing if the userId
matches the session email, if the user has voted before and tries to vote say
Up again there vote is removed, they can then click up again if they wish or
vote down."""
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
        return {'direction': direction, 'score': calculate(element)}
    else:
        prev_rating = results['rating']
        if prev_rating == rating:
            mongo.db.ratings.remove({'_id': ObjectId(results['_id'])})
            return {'direction': 'None', 'score': calculate(element)}
        else:
            mongo.db.ratings.update({'_id': ObjectId(results['_id'])},
                                    {
                                    'userId': session['email'],
                                    'canId': element,
                                    'rating': rating
                                    })
            return {'direction': direction, 'score': calculate(element)}


@app.route('/')
@app.route('/home')
def home():
    return render_template("beerceller.html",
                           title='Can share',
                           background='background_image_nonlogedin_land')


""" if the user is an admin they can access the admin page that gives a delete
button. the function then calls for cans and bottle collections and ratings
via the can id converting them to a lists using a for loop to find the
correct beer type for the can and push it into results to be displayed on the
page """
@app.route('/homeLoggedIn')
@check_logged_in
def homeLoggedIn():
    if session['usertype'] == 'admin':
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
    return render_template('caninfo.html', caninfo=results,
                           beer_type=_beer_type,
                           title='Can Info',
                           background='background_image_info')


@app.route('/help')
def help():
    return render_template('help.html', title='Help',
                           background='background_image_help')


@app.route('/about')
def about():
    return render_template('about.html', title='About',
                           background='background_image_about')


""" if the current score is greater than the previous highest score, we delete
the previously saved higest scoring cans and add the new one, if the
scores are equal we add that can to the high scoring list aswell"""
@app.route('/topshelf')
@check_logged_in
def topshelf():
    top_results = []
    highest = 0
    all_cans = list(mongo.db.cansAndBottleInfo.find())
    for i in all_cans:
        score_result = calculate(i['_id'])
        if score_result > highest:
            top_results.clear()
            top_results.append(i)
            highest = score_result

        elif score_result == highest:
            top_results.append(i)

    return render_template('topshelf.html', title='Top Shelf',
                           background='background_image_topshelf',
                           cans=top_results, canscore=highest)


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
        # GET THE DATA FROM MY FORM (COMING FROM THE CLIENT)
        cans = mongo.db.cansAndBottleInfo
        form = request.form.to_dict()
        form['beer_type'] = ObjectId(form['beer_type'])
        form['creator'] = session['email']
        cans.insert_one(form)
        return redirect(url_for('homeLoggedIn'))


"""Update take the user info and populates the form when the user edits a
field and sends it back it updtaes all the fields. The vegan section needs
some feedback so if the form is send back with the switch off it will get a
bad key error, therfore has 'off' as the alternative."""
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
                               background='background_image_create',
                               title='Edit Beer')
    if request.method == 'POST':
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
