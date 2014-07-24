from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
from sqlalchemy import create_engine

app = Flask(__name__)

@app.route('/')
def start_page():
	
	blogd = pd.read_sql('select * from hypem_artists limit 15', engine)
	sortd_blogd = blogd.sort(['Results'], ascending = [0])
	
	return render_template('start.html', blogd = sortd_blogd)

	

if __name__ == '__main__':
	engine = create_engine('postgresql://postgres:@localhost:5432/hypemerdb')
	app.run()
	