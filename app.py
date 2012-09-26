import os, datetime

from flask import Flask, request # Retrieve Flask, our framework
from flask import render_template

app = Flask(__name__)   # create our flask app



@app.route('/')
def index():
    message = 'Which one is a butt?'
    img1 = "static/img/butt1.png"
    img2 = "static/img/notbutt1.png"
    return render_template('index.html', message=message, img1=img1, img2=img2)



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



	