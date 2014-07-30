import json
from NBSAPIPythonmaster import nbs_api as nbs
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine

nbsAPI = nbs.API('winifredtran') 
engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')

'''
Retrieves Next Big Sound data - artists without data will return a TypeError that is caught
@params: artists: list of artists to retrieve data from 
@return: json of data
'''
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
            except TypeError, e :
                print 'error for ', a, ' ', e[0]
                pass

        key = search_json.keys()[artist_ix]
        temp = nbsAPI.metricsArtist(key, opt = ['2010-01-01','2014-07-12', 'all' ])
        temp_json = json.loads(temp)
        dump_artist[a] = temp_json
    
    return dump_artist

'''
Converts NBS JSON unix date times to readable datetime 
@params: dump: json 
@return: json 
'''
def convert_json(dump):
    converted_nbs = dict()
    
    for a in dump.keys():
        dict_types = dict()

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

'''
Here we go into the NBS json dump to retrieve the time series for various platforms, ie soundcloud, facebook
@param: d_arts: dictionary of values, media: which media we would like to filter out
@return : dictionary of the filtered data
'''
def filtering_data(d_arts, media): 
    art_sc = dict()
    for x in d_arts.keys():
        try:
            if media in d_arts[x].keys():
                 art_sc[x] = d_arts[x][media]
        except Exception, e:
            print e[0]
    return art_sc

'''
finding the log of the absolute value of the difference in plays per day 
@params: dict of artists and their timeseries
@return: dataframe of transformed values
'''
def getMovement(artists, media):
    entire_df = pd.DataFrame()
    for a, val in artists.iteritems():
        temp = pd.DataFrame(val)
        temp = temp.set_index('date')
        temp[media] = np.log(abs(temp[media].diff(1)))
        entire_df = pd.concat([entire_df, temp], axis = 1)
        entire_df = entire_df.rename(columns = {media: a.replace(' ', '_')})
    return entire_df

'''
helper method for creating dataframes
@params: metric: the type of metric from the social media platform, m_name: the name of the metric
@return: dataframe 
'''
def df_helper(metric, m_name):
    
    play_df = pd.DataFrame.from_dict(metric)
    play_df.columns = ['date', m_name]
    play_df['date'] = pd.to_datetime(play_df['date'])
    play_df = play_df.sort('date').reset_index()
    play_df.pop('index')
    
    return play_df

'''
Creating a dataframe of the values over time for each of the metrics within a social media platform 
@params: artists: dict of artists and their values for a particular social media platform, 
metric_types: list of metric types for that social media platform 
@return: dataframe 
'''
def creating_dfs(artists, metric_types):

    artists_ts = defaultdict(dict)

    for a in artists: 
        artist = a.encode('ascii', errors = 'ignore').rstrip()
        for metric in metric_types:
            try:
                if artists[a][metric] :
                    artists_ts[metric][artist] = df_helper(artists[a][metric], metric)
            except Exception, e:
                print e[0], a 
    return artists_ts

'''
With help of helper functions, we create a complete featurized dataframe with artists and their 
feature values of their linear regression parameters: coefs and intercepts. Before getting the linear
regression values, we store the movement for webapp's rickshaw graph. 
@params: filtered: our filtered timeseries data for a particular social media platform and its' metrics
media: name of social media platform for column labels
media_metric: metric types for further filtering and column label 
@return: completed dataframe of features for a social media platform 
'''
def create_ts_features(filtered, media, media_metric):

    ts = creating_dfs(filtered, media_metric)
        
    main = pd.DataFrame()

    for x in ts:
        temp = getMovement(ts[x], x)
        print "timeseries keys:  "
        print ts[x].keys()
        #to store data for json calls later
        temp.to_sql((media + x + '_ts'), engine, if_exists = 'replace')

        maint = getLinear_feats(temp, x, media)
        main = pd.concat([main, maint], axis = 1)
    
    return main

'''
Here we create the params from the linear regression of each time series. 
The coefs give us the general overall volaititlty over the 90 days, as the intercept gives us the mean log(abs(dif))
@param: df: filtered movements, metric: the social media metric, media: the social media platform 
@return: dataframe of the artist and their linear regression results - coefficent and intercept
'''
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
