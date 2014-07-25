from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
from sqlalchemy import create_engine
import psycopg2 as psyco
import pandas as pd

app = Flask(__name__)

@app.route('/')
def start_page():
	
	blogd = pd.read_sql('hypemer_trunk', engine)
	sortd_blogd = blogd.sort(['probas'], ascending = [0])
	sortd_blogd = sortd_blogd.set_index('index')
	print "Got artists..."
	return render_template('start.html', blogd = sortd_blogd)

	

if __name__ == '__main__':
	engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')
	print "connected to engine" 
	#conn = psyco.connect(dbname = 'hypemerdb')
	app.run(host = '0.0.0.0', debug = True)
	
