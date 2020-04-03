import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'CanShare'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)


@app.route('/')
@app.route('/home')
def home():
    return render_template("beerceller.html",
                           caninfo=mongo.db.cansAndBottleInfo.find())


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/halloffame')
def halloffame():
    return render_template('halloffame.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)