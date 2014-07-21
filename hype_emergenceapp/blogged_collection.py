import requests
import bs4
from NBSAPIPythonmaster import nbs_api as nbs
from datetime import datetime
import json
import cPickle as pickle 
import pyen
import pandas as pd 
from time import sleep
import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine

nbsAPI = nbs.API('winifredtran')
eco_api = "NCBSJDMBE39OEZKBZ"
eco = pyen.Pyen(eco_api)
engine = create_engine('postgresql://dubT:unicorn!@localhost:5432/nebulae')
model = pickle.load(open('initial_model.pkl', 'rb'))

def getArtists(num):
    artists = []
    for x in xrange(num):
        r = requests.get('http://hypem.com/playlist/latest/noremix/json/%d/data.js' % x)
        data = r.json()
        for d in data.keys():
            if d != 'version': 
                artists.append(data[d]['artist'])
    return list(set(artists))

def getEcho_df(artists):
	emerge_data = []
	for a in artists:
	    try:
	        emerge_data.append(eco.get('artist/profile', name = str(a), bucket = ['hotttnesss' , 'discovery', 'familiarity']))
	    except Exception , e: 
	        print 'cant get ', a 
	        
	discover = []
	hotness = []
	familiar = []
	art_p = []

	for x in emerge_data:
	    discover.append(x['artist']['discovery'])
	    hotness.append(x['artist']['hotttnesss'])
	    familiar.append(x['artist']['familiarity'])
	    art_p.append(x['artist']['name'].encode('ascii', errors = 'ignore'))
	temp_pdf = pd.DataFrame(zip(art_p, hotness, discover, familiar))
	temp_pdf.columns = ['artist', 'hottness', 'discovery', 'familiarity']
	temp_pdf = temp_pdf.set_index('artist')

	return temp_pdf

def get_NBS(artists):
    
    dump_artist = dict()
    
    for a in artists:
        search = nbsAPI.artistSearch(a.encode('ascii', errors='ignore'))
        search_json = json.loads(search)

        #finding the exact match if not, default to first search
        artist_ix = 0
        for i, x in enumerate(search_json.values()):
            try:
                if x['name'].encode('ascii', errors = 'ignore') == a.encode('ascii', errors = 'ignore'): 
                    artist_ix = i 
            #Error caused by ill formated names 
            except Exception,e :
                print 'error for ', a, ' ', e[0]
                pass

        key = search_json.keys()[artist_ix]
        temp = nbsAPI.metricsArtist(key, opt = ['2010-01-01','2014-07-12', 'all' ])
        temp_json = json.loads(temp)
        dump_artist[a] = temp_json
    
    return dump_artist

def convert_json(dump):
    converted_nbs = dict()
    
    for a in dump.keys():
        dict_types = dict()
        print a
        #unpacking values within artist's indivdual JSON
        for x in dump[a]:
            if type(x) == dict:
                metric_type = x['Service']['name'].encode('ascii', errors = 'ignore')
                new_dict = dict()

                try:
                    for key in x['Metric']:
                        ####CHECK IF THIS IS RIGHT 
                        if type(x['Metric'][key]) != list: 
                            days_values = []
                            for day, value in x['Metric'][key].iteritems():
                                c_key = np.int16(day).astype('datetime64[D]')
                                days_values.append((str(c_key),value))
                            new_dict[key] = days_values   
                        else:
                            new_dict[key] = x['Metric'][key]
                    dict_types[metric_type] = new_dict
                    ## add the remaining elements of the json - need the keys
                    dict_types[metric_type].update([x['Profile'], x['Service']])
                except Exception, e:
                    print x['Metric']
                    print 'error ' , e[0]
        converted_nbs[a.encode('ascii', errors = 'ignore')] = dict_types 
    return converted_nbs

def filtering_data(d_arts, media): 
    art_sc = dict()
    for x in d_arts.keys():
        try:
            if media in d_arts[x].keys():
                 art_sc[x] = d_arts[x][media]
        except Exception, e:
            print e[0]
    return art_sc

def getMovement(artists, media):
    entire_df = pd.DataFrame()
    for a, val in artists.iteritems():
        temp = pd.DataFrame(val)
        temp = temp.set_index('date')
        temp[media] = np.log(abs(temp[media].diff(1)))
        entire_df = pd.concat([entire_df, temp], axis = 1)
        entire_df = entire_df.rename(columns = {media: a})
    return entire_df

