from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
from sqlalchemy import create_engine
import psycopg2 as psyco

app = Flask(__name__)

@app.route('/')
def start_page():
	
	cur = conn.cursor()
	blogd = cur.execute('select * from hypemer_closet limit 15').fetchall()
	sortd_blogd = blogd.sort(['Results'], ascending = [0])
	
	return render_template('start.html', blogd = sortd_blogd)

	

if __name__ == '__main__':
	conn = psyco.connect(dbname = 'hypemerdb')
	app.run()
	