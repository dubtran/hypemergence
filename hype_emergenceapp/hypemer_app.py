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


'''
Module used to convert data points into a readable format for Rickshaw ajax graph
@param: jsn: json file 
@return: list of dictionaries of x, y values for Rickshaw 
'''
def change_json(jsn):
	data = []
	
	for key, val in jsn.iteritems():
		if key != None and val != None:
			data.append({'x': int(key)/1000, 'y' : val})

	data = sorted(data, key=lambda x: x['x'])

	return data

'''
Used for hover events. Pulls data from database to then convert and return as a json doc for Rickshaw ajax graph
@param: artist: artist name to filter out data
@return: rendered json 
'''
@app.route('/<artist>')
def get_json(artist):

	print "Getting JSON for: " + str(artist)

	ytfans = pd.read_sql('ytfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	ytplays = pd.read_sql('ytfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	ytlike = pd.read_sql('ytlikes_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	scplays = pd.read_sql('scplays_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	scfans = pd.read_sql('scfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	
	ytout = []
	scout = []
	if artist in ytfans.columns:
		ytply = ytplays.add(ytfans, fill_value=0)
		yt_j = json.loads(ytply.add(ytlike, fill_value=0).to_json())
		ytout = change_json(yt_j[artist])

	if artist in scplays.columns:
		sc_j = json.loads(scplays.add(scfans, fill_value=0).to_json())
		scout = change_json(sc_j[artist])
		
	twfans = pd.read_sql('twfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	twlists = pd.read_sql('twlists_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	twmentions = pd.read_sql('twmentions_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	twretweets = pd.read_sql('twretweets_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	twfriends = pd.read_sql('twfriends_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	
	fbpage = pd.read_sql('fbpage-story-adds-unique_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)
	fbfans = pd.read_sql('fbfans_ts', engine).set_index('date').replace([np.inf, -np.inf], np.nan).fillna(0)

	twout = []
	fbout = []
	if artist in twfans.columns:
		tw = twfans.add(twlists, fill_value=0)
		tw = tw.add(twmentions, fill_value=0)
		tw = tw.add(twretweets, fill_value=0)
		tw_j = json.loads(tw.add(twfriends, fill_value=0).to_json())
		twout = change_json(tw_j[artist])

	if artist in fbfans.columns:
		fb_j = json.loads(fbpage.add(fbfans, fill_value=0).to_json())
		fbout = change_json(fb_j[artist])

	jsn = json.dumps([{ 'data': ytout, 'name': 'youtube'}, {'data': scout, 'name':'soundcloud'}, { 'data': twout, 'name': 'twitter'}, {'data': fbout, 'name':'facebook'}])

	return Response(jsn , mimetype='application/json')

if __name__ == '__main__':
	engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')
	print "connected to engine" 
	#conn = psyco.connect(dbname = 'hypemerdb')
	app.run(host = '0.0.0.0', debug = True)
	
