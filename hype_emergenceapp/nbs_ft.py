import json
from NBSAPIPythonmaster import nbs_api as nbs
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

nbsAPI = nbs.API('winifredtran') 

def get_NBS(artists):
    
    dump_artist = dict()
    
    for a in artists:
        artist = a.encode('ascii', errors='ignore').rstrip()
        search = nbsAPI.artistSearch(artist)
        search_json = json.loads(search)

        #finding the exact match if not, default to first search
        artist_ix = 0
        for i, x in enumerate(search_json.values()):
            try:
                if x['name'].encode('ascii', errors='ignore') == artist: 
                    artist_ix = i 
            #Error caused by ill formated names 
            except Exception,e :
                print 'error for ', a, ' ', e[0]
                pass

        key = search_json.keys()[artist_ix]
        temp = nbsAPI.metricsArtist(key, opt=['2010-01-01','2014-07-12', 'all' ])
        temp_json = json.loads(temp)
        dump_artist[a] = temp_json
    
    return dump_artist

def convert_json(dump):
    converted_nbs = dict()
    
    for a in dump.keys():
        dict_types = dict()

        #unpacking values within artist's indivdual JSON
        for x in dump[a]:
            if type(x) == dict:
                metric_type = x['Service']['name'].encode('ascii', errors = 'ignore')
                new_dict = dict()

                if x != None:
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
                # except Exception, e:
                #     print x['Metric']
                #     print 'error ' , e[0]
        converted_nbs[a.encode('ascii', errors = 'ignore')] = dict_types 
    return converted_nbs

def filtering_data(d_arts, media): 
    art_sc = dict()
    for x in d_arts.keys():
        try:
            if media in d_arts[x]:
                 art_sc[x] = d_arts[x][media]
        except Exception, e:
            print "new error", e[0]
    return art_sc

def getMovement(artists, media):
    entire_df = pd.DataFrame()
    for a, val in artists.iteritems():
        temp = pd.DataFrame(val)
        temp = temp.set_index('date')
        temp[media] = np.log(abs(temp[media].diff(1)))
        entire_df = pd.concat([entire_df, temp], axis=1)
        entire_df = entire_df.rename(columns={media: a})
    return entire_df

def df_helper(metric, m_name):
    
    play_df = pd.DataFrame.from_dict(metric)
    play_df.columns = ['date', m_name]
    play_df['date'] = pd.to_datetime(play_df['date'])
    play_df = play_df.sort('date').reset_index()
    play_df.pop('index')
    
    return play_df

def creating_dfs(artists, metric_types):

    artists_ts = defaultdict(dict)

    for a in artists: 
        artist = a.encode('ascii', errors='ignore').rstrip()
        for metric in metric_types:
            if artists[a][metric] :
                artists_ts[metric][artist] = df_helper(artists[a][metric], metric)
    return artists_ts


def create_ts_features(filtered, media, media_metric):
    
    # if media == 'fb':
    #     ts = creating_fbdfs(filtered, media_metric)
    # else:
    ts = creating_dfs(filtered, media_metric)
        
    main = pd.DataFrame()
    for x in ts:
        temp = getMovement(ts[x], x)
        maint = getLinear_feats(temp, x, media)
        main = pd.concat([main, maint], axis=1)
    
    return main

def getLinear_feats(df, metric, media):
    linear_results = dict()
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    for index, vals in df.T.iterrows():
        model = LinearRegression()
        model = model.fit(np.arange(len(vals.values))[:,np.newaxis], vals.values)
        linear_results[index] = (model.coef_[0], model.intercept_)
    linear_df = pd.DataFrame.from_dict(linear_results).T
    linear_df.columns = [(media+metric+'_c'), (media+metric)]
    return linear_df