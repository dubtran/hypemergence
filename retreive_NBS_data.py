from NBSAPIPythonmaster import nbs_api as nbs
import json
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import numpy as np
import psycopg2 as psyco

nbsAPI = nbs.API('winifredtran')

def get_json(artists):
    m_artists = dict()
    
    for a in artists:
        #Check clause just incase artist does not exist. 
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

def unpack_json(artists):

    dict_types = dict()
    #unpacking values within artist's indivdual JSON
    for x in temp_json:
        try:
            metric_type = x['Service']['name']
            new_dict = dict()
            if '.' in metric_type:
                metric_type = metric_type.strip('.')
            else:
                metric_type = metric_type
            for key in x['Metric']:
            	####CHECK IF THIS IS RIGHT 
                if type(x['Metric'][key]) == dict(): 
                    days_values = []
                    for day, value in x['Metric'][key].iteritems():
                        c_key = np.int16(day).astype('datetime64[D]')
                        days_values.append((str(c_key),value))
                    new_dict[key] = days_values   
                else:
                	new_dict[key] = x['Metric'][key]
            dict_types[metric_type] = new_dict
            ## add the remaining elements of the json - need the keys
            dict_types[metric_type].update(x[''])

        except Exception , e:
            print 'Error: ', e[0]
            print 'bad ... ', x
    #checking string value for . - Mongo doesn't like it
    if '.' in a:
        a = a.strip('.')

    m_artists[a] = dict_types 
        
    return m_artists

def storingMongo(to_store):
    db = client.NBS
    collection = db.metrics
    #here must edit the original name to not include . 
    tempdict = dict()
    for key, val in to_store.iteritems():
        if '.' in key.encode('ascii', errors = 'ignore'):
            newkey = key.encode('ascii', errors = 'ignore').replace('.', ' ')
            tempdict[newkey] = val
        else:
            tempdict[key] = val
    collection.insert(tempdict)
    return 'success'


if __name__ == '__main__':
	artists = 

    client = MongoClient()
	main_json = get_json(artists)