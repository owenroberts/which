import os, re, datetime
import requests

from flask import Flask, request, render_template, redirect, abort # Retrieve Flask, our framework
from flask import render_template
from flask import session, url_for, escape
from flask import jsonify

# import all of mongoengine
from flask.ext.mongoengine import mongoengine

# import data models
import models


from flask.ext.login import (LoginManager, current_user, login_required, login_user, logout_user, UserMixin, AnonymousUser, confirm_login, fresh_login_required)

#Library
from flaskext.bcrypt import Bcrypt

#Custom user library - maps User object to User model
from libs.user import * 	

app = Flask(__name__)   # create our flask app
#app.config['CSRF_ENABLED'] = False
app.secret_key = os.environ.get('SECRET_KEY')

flask_bcrypt = Bcrypt(app)

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
mongoengine.connect('mydata', host=os.environ.get('MONGOLAB_URI'))
print "Connecting to MongoLabs"

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please login to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(id):
	if id is None:
		redirect('/login')
		
	user = User()
	user.get_by_id(id)
	if user.is_active():
		return user
	else:
		return None

login_manager.setup_app(app)


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
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	# prepare registration form 
	registerForm = models.SignupForm(request.form)
	app.logger.info(request.form)

	if request.method == 'POST' and registerForm.validate():
		email = request.form['email']
		username = request.form['name']

		if request.form['password'] != None:
			# generate password hash
			password_hash = flask_bcrypt.generate_password_hash(request.form['password'])

		# prepare User
		user = User(name=username, email=email, password=password_hash)

		# save new user, but there might be exceptions (uniqueness of email and/or username)
		try:
			user.save()	
			if login_user(user, remember="no"):
				flash("Logged in!")
				return redirect(request.args.get("next") or '/')
			else:
				flash("unable to log you in")

		# got an error, most likely a uniqueness error
		except mongoengine.queryset.NotUniqueError:
			e = sys.exc_info()
			exception, error, obj = e

			app.logger.error(e)
			app.logger.error(error)
			app.logger.error(type(error))

			# uniqueness error was raised. tell user (via flash messaging) which error they need to fix.
			if str(error).find("email") > -1:			
				flash("Email submitted is already registered.","register")

			elif str(error).find("username") > -1:
				flash("Username is already registered. Pick another.","register")

			app.logger.error(error)	

	# prepare registration form			
	templateData = {
		'form' : registerForm
	}

	return render_template("/auth/register.html", **templateData)

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
		app.logger.info(session)
		session['score'] = 0
		score = session['score']
	
	templeData = {
		'current_user' : current_user,
		'images' : images,
		'user'	: user,
		'users' : users,
		'score' : session['score']
	}

	app.logger.info(user)
	
	return render_template("main.html", **templeData)

@app.route('/data/users')
def data_users():
	users = models.User.objects().order_by('+timestamp').limit(10)
	
	if users:
		public_users = []
		for u in users:
			tmpUser = {
				'name' : u.name,
				'score' : u.score,
				'timestamp' : str(u.timestamp)
			}
			public_users.append( tmpUser )
			
		data = {
			'status' : 'OK',
			'users' : public_users
		}
		
		return jsonify(data)
	
	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve users'
		}
		return jsonify(error)



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
	
@app.route('/users/<username>')
def user(username):
	
	try:
		user = models.User.objects.get(username=username)
	
	except Exception:
		e = sys.exc_info()
		app.logger.error(e)
		abort(404)
	
	user_content = models.Content.objects(user=user)
	
	templateData = {
			'user' : user,
			'current_user' : current_user,
			'user_content'  : user_content,
			'users' : models.User.objects()
		}

	return render_template('user_content.html', **templateData)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/getideas')
def get_remote_ideas():
	ideas_url = "http://itp-ideas-dwd.herokuapp.com/data/ideas"
	idea_request = requests.get(ideas_url)
	app.logger.info(idea_request.json)
	ideas_data = idea_request.json
	
	if ideas_data.get('status') == "OK":
			templateData = {
				'ideas' : ideas_data.get('ideas') # get the ideas from the returned json
			}

			return render_template('remote_ideas.html', **templateData)


	else:
		return "uhoh something went wrong - status = %s" % ideas_data.get('status')


# start the webserver
if __name__ == "__main__":
	app.debug = True
	app.secret_key = os.environ.get('SECRET_KEY')
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	