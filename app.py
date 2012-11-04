import os, re, datetime

from flask import Flask, request, render_template, redirect, abort # Retrieve Flask, our framework
from flask import render_template

# import all of mongoengine
from mongoengine import *

# import data models
import models


app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
connect('mydata', host=os.environ.get('MONGOLAB_URI'))
print "Connecting to MongoLabs"

answers = ['left', 'right']


@app.route('/', methods=['GET', 'POST'] )
def index():
	
	# get Answer form from models.py
	user_form = models.UserForm(request.form)
	
	# if form was submitted and it is valid...
	if request.method == "POST" and user_form.validate():
		
		# get form data - create new idea
		user = models.User()
		user.name = request.form.get('name')
		user.answer = request.form.get('answer')
		
		user.save() # save it

		# redirect to the new idea page
		return redirect('/user/%s' % user.name)
	
	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('answers'):
			for c in request.form.getlist('answers'):
				idea_form.answers.append_entry(c)

		# render the template
		
		
		templateData = {
			'users' : models.User.objects(),
			'answers' : answers,
			'form' : user_form
		}

		return render_template("main.html",img1 = "static/img/butt1.png", img2 = "static/img/notbutt1.png", **templateData)
	

@app.route('/user/<user_name>')
def user_answer(user_name):
	
	# get idea by idea_slug
	try:
		user = models.User.objects.get(name=user_name)
	except:
		abort(404)
			
	templateData = {
		'user' : user
	}
	app.logger.debug(templateData)
	
	# render and return the template
	return render_template('answer.html', **templateData)
	
@app.route('/users')
def users():
	
	users = models.User.objects().order_by('-timestamp')
	
	templateData = {
		'users' : users
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



	