def SC_df_helper(metric, m_name):
    
    play_df = pd.DataFrame.from_dict(metric)
    play_df.columns = ['date', m_name]
    play_df['date'] = pd.to_datetime(play_df['date'])
    play_df = play_df.sort('date').reset_index()
    play_df.pop('index')
    
    return play_df

def SCcreating_dfs(art_sc):
    dfs_plays = {}
    dfs_downloads = {}
    dfs_comments = {}
    dfs_fans = {}
    dfs_soundcloud = {}
    for x in art_sc.keys():
    	play_df = pd.DataFrame()
        download_df = pd.DataFrame()
        comment_df = pd.DataFrame()
        fan_df = pd.DataFrame()
        if art_sc[x]['plays']:
            play_df = SC_df_helper(art_sc[x]['plays'], 'plays') 
            dfs_plays[ x.encode('ascii', errors = 'ignore').rstrip()] = play_df

        if art_sc[x]['downloads']: 
            download_df = SC_df_helper(art_sc[x]['downloads'], 'downloads')
            dfs_downloads[ x.encode('ascii', errors = 'ignore').rstrip()] = download_df

        if art_sc[x]['comments']:
            comment_df = SC_df_helper(art_sc[x]['comments'], 'comments')
            dfs_comments[x.encode('ascii', errors = 'ignore').rstrip()] = comment_df

        if art_sc[x]['fans']:
            fan_df = SC_df_helper(art_sc[x]['fans'], 'fans')
            dfs_fans[x.encode('ascii', errors = 'ignore').rstrip()] = fan_df

        full_df = pd.concat([play_df, download_df, comment_df, fan_df], axis = 1)
        dfs_soundcloud[x.encode('ascii', errors = 'ignore')] = full_df
    return dfs_plays, dfs_downloads, dfs_comments, dfs_fans, dfs_soundcloud

def getLinear_feats(df):
    linear_results = dict()
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    for index, vals in df.T.iterrows():
        model = LinearRegression()
        model = model.fit(np.arange(len(vals.values))[:,np.newaxis], vals.values)
        linear_results[index] = (model.coef_[0], model.intercept_)
    linear_df = pd.DataFrame.from_dict(linear_results).T
    linear_df.columns = ['lin_coeff', 'plays']
    return linear_df

'''
HypeM Emergence:
Gathers the current artists blogged from HypeM, their features from echonest and NBS. 
Checks to see if the artists were mentioned in Pitchfork's rising 
With the features, it then runs the model to predict if they are emerging
'''

class hypem_emergence(object):
	

	def __init__(self):
        
		self.pitch_df = pd.read_sql('select distinct artist from pitch_artists' , engine)
		self.artists = getArtists(4)
		self.features = self.getFeatures()
		self.results = model.predict(self.features)
		self.probas = model.predict_proba(self.features)
		self.for_show = self.complete_it()
		self.images = self.get_images()

	def getFeatures(self):
		echo_df = getEcho_df(self.artists)

		nbs_dump = get_NBS(self.artists)
		nbs = convert_json(nbs_dump)
		filtered_nbs = filtering_data(nbs, 'SoundCloud')
		dfs_plays, dfs_downloads, dfs_comments, dfs_fans, dfs_soundcloud = SCcreating_dfs(filtered_nbs)

		sc_dif_df = getMovement(dfs_plays, 'plays')
		linear_df = getLinear_feats(sc_dif_df)

		linear_df['p_rising'] = linear_df.index.map(lambda x: int(x in list(self.pitch_df['artist'])) )
		whole_df = echo_df.join(linear_df, how = 'inner')
		whole_df = whole_df[['plays', 'discovery', 'familiarity', 'hottness', 'p_rising', 'lin_coeff']]
		return whole_df 

	def get_images(self):
		images = []
		for a in self.features.index:
			temp = eco.get('artist/images', name = str(a), results = 1)

			if temp['images']:
				images.append(temp['images'][0]['url'].encode('ascii', errors ='ignore'))
			else:
				images.append('no img')
		return images

	def complete_it(self):
		completed = self.features
		completed['Results'] = self.results
		completed['img'] = self.get_images()
		return completed










