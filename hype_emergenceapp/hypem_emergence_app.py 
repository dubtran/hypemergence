from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
import blogged_collection as bc

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def start_page():
	blogd = bc.hypem_emergence(1)
	sorted = blogd.features.sort(['Results'], ascending = [0])
	return render_template('start.html', blogd = sorted)

if __name__ == '__main__':
	
	
	app.run(host = '0.0.0.0', debug = True)
	