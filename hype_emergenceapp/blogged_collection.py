import requests
import bs4
from datetime import datetime
import json
import cPickle as pickle 
import pyen
import pandas as pd 
from time import sleep
import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine
import nbs_ft
                                                                                                                                                                                                                                                                                                                                                                                                                                           
eco_api = "NCBSJDMBE39OEZKBZ"
eco = pyen.Pyen(eco_api)
model_info = pickle.load(open('sweetSVM.pkl', 'rb'))
model = model_info['model']
model_params = model_info['params']

def getArtists(num):
    artists = []
    for x in xrange(num):
        r = requests.get('http://hypem.com/playlist/latest/noremix/json/%d/data.js' % x)
        data = r.json()
        for d in data.keys():
            if d != 'version': 
                if data[d]['artist'] != None:
                    artists.append(data[d]['artist'].encode('ascii', errors = 'ignore').rstrip())
    return list(set(artists))

def echo_doc_helper(artists):
	bio = []
	blog = []
	news = []
	review = []
	song = []
	video = []
	artist = []
	for a in artists:
	    
	    bio.append(a['artist']['doc_counts']['biographies'])
	    blog.append(a['artist']['doc_counts']['blogs'])
	    news.append(a['artist']['doc_counts']['news'])
	    review.append(a['artist']['doc_counts']['reviews'])
	    song.append(a['artist']['doc_counts']['songs'])
	    video.append(a['artist']['doc_counts']['video'])
	return (np.array(blog, dtype='float') / np.array(song,dtype ='float'))


def getEcho_df(artists):
    emerge_data = []
    for a in artists:
        art = a.encode('ascii', errors = 'ignore')
        
        try:
            emerge_data.append(eco.get('artist/profile', name = art, bucket = ['hotttnesss' , 'discovery', 'familiarity', 'doc_counts']))

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

    doc_param = echo_doc_helper(emerge_data)

    temp_pdf = pd.DataFrame(zip(art_p, hotness, discover, familiar, doc_param))
    temp_pdf.columns = ['artist', 'hottness', 'discovery', 'familiarity', 'blog/song']
    temp_pdf = temp_pdf.set_index('artist')

    return temp_pdf

def ts_featurize(nbs_data):

    facebook = ['fans', 'page-story-adds-unique']
    youtube = ['plays',  'fans', 'likes']
    instagram = ['friends', 'likes', 'fans', 'comments']
    lastfm = ['comments', 'fans', 'plays']
    rdio = ['collections', 'playlists', 'plays']
    soundcloud = ['comments','fans', 'plays']
    twitter = ['fans', 'friends', 'lists', 'mentions', 'retweets', 'statuses']
    youtube = ['fans', 'likes', 'plays']
    vevo = ['plays']

    fb = nbs_ft.filtering_data(nbs_data, 'Facebook')
    fbts = nbs_ft.create_ts_features(fb, 'fb', facebook)
    tartists = nbs_ft.filtering_data(nbs_data, 'Twitter')
    twit = nbs_ft.create_ts_features(tartists, 'tw', twitter)
    yartists = nbs_ft.filtering_data(nbs_data, 'YouTube')
    ytts = nbs_ft.create_ts_features(yartists, 'yt', youtube)
    ig = nbs_ft.filtering_data(nbs_data, 'Instagram')
    igts = nbs_ft.create_ts_features(ig, 'ig', instagram)
    sc = nbs_ft.filtering_data(nbs_data, 'SoundCloud')
    scts = nbs_ft.create_ts_features(sc, 'sc', soundcloud)
    lstfm = nbs_ft.filtering_data(nbs_data, 'Last.fm')
    lstfmts = nbs_ft.create_ts_features(lstfm, 'lf', lastfm)
    rdio_data = nbs_ft.filtering_data(nbs_data, 'Rdio')
    rdiots = nbs_ft.create_ts_features(rdio_data, 'rdio', rdio)
#     vevo_data= nbs_ft.filtering_data(nbs_data, 'Vevo')
#     vevots = nbs_ft.create_ts_features(vevo_data, 'v', vevo)

    main = pd.concat([fbts, twit, ytts, igts, scts, lstfmts, rdiots], axis = 1)

    return main



'''
HypeM Emergence:
Gathers the current artists blogged from HypeM, their features from echonest and NBS. 
Checks to see if the artists were mentioned in Pitchfork's rising 
With the features, it then runs the model to predict if they are emerging
'''

class hypem_emergence(object):

    def __init__(self, pages):
        
        self.pitch_df = pd.read_csv("https://www.kimonolabs.com/api/csv/e9e9pi60?apikey=b84997b282ae1ebcbaca9da9ce786cb9")
        self.artists = getArtists(pages)
        self.features = self.getFeatures()
        self.results = model.predict(self.features)
        self.probas = model.predict_proba(self.features)
        self.for_show = self.complete_it()
        self.images = self.get_images()

    def getPitchList(self):
        return [x[0][0] for x in self.pitch_df.iterrows()]

    def getFeatures(self):
        echo_df = getEcho_df(self.artists)

        nbs_dump = nbs_ft.get_NBS(self.artists)
        nbs = nbs_ft.convert_json(nbs_dump)

        ts_features = ts_featurize(nbs)

        ts_features['p_rising'] = ts_features.index.map(lambda x: int(x in self.getPitchList() ))
        whole_df = echo_df.join(ts_features, how = 'inner')
        
        whole_df = whole_df[model_info['params']].replace([np.inf, -np.inf], np.nan).fillna(0) 
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

     def get_soundcloud(self):
        urls = []
        for a in self.features.index:
            traks = sc.get('/tracks', q=a)
            if traks[0].uri:
                urls.append(traks[0].uri)
            else:
                urls.append('no sc')
        return urls

    def complete_it(self):
        completed = self.features
        completed['Results'] = self.results
        completed['probas'] =  [x[1] for x in self.probas]
        completed['img'] = self.get_images()
        completed['soundcloud'] = self.get_soundcloud()
        return completed


