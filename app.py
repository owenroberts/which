import os, re, datetime

from flask import Flask, request, render_template, redirect, abort # Retrieve Flask, our framework
from flask import render_template
from flask import session, url_for, escape

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


@app.route('/buildimages', methods=['GET'])
def buildimages():
	
	imgbutt = models.Image()
	imgbutt.src = 'static/img/butt1.png'
	imgbutt.isbutt = True
	imgbutt.save()
	
	imgnot = models.Image()
	imgnot.src = 'static/img/notbutt1.png'
	imgnot.isbutt = False
	imgnot.save()
	
	return "created"

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		session['username'] = request.form['username']
		session['score'] = 0 # query all votes for username - len(query)
		# session['score'] = models.Vote.objects(username=session['username']).count()
		
		return redirect(url_for('index'))
	return '''
		<form action="" method="POST">
			<p><input type="text" name=username>
			<p><input type=submit value=Login>
		</form>
	'''

@app.route('/logout')
def logout():
	# remove the username from the session if it's there
	session.pop('username', None)
	return redirect(url_for('index'))


# accepting a vote with an image ID
# record the vote for isbutt
@app.route('/vote/<imgid>')
def vote(imgid):
	
	# get the voted image
	img = models.Image.objects.get(id=imgid)
	if img and 'username' in session:
		if img.isbutt == True:
			session['score'] = session['score'] + 1
		else:
			session['score'] = session['score'] - 1
		
		
		user, wasCreated = models.User.objects.get_or_create(name=session['username'])
		user.score = session['score']
		user.save()
		
		#app.logger.info(user)
		return redirect('/') 
		
	else:
		# img not found
		return redirect('/')
	


@app.route('/', methods=['GET', 'POST'])
def index():
	
	if 'username' in session:
		user = session['username']
	else:
		user = None
		
#		return 'Logged in as %s' % escape(session['username'])
#	return 'You are not logged in'
	
	images = models.Image.objects()
	users = models.User.objects().order_by('-score', )
	# app.logger.info(images)
	
	if 	'score' not in session:
		score = session['score']
	
	templeData = {
		'images' : images,
		'user'	: user,
		'users' : users,
		'score' : session['score']
	}

	app.logger.info(user)

	return render_template("main.html", **templeData)



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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# start the webserver
if __name__ == "__main__":
	app.debug = True
	app.secret_key = os.environ.get('SECRET_KEY')
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	