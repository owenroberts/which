import os, datetime

from flask import Flask, request, render_template, redirect, abort # Retrieve Flask, our framework
from flask import render_template

# import all of mongoengine
from mongoengine import *

# import data models
import models


app = Flask(__name__)   # create our flask app

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
connect('mydata', host=os.environ.get('MONGOLAB_URI'))
print "Connecting to MongoLabs"

answers = ['left', 'right']


@app.route('/')
def index():
    img1 = "static/img/butt1.png"
    img2 = "static/img/notbutt1.png"
    
    templateData = {
		'users' : models.User.objects(),
		'answers' : answers
	}
	
    return render_template('index.html', img1=img1, img2=img2, **templateData)

@app.route('/answer', methods=["POST"])
def answer():
	app.logger.debug('idea form response data')
	app.logger.debug(request.form)
	app.logger.debug('list of submitted categories')
	app.logger.debug(request.form.getlist('categories'))

	# get form data - create new idea
	user = models.User()
	user.name = request.form.get('user','anonymous')
	user.answer = request.form.getlist('answer')
	
	user.save()

	templateData = {
		'user' : user
	}

	# render and return the template
	return render_template('answer.html', **templateData)
	
@app.route('/users')
def users():
	templateData = {
		'users' : models.User.objects()
	}
	return render_template("users.html", **templateData)

@app.route('/right')
def right():
	message = 'great job!'
	return render_template('right.html', message=message)
	
@app.route('/wrong')
def wrong():
	message = 'you suck!'
	return render_template('wrong.html', message=message)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	