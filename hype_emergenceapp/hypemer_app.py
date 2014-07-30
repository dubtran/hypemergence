from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
     render_template, flash
import requests
from sqlalchemy import create_engine
import psycopg2 as psyco
import pandas as pd
import json
import numpy as np

app = Flask(__name__)

@app.route('/')
def start_page():
	
	blogd = pd.read_sql('hypemer_trunk', engine)
	sortd_blogd = blogd.sort(['probas'], ascending = [0])
	sortd_blogd = sortd_blogd.set_index('index')
	print "Got artists..."
	return render_template('start.html', blogd = sortd_blogd)

def change_json(jsn):
	data = []
	
	for key, val in jsn.iteritems():
		if key != None and val != None:
			data.append({'x': int(key)/1000, 'y' : val})

	data = sorted(data, key=lambda x: x['x'])

	return data

@app.route('/<artist>')
def get_json(artist):

	print "Getting JSON for: " + str(artist)

	ytply = pd.read_sql('ytplays_ts', engine).sort('date').set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	ytlike = pd.read_sql('ytlikes_ts', engine).sort('date').set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	ytfans = pd.read_sql('ytfans_ts', engine).sort('date').set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	ytply = ytply.add(ytfans, fill_value=0)
	yt_j = json.loads(ytply.add(ytlike, fill_value=0).to_json())
	# yt_j = json.loads(pd.read_sql('ytfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0).to_json())
	ytout = change_json(yt_j[artist])

	scplays_j = json.loads(pd.read_sql('scplays_ts', engine).set_index('date')replace([np.inf, -np.inf], np.nan).fillna(0).to_json())
	scout = change_json(scplays_j[artist])

	return Response(json.dumps([{ 'data': ytout, 'name': 'youtube'}, {'data': scout, 'name':'soundcloud'}]),  mimetype='application/json')

if __name__ == '__main__':
	engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')
	print "connected to engine" 
	#conn = psyco.connect(dbname = 'hypemerdb')
	app.run(host = '0.0.0.0', debug = True)
	
