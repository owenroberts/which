# -*- coding: utf-8 -*-
from mongoengine import *
from datetime import datetime

class User(Document):

	name = StringField(max_length=120, required=True)
	score = 0
	answer = ListField(StringField(required=True))

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())
