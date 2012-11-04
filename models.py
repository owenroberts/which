# -*- coding: utf-8 -*-
from mongoengine import *
from flask.ext.mongoengine.wtf import model_form

from datetime import datetime

class User(Document):

	name = StringField(max_length=120, required=True)
	answer = StringField(required=True)
	score = 0 #IntField default = 0
	

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())

UserForm = model_form(User)

class Image(Document):
	
	src = StringField(max_length=120, required=True)
	isbutt = BooleanField(required=True)

"""
look at
http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask/#.UHh7zY6CJG5
http://mongoengine-odm.readthedocs.org/en/latest/apireference.html#fields
"""