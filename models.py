# -*- coding: utf-8 -*-
from flask.ext.mongoengine.wtf import model_form
from wtforms.fields import * # for our custom signup form
from flask.ext.mongoengine.wtf.orm import validators
from flask.ext.mongoengine import *
import datetime

class User(mongoengine.Document):

	name = mongoengine.StringField(max_length=120, unique=True, required=True)
	password = mongoengine.StringField()
	email = mongoengine.EmailField(unique=True, verbose_name="Email Address")
	active = mongoengine.BooleanField(default=True)
	score = mongoengine.IntField(default=0)

	# Timestamp will record the date and time idea was created.
	timestamp = mongoengine.DateTimeField(default=datetime.datetime.now())

user_form = model_form(User, exclude=['password'])

# Signup Form created from user_form
class SignupForm(user_form):
	password = PasswordField('Password', validators=[validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')

# Login form will provide a Password field (WTForm form field)
class LoginForm(user_form):
	password = PasswordField('Password')

class Image(mongoengine.Document):
	
	src = mongoengine.StringField(max_length=120, required=True)
	isbutt = mongoengine.BooleanField(required=True)
	
ImageForm = model_form(Image)

"""
look at
http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask/#.UHh7zY6CJG5
http://mongoengine-odm.readthedocs.org/en/latest/apireference.html#fields
"""